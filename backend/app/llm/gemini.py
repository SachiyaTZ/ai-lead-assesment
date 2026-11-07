from __future__ import annotations

import asyncio
import base64
import json
from typing import Any

import httpx

from app.core.config import Settings, get_settings


class GeminiError(RuntimeError):
    """Raised when Gemini cannot return a usable response."""


class GeminiClient:
    """Small async Gemini REST client.

    The assessment emphasizes async engineering and provider abstraction. Using httpx keeps
    the implementation explicit and avoids coupling the application to a synchronous SDK.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    @property
    def enabled(self) -> bool:
        return bool(self.settings.gemini_api_key.strip())

    async def generate_text(
        self,
        prompt: str,
        *,
        system_instruction: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 1400,
    ) -> str:
        if not self.enabled:
            raise GeminiError("GEMINI_API_KEY is not configured")

        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_output_tokens,
            },
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        url = f"{self.BASE_URL}/{self.settings.gemini_model_name}:generateContent"
        headers = {
            "x-goog-api-key": self.settings.gemini_api_key,
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
                    response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                text = self._extract_text(data)
                if not text:
                    raise GeminiError("Gemini returned no text content")
                return text.strip()
            except httpx.HTTPStatusError as exc:
                # Retry only transient 429/5xx failures. Validation/auth failures should fail fast.
                if exc.response.status_code not in {429, 500, 502, 503, 504}:
                    detail = exc.response.text[:500]
                    raise GeminiError(
                        f"Gemini API returned HTTP {exc.response.status_code}: {detail}"
                    ) from exc
                last_error = exc
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_error = exc

            if attempt < 2:
                await asyncio.sleep(0.5 * (2**attempt))

        raise GeminiError(f"Gemini request failed after retries: {last_error}")

    async def generate_image(self, prompt: str) -> tuple[bytes, str]:
        """Generate an image with the configured Gemini image model.

        Returns `(image_bytes, mime_type)`. It is intentionally not exposed as an agent tool
        by default; this helper makes the configured image model available for future UI/tool use.
        """
        if not self.enabled:
            raise GeminiError("GEMINI_API_KEY is not configured")

        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"]},
        }
        url = f"{self.BASE_URL}/{self.settings.gemini_image_model_name}:generateContent"
        headers = {
            "x-goog-api-key": self.settings.gemini_api_key,
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                inline = part.get("inlineData") or part.get("inline_data")
                if inline and inline.get("data"):
                    return base64.b64decode(inline["data"]), inline.get("mimeType", "image/png")
        raise GeminiError("Gemini image model returned no image")

    @staticmethod
    def _extract_text(data: dict[str, Any]) -> str:
        parts: list[str] = []
        for candidate in data.get("candidates", []):
            for part in candidate.get("content", {}).get("parts", []):
                if isinstance(part.get("text"), str):
                    parts.append(part["text"])
        return "\n".join(parts)

    async def classify_intent(self, query: str) -> str | None:
        """Optional constrained intent classification used by the supervisor.

        Only one of the known labels is accepted; otherwise the caller uses deterministic routing.
        """
        allowed = {
            "simple_knowledge_query",
            "deep_research",
            "analytical_query",
            "enterprise_tool_query",
        }
        prompt = (
            "Classify the user request into exactly one label and return JSON only.\n"
            f"Allowed labels: {sorted(allowed)}\n"
            f"User request: {json.dumps(query)}\n"
            'Return: {"intent":"<label>"}'
        )
        try:
            raw = await self.generate_text(prompt, temperature=0.0, max_output_tokens=80)
            start, end = raw.find("{"), raw.rfind("}")
            if start == -1 or end == -1:
                return None
            value = json.loads(raw[start : end + 1]).get("intent")
            return value if value in allowed else None
        except Exception:
            return None

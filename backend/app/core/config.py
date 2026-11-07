from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Enterprise AI Assistant"
    environment: str = "development"
    api_prefix: str = "/api/v1"

    # Gemini is the primary LLM provider for this POC.
    gemini_api_key: str = ""
    gemini_model_name: str = "gemini-2.5-flash"
    gemini_image_model_name: str = "gemini-2.5-flash-image"
    llm_timeout_seconds: float = 45.0

    # Retrieval / platform settings.
    embedding_model: str = "local-hash-embedding"
    pinecone_api_key: str = ""
    pinecone_index_name: str = "enterprise-ai-assistant"
    pinecone_namespace: str = "enterprise"
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "enterprise-ai-assistant"
    jwt_secret: str = "change-me-in-production"
    jwt_expire_minutes: int = 120
    hybrid_dense_weight: float = 0.65
    hybrid_sparse_weight: float = 0.35
    retrieval_top_k: int = 6
    max_recursion_depth: int = 3
    max_research_subtasks: int = 6
    max_documents_per_step: int = 8
    max_total_tokens: int = 12000
    rate_limit_capacity: int = 20
    rate_limit_refill_rate: float = 0.2
    max_message_length: int = 8000
    use_pinecone: bool = False
    data_dir: str = "data"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def weights(self) -> tuple[float, float]:
        total = self.hybrid_dense_weight + self.hybrid_sparse_weight
        if total <= 0:
            return (0.65, 0.35)
        return (
            self.hybrid_dense_weight / total,
            self.hybrid_sparse_weight / total,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()

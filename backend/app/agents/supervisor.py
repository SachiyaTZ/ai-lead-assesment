from app.llm.gemini import GeminiClient


def _deterministic_intent(query: str) -> str:
    q = query.lower()
    intent = "simple_knowledge_query"
    if any(x in q for x in ["analyze", "all ", "recurring", "root causes", "last year", "across"]):
        intent = "deep_research"
    if any(x in q for x in ["distribution", "count", "frequency", "statistics"]):
        intent = "analytical_query"
    if any(x in q for x in ["who owns", "service owner", "employee directory"]):
        intent = "enterprise_tool_query"
    return intent


async def supervisor_node(state):
    # Deterministic routing remains the safe fallback. Gemini can improve classification,
    # but is never trusted for authorization or tool permissions.
    fallback = _deterministic_intent(state["query"])
    gemini_intent = await GeminiClient().classify_intent(state["query"])
    intent = gemini_intent or fallback

    plan = {
        "simple_knowledge_query": ["retrieve evidence", "validate citations", "respond"],
        "deep_research": ["scope documents", "retrieve targeted evidence", "batch findings", "aggregate causes", "respond"],
        "analytical_query": ["retrieve incidents", "run controlled analysis", "respond"],
        "enterprise_tool_query": ["select enterprise tool", "authorize", "execute", "respond"],
    }[intent]

    source = "Gemini + deterministic fallback" if gemini_intent else "deterministic fallback"
    return {
        "intent": intent,
        "plan": plan,
        "activity": state.get("activity", [])
        + [
            {
                "type": "state",
                "node": "supervisor",
                "status": "completed",
                "message": f"Intent: {intent} ({source})",
            }
        ],
    }

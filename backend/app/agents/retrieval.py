from app.models.schemas import SearchFilters

async def retrieval_node(state, retriever):
    q = state["query"]
    memory = state.get("memory_context", {})
    # Resolve lightweight follow-up references without forwarding unbounded history.
    if any(x in q.lower() for x in ["same problem", "same issue", "again later", "that incident", "it happen again"]):
        turns = memory.get("turns", [])
        if turns:
            q = f"{turns[-1].get('user','')} {q}"
    filters = SearchFilters(top_k=8 if state.get("intent") == "deep_research" else 6)
    if "payment" in q.lower(): filters.department = "payments"
    if any(x in q.lower() for x in ["incident", "outage", "root cause"]): filters.document_type = "incident"
    docs = await retriever.search(q, filters)
    return {
        "retrieved_documents": docs,
        "citations": list(dict.fromkeys(d.document_id for d in docs)),
        "activity": state.get("activity", []) + [{"type":"retrieval","node":"retrieval","status":"completed","message":f"Retrieved {len(docs)} evidence chunks"}],
    }

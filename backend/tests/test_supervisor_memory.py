import pytest
from app.agents.supervisor import supervisor_node
from app.memory.session import SessionMemory

@pytest.mark.asyncio
async def test_supervisor_routes_deep_research():
    out = await supervisor_node({"query":"Analyze all payment outages and recurring root causes", "activity":[]})
    assert out["intent"] == "deep_research"

@pytest.mark.asyncio
async def test_memory_is_bounded():
    m = SessionMemory(max_recent=2)
    await m.add_turn("c", "q1", "a1", [])
    await m.add_turn("c", "q2", "a2", [])
    await m.add_turn("c", "q3", "a3", [])
    data = await m.get("c")
    assert [t["user"] for t in data["turns"]] == ["q2", "q3"]

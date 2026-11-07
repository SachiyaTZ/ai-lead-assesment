import pytest
from app.rag.hybrid import HybridRetriever
from app.models.schemas import RetrievedChunk,SearchFilters

def d(i,text,dept="payments",typ="incident"):
    return RetrievedChunk(chunk_id=str(i),document_id=f"D{i}",title="t",content=text,source="x",department=dept,document_type=typ,access_level="internal",created_date="2026-01-01")
@pytest.mark.asyncio
async def test_hybrid_prefers_keyword_match():
    r=HybridRetriever([d(1,"payment gateway timeout payment failure"),d(2,"office holiday policy")]); await r.prepare(); out=await r.search("payment timeout",SearchFilters(top_k=2))
    assert out[0].document_id=="D1" and out[0].hybrid_score>=out[1].hybrid_score
@pytest.mark.asyncio
async def test_metadata_filter():
    r=HybridRetriever([d(1,"x"),d(2,"x","security")]); await r.prepare(); out=await r.search("x",SearchFilters(department="security")); assert {x.document_id for x in out}=={"D2"}

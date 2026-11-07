import re
from app.models.schemas import RetrievedChunk
CIT_RE=re.compile(r"\[([A-Z][A-Z0-9_-]+)\]")

def extract_citations(text: str) -> list[str]:
    return list(dict.fromkeys(CIT_RE.findall(text)))

def validate_citations(text: str, evidence: list[RetrievedChunk]) -> tuple[bool,list[str]]:
    allowed={x.document_id for x in evidence}
    cited=extract_citations(text)
    invalid=[c for c in cited if c not in allowed]
    return (not invalid,invalid)

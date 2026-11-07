from collections import Counter,defaultdict
from app.models.schemas import AnalysisRequest
ALLOWED_FIELDS={"root_cause","severity","affected_service","department","created_date","document_type"}

def run_analysis(req:AnalysisRequest)->dict:
    records=req.records
    if req.field and req.field not in ALLOWED_FIELDS: raise ValueError("Field is not allowed")
    if req.operation in {"count_by_field","group_by","frequency"}:
        field=req.field or "root_cause"; return {"operation":req.operation,"field":field,"counts":dict(Counter(str(r.get(field,"unknown")) for r in records))}
    if req.operation=="severity_summary": return {"counts":dict(Counter(str(r.get("severity","unknown")) for r in records))}
    if req.operation=="root_cause_summary": return {"counts":dict(Counter(str(r.get("root_cause","unknown")) for r in records))}
    if req.operation=="date_distribution": return {"counts":dict(Counter(str(r.get("created_date","unknown"))[:7] for r in records))}
    raise ValueError("Unsupported operation")

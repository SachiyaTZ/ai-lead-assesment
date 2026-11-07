from app.tools.analysis import run_analysis
from app.models.schemas import AnalysisRequest
def test_controlled_analysis():
    r=run_analysis(AnalysisRequest(operation="root_cause_summary",records=[{"root_cause":"timeout"},{"root_cause":"timeout"},{"root_cause":"db"}]))
    assert r["counts"]["timeout"]==2

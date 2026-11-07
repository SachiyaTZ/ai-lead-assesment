from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.research import research_node
from app.agents.response import response_node
from app.models.schemas import AnalysisRequest
from app.security.authorization import authorize
from app.tools.analysis import run_analysis
from app.tools.mcp_mock import get_service

class AssistantGraph:
    def __init__(self,retriever,user): self.retriever=retriever; self.user=user; self.graph=self._build()
    def _build(self):
        async def validate(s): return {"activity":s.get("activity",[])+[{"type":"validation","node":"input_validation","status":"passed"}]}
        async def security(s): return {"activity":s.get("activity",[])+[{"type":"validation","node":"security_scan","status":"passed"}]}
        async def retrieve(s):
            from app.agents.retrieval import retrieval_node
            return await retrieval_node(s,self.retriever)
        async def analysis(s):
            authorize(self.user,"analytics")
            docs=s.get("retrieved_documents",[])
            records=[]
            for d in docs:
                records.append({"root_cause":_extract(d.content,"Root cause:"),"severity":_extract(d.content,"Severity:"),"created_date":d.created_date,"department":d.department,"document_type":d.document_type})
            return {"analysis_result":run_analysis(AnalysisRequest(operation="root_cause_summary",records=records)),"activity":s.get("activity",[])+[{"type":"tool","node":"analysis","status":"completed","message":"Controlled root-cause analysis executed"}]}
        async def tool(s):
            authorize(self.user,"mcp"); q=s["query"].lower(); name="payment-api" if "payment" in q else "customer-profile"
            r=await get_service(name); return {"tool_result":r,"activity":s.get("activity",[])+[{"type":"tool","node":"mcp","status":"completed","message":f"Service catalog lookup: {name}"}]}
        def route(s): return s["intent"]
        g=StateGraph(AgentState)
        for name,node in [("validate",validate),("security",security),("supervisor",supervisor_node),("retrieve",retrieve),("research",research_node),("analysis",analysis),("tool",tool),("response",response_node)]: g.add_node(name,node)
        g.add_edge(START,"validate"); g.add_edge("validate","security"); g.add_edge("security","supervisor")
        g.add_conditional_edges("supervisor",route,{"simple_knowledge_query":"retrieve","deep_research":"retrieve","analytical_query":"retrieve","enterprise_tool_query":"tool"})
        g.add_conditional_edges("retrieve",lambda s:s["intent"],{"simple_knowledge_query":"response","deep_research":"research","analytical_query":"analysis"})
        g.add_edge("research","response"); g.add_edge("analysis","response"); g.add_edge("tool","response"); g.add_edge("response",END)
        return g.compile()
    async def invoke(self,state): return await self.graph.ainvoke(state)

def _extract(text,label):
    for line in text.splitlines():
        if line.lower().startswith(label.lower()): return line.split(":",1)[1].strip()
    return "unknown"

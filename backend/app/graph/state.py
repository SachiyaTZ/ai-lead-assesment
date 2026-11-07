from typing import TypedDict,Any
class AgentState(TypedDict,total=False):
    messages:list[dict[str,str]]
    user_id:str
    role:str
    conversation_id:str
    query:str
    intent:str
    plan:list[str]
    retrieved_documents:list[Any]
    citations:list[str]
    tool_calls:list[dict]
    validation_results:list[dict]
    memory_context:dict
    recursion_depth:int
    errors:list[str]
    activity:list[dict]
    analysis_result:dict
    tool_result:dict
    final_answer:str

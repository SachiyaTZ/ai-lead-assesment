import uuid
from app.core.config import get_settings
from app.core.exceptions import ValidationError
from app.graph.workflow import AssistantGraph
from app.security.injection import scan_user_input
from app.security.authorization import authorize

class AssistantService:
    def __init__(self,retriever,memory,limiter): self.retriever=retriever; self.memory=memory; self.limiter=limiter
    async def chat(self,user,message,conversation_id=None):
        s=get_settings(); authorize(user,"chat"); await self.limiter.consume(user.user_id)
        if len(message)>s.max_message_length: raise ValidationError("Message too long")
        sec=scan_user_input(message)
        if not sec.allowed:
            return {"conversation_id":conversation_id or str(uuid.uuid4()),"answer":"I can’t follow instructions that attempt to bypass security controls, expose secrets, or escalate privileges.","citations":[],"activity":[{"type":"validation","node":"security_scan","status":"blocked","message":"Prompt-injection pattern detected"}]}
        cid=conversation_id or str(uuid.uuid4()); mem=await self.memory.get(cid)
        graph=AssistantGraph(self.retriever,user)
        state={"messages":[],"user_id":user.user_id,"role":user.role.value,"conversation_id":cid,"query":message,"memory_context":mem,"recursion_depth":0,"errors":[],"activity":[]}
        result=await graph.invoke(state); answer=result.get("final_answer","")
        citations=list(dict.fromkeys(result.get("citations",[])))
        await self.memory.add_turn(cid,message,answer,citations)
        result.update({"conversation_id":cid,"answer":answer,"citations":citations})
        return result

import asyncio, json
from fastapi import APIRouter,Depends,Request
from fastapi.responses import StreamingResponse
from app.auth.dependencies import current_user
from app.auth.users import authenticate,User
from app.auth.jwt import create_access_token
from app.core.exceptions import AuthenticationError
from app.models.schemas import LoginRequest,TokenResponse,ChatRequest,ChatResponse

router=APIRouter()
@router.post("/auth/login",response_model=TokenResponse)
async def login(req:LoginRequest):
    user=authenticate(req.email,req.password)
    if not user: raise AuthenticationError("Invalid email or password")
    return TokenResponse(access_token=create_access_token(user),user_id=user.user_id,role=user.role)

@router.post("/chat",response_model=ChatResponse)
async def chat(req:ChatRequest,request:Request,user:User=Depends(current_user)):
    r=await request.app.state.assistant.chat(user,req.message,req.conversation_id)
    return ChatResponse(conversation_id=r["conversation_id"],answer=r["answer"],citations=r.get("citations",[]),activity=r.get("activity",[]))

@router.post("/chat/stream")
async def chat_stream(req:ChatRequest,request:Request,user:User=Depends(current_user)):
    async def gen():
        try:
            yield f"data: {json.dumps({'type':'state','node':'request','status':'accepted'})}\n\n"
            result=await request.app.state.assistant.chat(user,req.message,req.conversation_id)
            for event in result.get("activity",[]):
                yield f"data: {json.dumps(event)}\n\n"; await asyncio.sleep(0)
            for token in result["answer"].split(" "):
                yield f"data: {json.dumps({'type':'token','content':token+' '})}\n\n"; await asyncio.sleep(0.005)
            yield f"data: {json.dumps({'type':'done','conversation_id':result['conversation_id'],'citations':result.get('citations',[])})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type':'error','message':str(e)})}\n\n"
    return StreamingResponse(gen(),media_type="text/event-stream")

@router.get("/conversations/{conversation_id}")
async def conversation(conversation_id:str,request:Request,user:User=Depends(current_user)):
    return await request.app.state.memory.get(conversation_id)
@router.delete("/conversations/{conversation_id}")
async def clear(conversation_id:str,request:Request,user:User=Depends(current_user)):
    await request.app.state.memory.clear(conversation_id); return {"status":"cleared"}
@router.get("/health")
async def health(): return {"status":"ok"}
@router.get("/ready")
async def ready(request:Request): return {"status":"ready","documents":len(request.app.state.store.docs)}

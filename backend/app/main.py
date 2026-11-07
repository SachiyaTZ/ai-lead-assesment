from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.core.config import get_settings
from app.core.logging import configure_logging,logger
from app.core.exceptions import AppError
from app.rag.documents import DocumentStore
from app.rag.hybrid import HybridRetriever
from app.memory.session import SessionMemory
from app.rate_limit.token_bucket import TokenBucketLimiter
from app.services.assistant import AssistantService
from app.observability.tracing import configure_langsmith
import time, uuid

s=get_settings(); configure_logging(s.log_level); configure_langsmith(); log=logger(__name__)
@asynccontextmanager
async def lifespan(app:FastAPI):
    data=Path(s.data_dir)
    if not data.exists():
        data=Path(__file__).resolve().parents[3]/"data"
    store=DocumentStore(str(data)); store.load(); dw,sw=s.weights; retriever=HybridRetriever(store.docs,dw,sw); await retriever.prepare()
    memory=SessionMemory(); limiter=TokenBucketLimiter(s.rate_limit_capacity,s.rate_limit_refill_rate)
    app.state.store=store; app.state.memory=memory; app.state.assistant=AssistantService(retriever,memory,limiter)
    log.info("startup",documents=len(store.docs)); yield

app=FastAPI(title=s.app_name,version="1.0.0",lifespan=lifespan)

@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        log.info("request_complete", request_id=request_id, path=request.url.path, method=request.method, status=response.status_code, latency_ms=round((time.perf_counter()-started)*1000,2))
        return response
    except Exception:
        log.exception("request_failed", request_id=request_id, path=request.url.path, method=request.method, latency_ms=round((time.perf_counter()-started)*1000,2))
        raise
app.include_router(router,prefix=s.api_prefix)
@app.exception_handler(AppError)
async def app_error_handler(request:Request,exc:AppError):
    return JSONResponse(status_code=exc.status_code,content={"error":{"code":exc.code,"message":exc.message,"details":exc.details}})
@app.exception_handler(Exception)
async def unhandled(request:Request,exc:Exception):
    log.exception("unhandled_error",path=str(request.url.path)); return JSONResponse(status_code=500,content={"error":{"code":"internal_error","message":"Unexpected server error"}})

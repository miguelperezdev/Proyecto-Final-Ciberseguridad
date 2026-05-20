import datetime
from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse
from app.config import TASK_PROMPTS
from app.services.validation_service import validate_input
from app.services.audit_service import log_interaction, get_recent_logs, get_blocked_logs
from app.services.ollama_service import query_ollama

router = APIRouter()

@router.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "CyberDefense Assistant API v1.0.0"}

@router.post("/chat", response_model=ChatResponse, tags=["Assistant"])
async def chat(req: ChatRequest):
    valid, reason = validate_input(req.message)
    if not valid:
        log_interaction(req.task, req.message, blocked=True, block_reason=reason)
        raise HTTPException(status_code=400, detail=reason)

    task_context = TASK_PROMPTS.get(req.task, "")
    full_user_msg = task_context + req.message

    ia_response = await query_ollama(full_user_msg)
    timestamp = datetime.datetime.now().isoformat()

    log_interaction(req.task, req.message, ia_resp=ia_response)

    return ChatResponse(task=req.task, response=ia_response, timestamp=timestamp)

@router.get("/logs", tags=["Audit"])
def get_logs(limit: int = 50):
    return get_recent_logs(limit)

@router.get("/logs/blocked", tags=["Audit"])
def blocked_logs():
    return get_blocked_logs()
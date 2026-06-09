from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Depends

from app.config import API_KEY
from app.models import ChatCompletionRequest
from app.queue import queue
from app.redis_client import redis_conn
from app.tasks import run_command_code
from app.services.command_code import ask_command_code
from app.utils.openai_response import create_chat_completion_response


# =====================================================
# AUTH
# =====================================================

def verify_api_key(
    authorization: str = Header(None)
):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    if authorization != f"Bearer {API_KEY}":
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    return authorization


# =====================================================
# APP
# =====================================================

app = FastAPI(
    title="Command Code API",
    version="1.0.0"
)


# =====================================================
# BASIC ENDPOINTS
# =====================================================

@app.get("/")
async def root():
    return {
        "service": "Command Code API",
        "status": "ok"
    }


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": "command-code",
                "object": "model",
                "owned_by": "wempy"
            }
        ]
    }


# =====================================================
# OPENAI COMPATIBLE (SYNC)
# =====================================================

@app.post("/v1/chat/completions")
async def chat_completion(
    request: ChatCompletionRequest,
    _: str = Depends(verify_api_key)
):

    prompt = "\n".join(
        f"{msg.role}: {msg.content}"
        for msg in request.messages
    )

    output = ask_command_code(prompt)

    return create_chat_completion_response(
        output,
        request.model or "command-code"
    )


# =====================================================
# ASYNC MODE
# =====================================================

@app.post("/v1/chat/completions/async")
async def create_chat_completion_async(
    request: ChatCompletionRequest,
    _: str = Depends(verify_api_key)
):

    job_id = str(uuid4())

    prompt = "\n".join(
        f"{msg.role}: {msg.content}"
        for msg in request.messages
    )

    redis_conn.hset(
        f"job:{job_id}",
        mapping={
            "status": "queued",
            "prompt": prompt
        }
    )

    queue.enqueue(
        run_command_code,
        prompt,
        job_id
    )

    return {
        "id": job_id,
        "object": "chat.completion.job",
        "status": "queued"
    }


# =====================================================
# JOB STATUS
# =====================================================

@app.get("/v1/jobs/{job_id}")
async def get_job(job_id: str):

    raw = redis_conn.hgetall(
        f"job:{job_id}"
    )

    if not raw:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    data = {}

    for k, v in raw.items():

        if isinstance(k, bytes):
            k = k.decode()

        if isinstance(v, bytes):
            v = v.decode()

        data[k] = v

    return data
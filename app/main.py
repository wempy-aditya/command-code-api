from uuid import uuid4

from fastapi import FastAPI
from app.tasks import run_command_code

from app.models import ChatCompletionRequest
from app.queue import queue
from app.redis_client import redis_conn

app = FastAPI(
    title="Command Code API",
    version="1.0.0"
)


@app.get("/health")
async def health():
    return {
        "status": "ok"
    }


@app.post("/v1/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest
):

    job_id = str(uuid4())

    prompt = request.messages[-1].content

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
        job_id=job_id
    )

    return {
        "id": job_id,
        "object": "chat.completion.job",
        "status": "queued"
    }


@app.get("/v1/jobs/{job_id}")
async def get_job(job_id: str):

    raw = redis_conn.hgetall(
    f"job:{job_id}"
    )

    data = {
        k.decode(): v.decode()
        for k, v in raw.items()
    }

    if not data:
        return {
            "error": "job not found"
        }

    return data
from uuid import uuid4

from fastapi import FastAPI
from app.tasks import run_command_code

from app.models import ChatCompletionRequest
from app.queue import queue
from app.redis_client import redis_conn
from app.services.command_code import ask_command_code

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
        job_id
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

    if not raw:
        return {
            "error": "job not found"
        }

    data = {}

    for k, v in raw.items():

        if isinstance(k, bytes):
            k = k.decode()

        if isinstance(v, bytes):
            v = v.decode()

        data[k] = v

    return data

@app.post("/v1/chat/completions-sync")
async def chat_completion_sync(
    request: ChatCompletionRequest
):

    prompt = request.messages[-1].content

    output = ask_command_code(prompt)

    return {
        "id": "chatcmpl-local",
        "object": "chat.completion",
        "model": "command-code",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": output
                },
                "finish_reason": "stop"
            }
        ]
    }
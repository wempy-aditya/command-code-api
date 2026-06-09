import subprocess

from app.config import CMD_BINARY
from app.redis_client import redis_conn


def run_command_code(
    prompt: str,
    job_id: str
):

    redis_conn.hset(
        f"job:{job_id}",
        mapping={
            "status": "running"
        }
    )

    try:

        result = subprocess.run(
            [
                CMD_BINARY,
                "-p",
                prompt
            ],
            capture_output=True,
            text=True
        )

        output = result.stdout.strip()

        redis_conn.hset(
            f"job:{job_id}",
            mapping={
                "status": "completed",
                "result": output
            }
        )

        return output

    except Exception as e:

        redis_conn.hset(
            f"job:{job_id}",
            mapping={
                "status": "failed",
                "error": str(e)
            }
        )

        raise
import os
import sys
from pathlib import Path

from redis import Redis
from rq import Worker, Queue

BASE_DIR = Path(__file__).resolve().parent.parent

redis_conn = Redis(
    host="localhost",
    port=6378,
    decode_responses=True
)

listen = ["command_code"]

if __name__ == "__main__":
    worker = Worker(
        [Queue(name, connection=redis_conn) for name in listen],
        connection=redis_conn
    )

    print("Worker started...")
    print(redis_conn)
    print(redis_conn.connection_pool.connection_kwargs)
    worker.work()
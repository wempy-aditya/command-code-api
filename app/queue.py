from rq import Queue

from app.redis_client import redis_conn

queue = Queue(
    "command_code",
    connection=redis_conn
)
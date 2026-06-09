from rq import Worker, Queue

from app.redis_client import redis_conn

listen = ["command_code"]

if __name__ == "__main__":
    worker = Worker(
        [Queue(name, connection=redis_conn) for name in listen],
        connection=redis_conn
    )

    print("Worker started...")
    worker.work()
from redis import Redis

redis_conn = Redis(
    host="localhost",
    port=6378,
    decode_responses=True
)
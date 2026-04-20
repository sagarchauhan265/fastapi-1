import redis
# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     db=0,
#     decode_responses=True  # return str instead of bytes
# )

try:
    redis_client = redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True,  # return str instead of bytes
        # seconds
    )

    # Ping Redis server
    if redis_client.ping():
        print("Connected to Redis successfully!")
    else:
        print("Redis connection failed.")
except redis.ConnectionError as e:
    print(f"Connection error: {e}")
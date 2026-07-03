import redis
import os

def get_redis():
    try:
        redis_url=os.environ["REDIS_URL"]
        r = redis.Redis.from_url(redis_url)
        return r
    except KeyError:
        return None

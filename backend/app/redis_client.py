import redis
from app.config import settings

def get_redis_client():
    return redis.Redis.from_url(settings.REDIS_URL)
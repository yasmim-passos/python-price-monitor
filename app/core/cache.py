import redis
import json
from typing import Optional, Any
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = settings.CACHE_TTL_SECONDS) -> bool:
        """Set value in cache with TTL"""
        try:
            self.redis.setex(
                key,
                ttl,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.redis.exists(key))
        except Exception as e:
            print(f"Redis EXISTS error: {e}")
            return False
    
    def flush_all(self) -> bool:
        """Clear all cache (use with caution!)"""
        try:
            self.redis.flushdb()
            return True
        except Exception as e:
            print(f"Redis FLUSHDB error: {e}")
            return False


# Singleton instance
redis_client = RedisClient()


def get_redis() -> RedisClient:
    """Dependency for Redis client"""
    return redis_client

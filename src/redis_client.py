import redis
import json
from typing import Optional, Any
from src.config import get_settings

settings = get_settings()


class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            username=settings.redis_username if settings.redis_username else None,
            password=settings.redis_password if settings.redis_password else None,
            decode_responses=True,
        )

    def set_session(self, session_id: str, data: dict, expiry: int = None) -> bool:
        """Store session data in Redis"""
        expiry = expiry or settings.session_expiry_seconds
        try:
            self.client.setex(f"session:{session_id}", expiry, json.dumps(data))
            return True
        except Exception as e:
            print(f"Error setting session: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data from Redis"""
        try:
            data = self.client.get(f"session:{session_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None

    def delete_session(self, session_id: str) -> bool:
        """Delete session from Redis"""
        try:
            self.client.delete(f"session:{session_id}")
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def extend_session(self, session_id: str, expiry: int = None) -> bool:
        """Extend session expiry time"""
        expiry = expiry or settings.session_expiry_seconds
        try:
            self.client.expire(f"session:{session_id}", expiry)
            return True
        except Exception as e:
            print(f"Error extending session: {e}")
            return False

    def session_exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return self.client.exists(f"session:{session_id}") > 0


redis_client = RedisClient()

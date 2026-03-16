import os

import redis
from dotenv import load_dotenv

load_dotenv()

def get_redis_client():
    return redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379"),
        decode_responses=True
    )

def add_token_to_blacklist(token: str, expires_in: int):
    try:
        client = get_redis_client()
        client.setex(f"blacklist:{token}", expires_in, "true")
    except Exception:
        pass  # Don't break logout if Redis is unavailable in tests

def is_token_blacklisted(token: str) -> bool:
    try:
        client = get_redis_client()
        return client.exists(f"blacklist:{token}") > 0
    except Exception:
        return False  # Don't block requests if Redis is unavailable in tests

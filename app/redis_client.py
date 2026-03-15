import redis
import os
from dotenv import load_dotenv

load_dotenv()

redis_client=redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

def add_token_to_blacklist(token:str,expires_in:int):
    redis_client.setex(f"blacklist:{token}",expires_in,"true")

def is_token_blackllisted(token:str)->bool:
    return redis_client.exists(f"blacklist:{token}")>0
import json
import re

import redis

from config import settings


_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
        )
    return _client


def _key(query: str) -> str:
    norm = re.sub(r"\s+", " ", query.strip().lower())
    return f"search:{norm}"


def get_cached(query: str):
    raw = get_redis().get(_key(query))
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def set_cached(query: str, payload: dict) -> None:
    get_redis().setex(_key(query), settings.REDIS_TTL, json.dumps(payload))


def ping() -> bool:
    try:
        return get_redis().ping()
    except Exception:
        return False

"""Redis service — centralized connection and key helpers."""
import json
from typing import Any
from config import get_settings

settings = get_settings()

# Synchronous Redis client (used from sync FastAPI routes)
_client = None


def get_redis():
    """Returns real Redis or in-memory fallback depending on REDIS_URL."""
    global _client
    if _client is None:
        if settings.redis_url.startswith("memory://"):
            from services.memory_redis import _memory_client
            _client = _memory_client
        else:
            import redis
            _client = redis.from_url(settings.redis_url, decode_responses=True)
    return _client



# ─── Key helpers ─────────────────────────────────────────────────────────────

def agent_session_key(customer_id: str) -> str:
    return f"agent:session:{customer_id}"


def nudge_limit_key(customer_id: str) -> str:
    return f"nudge:limit:{customer_id}"


def ws_session_key(banker_id: str) -> str:
    return f"ws:session:{banker_id}"


DEMO_STATE_KEY = "demo:run:state"


# ─── Convenience wrappers ─────────────────────────────────────────────────────

def get_json(key: str) -> Any | None:
    r = get_redis()
    val = r.get(key)
    if val:
        return json.loads(val)
    return None


def set_json(key: str, value: Any, ttl_seconds: int | None = None) -> None:
    r = get_redis()
    serialized = json.dumps(value)
    if ttl_seconds:
        r.setex(key, ttl_seconds, serialized)
    else:
        r.set(key, serialized)


def get_nudge_count(customer_id: str) -> int:
    r = get_redis()
    val = r.get(nudge_limit_key(customer_id))
    return int(val) if val else 0


def increment_nudge_count(customer_id: str) -> int:
    r = get_redis()
    key = nudge_limit_key(customer_id)
    pipe = r.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)  # 24 hours
    result = pipe.execute()
    return result[0]


def set_demo_state(state: dict) -> None:
    set_json(DEMO_STATE_KEY, state)


def get_demo_state() -> dict | None:
    return get_json(DEMO_STATE_KEY)


def clear_demo_state() -> None:
    get_redis().delete(DEMO_STATE_KEY)


def check_redis_health() -> bool:
    try:
        get_redis().ping()
        return True
    except Exception:
        return False

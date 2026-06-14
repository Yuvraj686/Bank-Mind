"""
In-memory Redis fallback — used when REDIS_URL starts with 'memory://'
Provides the same interface as the real redis_service.py
"""
import json
import time
import threading
from typing import Any

_store: dict[str, tuple[Any, float | None]] = {}
_lock = threading.Lock()


class MemoryRedis:
    """Minimal Redis-like in-memory store."""

    def get(self, key: str) -> str | None:
        with _lock:
            entry = _store.get(key)
            if entry is None:
                return None
            value, exp = entry
            if exp and time.time() > exp:
                del _store[key]
                return None
            return value

    def set(self, key: str, value: str) -> None:
        with _lock:
            _store[key] = (value, None)

    def setex(self, key: str, ttl: int, value: str) -> None:
        with _lock:
            _store[key] = (value, time.time() + ttl)

    def incr(self, key: str) -> int:
        with _lock:
            entry = _store.get(key)
            if entry is None:
                _store[key] = ('1', None)
                return 1
            val = int(entry[0]) + 1
            _store[key] = (str(val), entry[1])
            return val

    def expire(self, key: str, ttl: int) -> None:
        with _lock:
            entry = _store.get(key)
            if entry:
                _store[key] = (entry[0], time.time() + ttl)

    def delete(self, key: str) -> None:
        with _lock:
            _store.pop(key, None)

    def ping(self) -> bool:
        return True

    def pipeline(self):
        return MemoryPipeline(self)

    def flushall(self):
        with _lock:
            _store.clear()


class MemoryPipeline:
    def __init__(self, redis: MemoryRedis):
        self._redis = redis
        self._cmds = []
        self._results = []

    def incr(self, key: str):
        self._cmds.append(('incr', key))
        return self

    def expire(self, key: str, ttl: int):
        self._cmds.append(('expire', key, ttl))
        return self

    def execute(self) -> list:
        results = []
        for cmd in self._cmds:
            if cmd[0] == 'incr':
                results.append(self._redis.incr(cmd[1]))
            elif cmd[0] == 'expire':
                self._redis.expire(cmd[1], cmd[2])
                results.append(True)
        return results


_memory_client = MemoryRedis()

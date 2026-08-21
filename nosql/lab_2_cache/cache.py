import threading
import time
from typing import Any, Callable, Optional


class Cache:
    def __init__(self, cleanup_interval: float = 0.1):
        self._store: dict[Any, Any] = {}
        self._expirations: dict[Any, float] = {}
        self._lock = threading.RLock()
        self._cleanup_interval = cleanup_interval
        self._stop_event = threading.Event()
        self._cleaner = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._cleaner.start()

    def _cleanup_loop(self) -> None:
        while not self._stop_event.wait(self._cleanup_interval):
            now = time.monotonic()
            with self._lock:
                expired = [k for k, exp in self._expirations.items() if exp <= now]
                for k in expired:
                    self._store.pop(k, None)
                    self._expirations.pop(k, None)

    def set(self, k: Any, v: Any, ttl: Optional[float] = None) -> None:
        if k is None:
            raise ValueError("key must not be None")
        with self._lock:
            self._store[k] = v
            if ttl is not None:
                self._expirations[k] = time.monotonic() + ttl
            else:
                self._expirations.pop(k, None)

    def get(self, k: Any) -> Any:
        if k is None:
            raise ValueError("key must not be None")
        with self._lock:
            exp = self._expirations.get(k)
            if exp is not None and exp <= time.monotonic():
                self._store.pop(k, None)
                self._expirations.pop(k, None)
                return None
            return self._store.get(k)

    def delete(self, k: Any) -> Any:
        if k is None:
            raise ValueError("key must not be None")
        with self._lock:
            self._expirations.pop(k, None)
            return self._store.pop(k, None)

    def compute_if_present(self, k: Any, func: Callable[[Any], Any]) -> Any:
        if k is None:
            raise ValueError("key must not be None")
        with self._lock:
            exp = self._expirations.get(k)
            if exp is not None and exp <= time.monotonic():
                self._store.pop(k, None)
                self._expirations.pop(k, None)
                return None
            if k not in self._store:
                return None
            new_value = func(self._store[k])
            self._store[k] = new_value
            return new_value

    def close(self) -> None:
        self._stop_event.set()
        self._cleaner.join(timeout=1.0)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

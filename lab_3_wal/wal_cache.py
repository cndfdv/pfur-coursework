import json
import os
import threading
import time
from typing import Any, Optional

_TOMBSTONE = object()


class WalCache:
    def __init__(self, wal_path: str, compaction_interval: float = 60.0):
        self._wal_path = wal_path
        self._store: dict[Any, Any] = {}
        self._lock = threading.RLock()
        self._wal_lock = threading.Lock()

        os.makedirs(os.path.dirname(os.path.abspath(wal_path)) or ".", exist_ok=True)
        if not os.path.exists(wal_path):
            open(wal_path, "a").close()
        else:
            self._replay()

        self._stop_event = threading.Event()
        self._compaction_interval = compaction_interval
        self._compactor = threading.Thread(target=self._compaction_loop, daemon=True)
        self._compactor.start()

    @property
    def wal_path(self) -> str:
        return self._wal_path

    def _replay(self) -> None:
        with open(self._wal_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                op = rec.get("op")
                k = rec.get("k")
                if op == "set":
                    self._store[k] = rec.get("v")
                elif op == "del":
                    self._store.pop(k, None)

    def _append_wal(self, record: dict) -> None:
        line = json.dumps(record, ensure_ascii=False) + "\n"
        with self._wal_lock:
            with open(self._wal_path, "a", encoding="utf-8") as f:
                f.write(line)
                f.flush()
                os.fsync(f.fileno())

    def set(self, k: Any, v: Any) -> None:
        if k is None:
            raise ValueError("key must not be None")
        self._append_wal({"op": "set", "k": k, "v": v})
        with self._lock:
            self._store[k] = v

    def get(self, k: Any) -> Any:
        if k is None:
            raise ValueError("key must not be None")
        with self._lock:
            return self._store.get(k)

    def delete(self, k: Any) -> Any:
        if k is None:
            raise ValueError("key must not be None")
        self._append_wal({"op": "del", "k": k})
        with self._lock:
            return self._store.pop(k, None)

    def compact(self) -> None:
        tmp_path = self._wal_path + ".compact"
        with self._wal_lock:
            with self._lock:
                snapshot = list(self._store.items())
            with open(tmp_path, "w", encoding="utf-8") as f:
                for k, v in snapshot:
                    f.write(json.dumps({"op": "set", "k": k, "v": v}, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, self._wal_path)

    def _compaction_loop(self) -> None:
        while not self._stop_event.wait(self._compaction_interval):
            try:
                self.compact()
            except Exception:
                pass

    def close(self) -> None:
        self._stop_event.set()
        self._compactor.join(timeout=1.0)

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

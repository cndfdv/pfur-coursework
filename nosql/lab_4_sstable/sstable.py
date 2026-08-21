"""SSTable: HEADER | DATA BLOCKS | SPARSE_INDEX | FOOTER.

Все ключи/значения — строки UTF-8.
Записи в DATA BLOCKS отсортированы по ключу.
SPARSE_INDEX содержит каждый N-й ключ и смещение его записи в DATA BLOCKS,
что позволяет искать значение без чтения всего файла.
"""

import json
import os
import struct
import threading
from typing import Optional

MAGIC = b"SSTB0001"
FOOTER_MAGIC = b"FTR00001"
DEFAULT_SPARSE_STEP = 64

# заголовки фиксированной длины:
# HEADER:  MAGIC(8) | entry_count(u32) | sparse_step(u32) | data_offset(u64)
# FOOTER:  sparse_offset(u64) | sparse_count(u32) | FOOTER_MAGIC(8)
HEADER_FMT = "<8sIIQ"
HEADER_SIZE = struct.calcsize(HEADER_FMT)
FOOTER_FMT = "<QI8s"
FOOTER_SIZE = struct.calcsize(FOOTER_FMT)


def _write_kv(f, key: str, value: str) -> None:
    kb = key.encode("utf-8")
    vb = value.encode("utf-8")
    f.write(struct.pack("<I", len(kb)))
    f.write(kb)
    f.write(struct.pack("<I", len(vb)))
    f.write(vb)


def _read_kv(f) -> tuple[str, str]:
    (kl,) = struct.unpack("<I", f.read(4))
    k = f.read(kl).decode("utf-8")
    (vl,) = struct.unpack("<I", f.read(4))
    v = f.read(vl).decode("utf-8")
    return k, v


class Cache:
    """In-memory кэш для подготовки SSTable."""

    def __init__(self):
        self._store: dict[str, str] = {}

    def set(self, k: str, v: str) -> None:
        if k is None:
            raise ValueError("key must not be None")
        self._store[str(k)] = str(v)

    def get(self, k: str) -> Optional[str]:
        return self._store.get(k)

    def delete(self, k: str) -> Optional[str]:
        return self._store.pop(k, None)

    def __len__(self) -> int:
        return len(self._store)

    def flush_to_sstable(self, path: str, sparse_step: int = DEFAULT_SPARSE_STEP) -> None:
        items = sorted(self._store.items())
        with open(path, "wb") as f:
            f.write(b"\x00" * HEADER_SIZE)  # резерв под HEADER
            data_offset = f.tell()

            sparse: list[tuple[str, int]] = []
            for i, (k, v) in enumerate(items):
                offset = f.tell()
                if i % sparse_step == 0:
                    sparse.append((k, offset))
                _write_kv(f, k, v)

            sparse_offset = f.tell()
            for k, off in sparse:
                kb = k.encode("utf-8")
                f.write(struct.pack("<I", len(kb)))
                f.write(kb)
                f.write(struct.pack("<Q", off))

            f.write(struct.pack(FOOTER_FMT, sparse_offset, len(sparse), FOOTER_MAGIC))

            f.seek(0)
            f.write(struct.pack(HEADER_FMT, MAGIC, len(items), sparse_step, data_offset))
            f.flush()
            os.fsync(f.fileno())


class SSTableReader:
    """Чтение SSTable: GET ищет ключ через sparse index и линейный скан блока."""

    def __init__(self, path: str):
        self._path = path
        self._lock = threading.Lock()
        with open(path, "rb") as f:
            header = f.read(HEADER_SIZE)
            magic, entry_count, sparse_step, data_offset = struct.unpack(HEADER_FMT, header)
            if magic != MAGIC:
                raise ValueError("bad SSTable magic")

            f.seek(-FOOTER_SIZE, os.SEEK_END)
            sparse_offset, sparse_count, fmagic = struct.unpack(FOOTER_FMT, f.read(FOOTER_SIZE))
            if fmagic != FOOTER_MAGIC:
                raise ValueError("bad footer magic")

            f.seek(sparse_offset)
            sparse: list[tuple[str, int]] = []
            for _ in range(sparse_count):
                (kl,) = struct.unpack("<I", f.read(4))
                k = f.read(kl).decode("utf-8")
                (off,) = struct.unpack("<Q", f.read(8))
                sparse.append((k, off))

        self._entry_count = entry_count
        self._sparse_step = sparse_step
        self._data_offset = data_offset
        self._sparse_offset = sparse_offset
        self._sparse = sparse

    @property
    def entry_count(self) -> int:
        return self._entry_count

    def get(self, key: str) -> Optional[str]:
        # binary search по sparse index: ищем последний ключ, который <= искомому
        lo, hi = 0, len(self._sparse) - 1
        if hi < 0 or key < self._sparse[0][0]:
            return None
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self._sparse[mid][0] <= key:
                lo = mid
            else:
                hi = mid - 1
        start_offset = self._sparse[lo][1]
        # верхняя граница — следующий sparse ключ или начало sparse-секции
        end_offset = self._sparse[lo + 1][1] if lo + 1 < len(self._sparse) else self._sparse_offset

        with self._lock, open(self._path, "rb") as f:
            f.seek(start_offset)
            while f.tell() < end_offset:
                k, v = _read_kv(f)
                if k == key:
                    return v
                if k > key:
                    return None
        return None

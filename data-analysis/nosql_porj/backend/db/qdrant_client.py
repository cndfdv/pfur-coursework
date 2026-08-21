import time

from qdrant_client import QdrantClient
from qdrant_client.http import models as qm

from config import settings


_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _client


def wait_ready(timeout_s: int = 60) -> None:
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            get_qdrant().get_collections()
            return
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"Qdrant not ready after {timeout_s}s: {last_err}")


def ensure_collection() -> None:
    wait_ready()
    client = get_qdrant()
    existing = {c.name for c in client.get_collections().collections}
    if settings.QDRANT_COLLECTION not in existing:
        client.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=qm.VectorParams(
                size=settings.VECTOR_SIZE,
                distance=qm.Distance.COSINE,
            ),
        )


def search(vector: list[float], limit: int = 10):
    client = get_qdrant()
    return client.search(
        collection_name=settings.QDRANT_COLLECTION,
        query_vector=vector,
        limit=limit,
        with_payload=True,
    )


def upsert_points(points: list[qm.PointStruct]) -> None:
    client = get_qdrant()
    client.upsert(collection_name=settings.QDRANT_COLLECTION, points=points)


def count_points() -> int:
    client = get_qdrant()
    try:
        return client.count(collection_name=settings.QDRANT_COLLECTION).count
    except Exception:
        return 0


def ping() -> bool:
    try:
        get_qdrant().get_collections()
        return True
    except Exception:
        return False

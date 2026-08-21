import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer

from config import settings
from db import clickhouse_client, mongo_client, qdrant_client, redis_client


model: SentenceTransformer | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    model = SentenceTransformer(settings.MODEL_NAME)

    try:
        qdrant_client.ensure_collection()
    except Exception as e:
        print(f"[startup] qdrant init failed: {e}")
    try:
        clickhouse_client.ensure_schema()
    except Exception as e:
        print(f"[startup] clickhouse init failed: {e}")
    try:
        mongo_client.ensure_indexes()
    except Exception as e:
        print(f"[startup] mongo init failed: {e}")

    yield


app = FastAPI(title="ArXiv Semantic Search", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def embed(text: str) -> list[float]:
    if model is None:
        raise RuntimeError("Model is not initialized")
    vec = model.encode(text, normalize_embeddings=True)
    return vec.tolist()


@app.get("/api/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(10, ge=1, le=50)):
    started = time.perf_counter()
    query = q.strip()
    if not query:
        raise HTTPException(status_code=400, detail="empty query")

    cached = redis_client.get_cached(query)
    if cached is not None:
        try:
            clickhouse_client.log_search(query, len(cached.get("results", [])))
        except Exception as e:
            print(f"[search] clickhouse log failed: {e}")
        cached = {**cached, "cached": True}
        cached["query_time_ms"] = int((time.perf_counter() - started) * 1000)
        for r in cached.get("results", []):
            r["cached"] = True
        return cached

    vector = embed(query)
    try:
        hits = qdrant_client.search(vector, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"qdrant error: {e}")

    arxiv_ids = [str(h.payload.get("arxiv_id")) for h in hits if h.payload]
    score_by_id = {str(h.payload.get("arxiv_id")): float(h.score) for h in hits if h.payload}

    try:
        meta_by_id = mongo_client.find_by_ids(arxiv_ids)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"mongo error: {e}")

    results = []
    for aid in arxiv_ids:
        meta = meta_by_id.get(aid)
        if not meta:
            continue
        results.append({
            "arxiv_id": aid,
            "title": meta.get("title", ""),
            "authors": meta.get("authors", []),
            "year": meta.get("year"),
            "categories": meta.get("categories", []),
            "abstract": meta.get("abstract", ""),
            "score": round(score_by_id.get(aid, 0.0), 4),
            "cached": False,
        })

    payload = {
        "results": results,
        "total": len(results),
        "cached": False,
        "query_time_ms": int((time.perf_counter() - started) * 1000),
    }

    try:
        redis_client.set_cached(query, payload)
    except Exception as e:
        print(f"[search] redis cache failed: {e}")

    try:
        clickhouse_client.log_search(query, len(results))
    except Exception as e:
        print(f"[search] clickhouse log failed: {e}")

    return payload


@app.get("/api/stats")
def stats():
    total = 0
    try:
        total = mongo_client.total_articles()
    except Exception as e:
        print(f"[stats] mongo total failed: {e}")

    by_year = []
    by_cat = []
    try:
        by_year = mongo_client.articles_by_year()
        by_cat = mongo_client.articles_by_category()
    except Exception as e:
        print(f"[stats] mongo aggregates failed: {e}")

    top = []
    total_searches = 0
    try:
        top = clickhouse_client.top_queries(10)
        total_searches = clickhouse_client.total_searches()
    except Exception as e:
        print(f"[stats] clickhouse failed: {e}")

    return {
        "total_articles": total,
        "total_searches": total_searches,
        "top_queries": top,
        "articles_by_year": by_year,
        "articles_by_category": by_cat,
    }


@app.get("/api/health")
def health():
    return {
        "qdrant": qdrant_client.ping(),
        "redis": redis_client.ping(),
        "clickhouse": clickhouse_client.ping(),
        "mongo": mongo_client.ping(),
        "model": model is not None,
    }


@app.get("/")
def root():
    return {"service": "arxiv-search", "docs": "/docs"}

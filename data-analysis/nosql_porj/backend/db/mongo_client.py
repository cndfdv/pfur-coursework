from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection

from config import settings


_client: MongoClient | None = None


def get_mongo() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            serverSelectionTimeoutMS=5000,
        )
    return _client


def get_collection() -> Collection:
    return get_mongo()[settings.MONGO_DB][settings.MONGO_COLLECTION]


def ensure_indexes() -> None:
    col = get_collection()
    col.create_index([("arxiv_id", ASCENDING)], unique=True)
    col.create_index([("year", ASCENDING)])
    col.create_index([("categories", ASCENDING)])


def find_by_ids(arxiv_ids: list[str]) -> dict[str, dict]:
    if not arxiv_ids:
        return {}
    col = get_collection()
    docs = col.find({"arxiv_id": {"$in": arxiv_ids}}, {"_id": 0})
    return {d["arxiv_id"]: d for d in docs}


def total_articles() -> int:
    return get_collection().estimated_document_count()


def articles_by_year() -> list[dict]:
    col = get_collection()
    pipeline = [
        {"$match": {"year": {"$ne": None}}},
        {"$group": {"_id": "$year", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    return [{"year": d["_id"], "count": d["count"]} for d in col.aggregate(pipeline)]


def articles_by_category() -> list[dict]:
    col = get_collection()
    pipeline = [
        {"$unwind": "$categories"},
        {"$group": {"_id": "$categories", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 20},
    ]
    return [{"category": d["_id"], "count": d["count"]} for d in col.aggregate(pipeline)]


def ping() -> bool:
    try:
        get_mongo().admin.command("ping")
        return True
    except Exception:
        return False

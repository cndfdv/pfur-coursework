"""Load arXiv articles into MongoDB + Qdrant.

Usage:
    python scripts/load_data.py --file /path/to/arxiv-metadata.json --limit 8000
    python scripts/load_data.py --fake 500   # generate Faker demo data
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import uuid
from pathlib import Path
from typing import Iterable, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qdrant_client.http import models as qm
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from config import settings
from db import clickhouse_client, mongo_client, qdrant_client

TARGET_CATEGORIES = {"cs.AI", "cs.LG", "cs.CV"}
BATCH_SIZE = 100


def parse_year(raw) -> int | None:
    if not raw:
        return None
    try:
        return int(str(raw)[:4])
    except (ValueError, TypeError):
        return None


def parse_authors(raw) -> list[str]:
    if isinstance(raw, list):
        return [str(a) for a in raw if a]
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.replace(" and ", ",").split(",")]
        return [p for p in parts if p]
    return []


def parse_categories(raw) -> list[str]:
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if c]
    if isinstance(raw, str):
        return [c.strip() for c in raw.split() if c.strip()]
    return []


def iter_arxiv_jsonl(path: Path, limit: int) -> Iterator[dict]:
    collected = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue

            cats = parse_categories(row.get("categories"))
            if not any(c in TARGET_CATEGORIES for c in cats):
                continue

            abstract = (row.get("abstract") or "").strip()
            title = (row.get("title") or "").strip()
            if not abstract or not title:
                continue

            year = parse_year(
                row.get("update_date") or row.get("journal-ref") or row.get("versions", [{}])[0].get("created")
            )

            yield {
                "arxiv_id": str(row.get("id") or row.get("arxiv_id")),
                "title": title,
                "authors": parse_authors(row.get("authors")),
                "year": year,
                "categories": [c for c in cats if c in TARGET_CATEGORIES] or cats[:3],
                "abstract": abstract,
            }

            collected += 1
            if collected >= limit:
                return


def iter_fake(count: int) -> Iterator[dict]:
    from faker import Faker

    fake = Faker()
    topics = [
        "attention mechanism", "graph neural network", "transformer", "diffusion model",
        "reinforcement learning", "image segmentation", "self-supervised learning",
        "large language model", "contrastive learning", "knowledge distillation",
        "neural architecture search", "vision transformer", "federated learning",
        "few-shot learning", "multi-modal", "representation learning",
    ]
    cats = list(TARGET_CATEGORIES)

    for i in range(count):
        topic = random.choice(topics)
        yield {
            "arxiv_id": f"demo.{i:05d}",
            "title": f"{topic.title()}: {fake.catch_phrase()}",
            "authors": [fake.name() for _ in range(random.randint(1, 4))],
            "year": random.randint(2015, 2024),
            "categories": random.sample(cats, k=random.randint(1, 2)),
            "abstract": (
                f"We study {topic} in the context of {fake.bs()}. "
                + " ".join(fake.paragraphs(nb=2))
            ),
        }


def batched(it: Iterable[dict], size: int) -> Iterator[list[dict]]:
    batch: list[dict] = []
    for item in it:
        batch.append(item)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def stable_point_id(arxiv_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"arxiv:{arxiv_id}"))


def load(records: Iterator[dict], model: SentenceTransformer, total_hint: int | None = None) -> int:
    col = mongo_client.get_collection()
    qdrant_client.ensure_collection()
    clickhouse_client.ensure_schema()
    mongo_client.ensure_indexes()

    loaded = 0
    pbar = tqdm(total=total_hint, desc="loading", unit="art")

    for batch in batched(records, BATCH_SIZE):
        texts = [r["abstract"] for r in batch]
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)

        try:
            from pymongo import UpdateOne
            col.bulk_write(
                [UpdateOne({"arxiv_id": r["arxiv_id"]}, {"$set": r}, upsert=True) for r in batch],
                ordered=False,
            )
        except Exception as e:
            print(f"[mongo] bulk_write failed: {e}")

        points = [
            qm.PointStruct(
                id=stable_point_id(r["arxiv_id"]),
                vector=vectors[i].tolist(),
                payload={
                    "arxiv_id": r["arxiv_id"],
                    "title": r["title"],
                    "year": r["year"],
                    "categories": r["categories"],
                },
            )
            for i, r in enumerate(batch)
        ]
        try:
            qdrant_client.upsert_points(points)
        except Exception as e:
            print(f"[qdrant] upsert failed: {e}")

        loaded += len(batch)
        pbar.update(len(batch))

    pbar.close()
    return loaded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, help="Path to arxiv-metadata JSON lines file")
    parser.add_argument("--limit", type=int, default=8000)
    parser.add_argument("--fake", type=int, default=0, help="Generate N fake articles instead")
    parser.add_argument("--force", action="store_true", help="Reload even if data already present")
    args = parser.parse_args()

    if not args.force:
        try:
            qdrant_client.ensure_collection()
            existing = qdrant_client.count_points()
            if existing > 0:
                print(f"[skip] Qdrant already has {existing} points. Use --force to reload.")
                return
        except Exception as e:
            print(f"[pre-check] could not read qdrant count ({e}), proceeding with load")

    print(f"Loading model {settings.MODEL_NAME}...")
    model = SentenceTransformer(settings.MODEL_NAME)

    if args.fake > 0 or not args.file:
        count = args.fake if args.fake > 0 else 500
        print(f"[demo mode] generating {count} fake articles")
        records = iter_fake(count)
        total_hint = count
    else:
        path = Path(args.file)
        if not path.exists():
            print(f"File not found: {path}. Falling back to 500 fake articles.")
            records = iter_fake(500)
            total_hint = 500
        else:
            records = iter_arxiv_jsonl(path, args.limit)
            total_hint = args.limit

    loaded = load(records, model, total_hint=total_hint)
    print(f"Done. Loaded {loaded} articles.")


if __name__ == "__main__":
    main()

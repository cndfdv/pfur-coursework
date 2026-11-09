"""Небольшой сохраняемый FAISS-индекс для лабораторных 3–5."""

import json
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path

import faiss
import torch
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from shared.config import EMBEDDING_MODEL
from shared.loaders import TextRecord


@dataclass
class RetrievedDocument:
    text: str
    title: str
    source: str
    url: str
    score: float


@lru_cache(maxsize=1)
def embedding_model() -> SentenceTransformer:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return SentenceTransformer(EMBEDDING_MODEL, device=device)


def records_to_chunks(records: list[TextRecord]) -> list[dict]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    documents = [
        Document(
            record.text,
            metadata={key: value for key, value in asdict(record).items() if key != "text"},
        )
        for record in records
    ]
    chunks = splitter.split_documents(documents)
    return [{"text": chunk.page_content, **chunk.metadata} for chunk in chunks]


def build_index(records: list[TextRecord], folder: Path, batch_size: int = 64) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    chunks = records_to_chunks(records)
    texts = [chunk["text"] for chunk in chunks]
    vectors = (
        embedding_model()
        .encode(
            texts,
            prompt_name="search_document",
            normalize_embeddings=True,
            batch_size=batch_size,
            show_progress_bar=True,
        )
        .astype("float32")
    )
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(folder / "index.faiss"))
    with (folder / "chunks.jsonl").open("w", encoding="utf-8") as file:
        for chunk in chunks:
            file.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    meta = {"documents": len(records), "chunks": len(chunks), "dimensions": vectors.shape[1]}
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2))
    return meta


class IndexStore:
    def __init__(self, folder: Path):
        self.index = faiss.read_index(str(folder / "index.faiss"))
        with (folder / "chunks.jsonl").open(encoding="utf-8") as file:
            self.chunks = [json.loads(line) for line in file]

    def search(self, query: str, k: int = 5) -> list[RetrievedDocument]:
        vector = (
            embedding_model()
            .encode(
                [query],
                prompt_name="search_query",
                normalize_embeddings=True,
            )
            .astype("float32")
        )
        scores, ids = self.index.search(vector, k)
        result = []
        for score, index_id in zip(scores[0], ids[0]):
            if index_id < 0:
                continue
            chunk = self.chunks[int(index_id)]
            result.append(
                RetrievedDocument(
                    text=chunk["text"],
                    title=chunk["title"],
                    source=chunk["source"],
                    url=chunk.get("url", ""),
                    score=float(score),
                )
            )
        return result

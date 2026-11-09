"""Гибридный поиск: BM25 + FAISS, объединение рангов через RRF."""

import json
import os
import re
from collections import defaultdict
from itertools import zip_longest
from pathlib import Path

import faiss
import numpy as np
import torch
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

MODEL_NAME = "deepvk/USER2-small"
RRF_WEIGHTS = {"faiss": 2.0, "bm25": 1.0}


class VKEmbeddings(Embeddings):
    """Одинаковая обработка текста здесь и в общем сохранённом индексе."""

    def __init__(self):
        self.model = SentenceTransformer(
            MODEL_NAME, device="cuda" if torch.cuda.is_available() else "cpu"
        )

    def embed_documents(self, texts):
        return self.model.encode(
            texts, prompt_name="search_document", normalize_embeddings=True, batch_size=64
        ).tolist()

    def embed_query(self, text):
        return self.model.encode([text], prompt_name="search_query", normalize_embeddings=True)[
            0
        ].tolist()


def reuse_vectors(chunks, embeddings):
    """Полный индекс из общей подготовки: сверяем каждый чанк, без pickle."""
    default = Path(__file__).resolve().parents[1] / "data" / "indexes" / "habr"
    folder = Path(os.getenv("RAG_INDEX_PATH", str(default)))
    if not all((folder / name).is_file() for name in ("meta.json", "chunks.jsonl", "index.faiss")):
        return None
    if json.loads((folder / "meta.json").read_text())["chunks"] != len(chunks):
        return None
    with (folder / "chunks.jsonl").open(encoding="utf-8") as file:
        for chunk, line in zip_longest(chunks, file):
            if chunk is None or line is None or chunk.page_content != json.loads(line)["text"]:
                return None
    index = faiss.read_index(str(folder / "index.faiss"))
    if index.ntotal != len(chunks) or index.metric_type != faiss.METRIC_INNER_PRODUCT:
        return None
    positions = sorted({0, len(chunks) // 2, len(chunks) - 1})
    probes = embeddings.embed_documents([chunks[i].page_content for i in positions])
    if index.d != len(probes[0]) or any(
        not np.allclose(index.reconstruct(i), vector, rtol=1e-3, atol=1e-5)
        for i, vector in zip(positions, probes)
    ):
        return None
    ids = {number: str(number) for number in range(len(chunks))}
    print(f"FAISS: переиспользованы проверенные векторы {len(chunks)} чанков", flush=True)
    return FAISS(
        embeddings,
        index,
        InMemoryDocstore({ids[i]: doc for i, doc in enumerate(chunks)}),
        ids,
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
    )


def tokenize(text):
    return re.findall(r"\w+", text.lower().replace("ё", "е"))


def build_indexes(chunks):
    """Построить оба индекса на одних чанках."""
    if not chunks:
        raise ValueError("Нет чанков для индексации.")
    embeddings = VKEmbeddings()
    vector_store = reuse_vectors(chunks, embeddings)
    if vector_store is None:
        vector_store = FAISS.from_documents(
            chunks, embeddings, distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT
        )
    bm25 = BM25Retriever.from_documents(chunks, preprocess_func=tokenize, k=20)
    return vector_store, bm25


def retrieve(question, vector_store, bm25, k=10):
    """RRF: семантический поиск весит 2, лексический — 1; top-k остаётся 10."""
    if not question.strip() or not tokenize(question):
        raise ValueError("Введите вопрос словами.")
    if k < 1:
        raise ValueError("k должен быть положительным.")
    dense = vector_store.similarity_search(question, k=max(20, k))
    query_tokens = set(tokenize(question))
    sparse = [
        doc
        for doc in bm25.invoke(question)
        if query_tokens.intersection(tokenize(doc.page_content))
    ]
    scores, documents = defaultdict(float), {}
    for ranking, weight in ((dense, RRF_WEIGHTS["faiss"]), (sparse, RRF_WEIGHTS["bm25"])):
        for rank, doc in enumerate(ranking, start=1):
            chunk_id = doc.metadata["chunk_id"]
            scores[chunk_id] += weight / (60 + rank)
            documents[chunk_id] = doc
    ordered = sorted(scores, key=scores.get, reverse=True)[:k]
    return [documents[key] for key in ordered]

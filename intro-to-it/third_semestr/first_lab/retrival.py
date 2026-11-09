"""Гибридный поиск: BM25 + FAISS, объединение рангов через RRF."""

import re
from collections import defaultdict

from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

MODEL_NAME = "deepvk/USER2-small"


def tokenize(text):
    return re.findall(r"\w+", text.lower().replace("ё", "е"))


def build_indexes(chunks):
    """Построить оба индекса на одних чанках. Модель работает локально на CPU."""
    if not chunks:
        raise ValueError("Нет чанков для индексации.")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True, "prompt_name": "search_document", "batch_size": 16,
        },
        query_encode_kwargs={"normalize_embeddings": True, "prompt_name": "search_query"},
    )
    vector_store = FAISS.from_documents(chunks, embeddings)
    bm25 = BM25Retriever.from_documents(chunks, preprocess_func=tokenize, k=20)
    return vector_store, bm25


def retrieve(question, vector_store, bm25, k=10):
    """Равные веса двух поисков: score = sum(1 / (60 + rank))."""
    if not question.strip() or not tokenize(question):
        raise ValueError("Введите вопрос словами.")
    if k < 1:
        raise ValueError("k должен быть положительным.")
    dense = vector_store.similarity_search(question, k=max(20, k))
    query_tokens = set(tokenize(question))
    sparse = [doc for doc in bm25.invoke(question)
            if query_tokens.intersection(tokenize(doc.page_content))]
    scores, documents = defaultdict(float), {}
    for ranking in (dense, sparse):
        for rank, doc in enumerate(ranking, start=1):
            chunk_id = doc.metadata["chunk_id"]
            scores[chunk_id] += 1 / (60 + rank)
            documents[chunk_id] = doc
    ordered = sorted(scores, key=scores.get, reverse=True)[:k]
    return [documents[key] for key in ordered]

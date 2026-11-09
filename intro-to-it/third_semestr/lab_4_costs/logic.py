"""Подготовка вопросов и измерение графа из лабораторной 3."""

import re
from time import perf_counter
from uuid import uuid4

from rapidfuzz import process, fuzz
from rapidfuzz.distance import Levenshtein

from lab_3_langgraph.graph import build_graph
from shared.costs import run_graph

WORD = re.compile(r"[A-Za-zА-Яа-яЁё]{5,}")


def correct_question(question: str, indexes: dict) -> str:
    """Исправить одну ошибку в слове по ограниченному словарю заголовков."""
    vocabulary = set()
    for index in indexes.values():
        for chunk in index.chunks[:2000]:
            vocabulary.update(word.lower() for word in WORD.findall(chunk.get("title", "")))
    vocabulary = sorted(vocabulary)[:10000]
    known = set(vocabulary)

    def replace(match):
        word = match.group()
        if word.lower() in known:
            return word
        candidate = process.extractOne(word.lower(), vocabulary, scorer=fuzz.ratio, score_cutoff=80)
        if not candidate or Levenshtein.distance(word.lower(), candidate[0]) != 1:
            return word
        corrected = candidate[0]
        if word.isupper():
            return corrected.upper()
        return corrected.capitalize() if word[0].isupper() else corrected

    return WORD.sub(replace, question)


def split_question(question: str) -> list[str]:
    """Разделить предложения и явные связки, сохранив весь текст в ≤3 частях."""
    parts = [part.strip() for part in re.split(
        r"(?<=[.!?])\s+|\s+и\s+(?=(?:как|что|почему)\b)", question, flags=re.I
    ) if part.strip()]
    return parts[:2] + [" ".join(parts[2:])] if len(parts) > 3 else parts


def run_question(question, indexes, api_key=None, document_filter=None):
    """Вернуть (результаты, измерения, исправленный текст, подзапросы)."""
    if not question.strip():
        raise ValueError("Введите непустой вопрос.")
    request_id = uuid4().hex[:12]
    started = perf_counter()
    corrected = correct_question(question.strip(), indexes)
    subquestions = split_question(corrected)
    rows = [{
        "request": request_id, "subquestion": 0, "stage": "prepare", "seconds": perf_counter() - started,
        "input_tokens": 0, "output_tokens": 0, "cached_tokens": 0, "cost_usd": 0.0,
    }]
    graph = build_graph(indexes, api_key, document_filter)
    results = []
    for number, subquestion in enumerate(subquestions, 1):
        result, measured = run_graph(graph, subquestion, request_id)
        results.append(result)
        rows.extend({**row, "subquestion": number} for row in measured)
    return results, rows, corrected, subquestions

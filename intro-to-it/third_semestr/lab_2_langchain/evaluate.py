"""Из корня: python lab_2_langchain/evaluate.py --split validation (на home)."""

import argparse
import hashlib
import json
import re
from pathlib import Path
from time import perf_counter

from chunking import find_data_path, load_documents, split_documents
from llm import MODEL_NAME as LLM_MODEL
from llm import answer_question
from retrieval import MODEL_NAME as EMBEDDING_MODEL
from retrieval import RRF_WEIGHTS, build_indexes, retrieve, tokenize

ROOT = Path(__file__).resolve().parents[1]


def source_ids(documents):
    return [document.metadata["article_id"] for document in documents]


def ranking_metrics(ids, expected):
    rank = next((i for i, article_id in enumerate(ids[:10], 1) if article_id in expected), None)
    return {
        "hit1": int(rank == 1),
        "hit5": int(rank is not None and rank <= 5),
        "hit10": int(rank is not None),
        "mrr10": 1 / rank if rank else 0.0,
    }


def summarize(results):
    facts = [result for result in results if result["kind"] == "fact"]
    return (
        {
            method: {
                metric: sum(result["metrics"][method][metric] for result in facts) / len(facts)
                for metric in ("hit1", "hit5", "hit10", "mrr10")
            }
            for method in ("bm25", "faiss", "hybrid")
        }
        if facts
        else {}
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--split", choices=("validation", "holdout", "challenge"), default="validation"
    )
    parser.add_argument("--no-generation", action="store_true")
    args = parser.parse_args()
    cases_path = Path(__file__).with_name("evaluation.json")
    cases = [case for case in json.loads(cases_path.read_text()) if case["split"] == args.split]
    output = ROOT / "data" / "lab2_quality"
    output.mkdir(parents=True, exist_ok=True)
    started = perf_counter()
    documents, stats = load_documents(limit=None)
    chunks = split_documents(documents)
    preparation_seconds = perf_counter() - started
    vectors, bm25 = build_indexes(chunks)
    metadata = {
        "llm_model": LLM_MODEL,
        "reasoning_effort": "medium",
        "embedding_model": EMBEDDING_MODEL,
        "rrf_weights": RRF_WEIGHTS,
        "top_k": 10,
        "source_file": find_data_path().name,
        "stats": stats,
        "chunks": len(chunks),
        "cases_sha256": hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        "code_sha256": {
            name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ("retrieval.py", "llm.py", "evaluate.py")
        },
        "preparation_seconds": preparation_seconds,
        "index_seconds": perf_counter() - started - preparation_seconds,
    }
    results = []
    for case in cases:
        tick = perf_counter()
        dense = vectors.similarity_search(case["question"], k=20)
        words = set(tokenize(case["question"]))
        sparse = [
            doc
            for doc in bm25.invoke(case["question"])
            if words.intersection(tokenize(doc.page_content))
        ]
        found = retrieve(case["question"], vectors, bm25, k=10)
        rankings = {
            "bm25": source_ids(sparse[:10]),
            "faiss": source_ids(dense[:10]),
            "hybrid": source_ids(found),
        }
        result = {
            **case,
            "rankings": rankings,
            "metrics": {
                method: ranking_metrics(ids, case["article_ids"])
                for method, ids in rankings.items()
            },
            "retrieval_seconds": perf_counter() - tick,
            "documents": [{"text": doc.page_content, **doc.metadata} for doc in found],
        }
        if not args.no_generation:
            tick = perf_counter()
            try:
                result["answer"] = answer_question(case["question"], found)
            except Exception as error:
                result["error"] = type(error).__name__
                result["answer"] = ""
            result["generation_seconds"] = perf_counter() - tick
            citations = [
                int(n)
                for group in re.findall(r"\[([\d,\s]+)\]", result["answer"])
                for n in re.findall(r"\d+", group)
            ]
            result["citations"] = citations
            result["citations_valid"] = bool(citations) and all(
                1 <= n <= len(found) for n in citations
            )
            result["cited_article_ids"] = [
                found[n - 1].metadata["article_id"] for n in citations if 1 <= n <= len(found)
            ]
        results.append(result)
        report = {
            "split": args.split,
            "metadata": metadata,
            "summary": summarize(results),
            "results": results,
        }
        (output / f"{args.split}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(case["id"], result["metrics"], result.get("answer", "Без генерации"), flush=True)
    print("SUMMARY", json.dumps(summarize(results), ensure_ascii=False), flush=True)
    print("REPORT", output / f"{args.split}.json", flush=True)


if __name__ == "__main__":
    main()

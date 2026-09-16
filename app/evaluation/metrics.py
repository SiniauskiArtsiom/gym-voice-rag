"""Retrieval metrics: Hit Rate@k, MRR@k, latency."""
import time
from dataclasses import dataclass, field

from app.retrieval.retriever import retrieve


@dataclass
class EvalResult:
    question: str
    expected_doc_ids: list[str]
    retrieved_doc_ids: list[str]
    hit: bool
    reciprocal_rank: float
    latency_ms: float
    category: str = ""


def hit_rate_at_k(results: list[EvalResult], k: int = 3) -> float:
    if not results:
        return 0.0
    return sum(r.hit for r in results) / len(results)


def mrr_at_k(results: list[EvalResult], k: int = 3) -> float:
    if not results:
        return 0.0
    return sum(r.reciprocal_rank for r in results) / len(results)


def avg_latency_ms(results: list[EvalResult]) -> float:
    if not results:
        return 0.0
    return sum(r.latency_ms for r in results) / len(results)


def evaluate_one(
    question: str, expected_doc_ids: list[str], k: int = 3, category: str = ""
) -> EvalResult:
    t0 = time.perf_counter()
    chunks = retrieve(question, k=k)
    latency = (time.perf_counter() - t0) * 1000

    retrieved = [c["metadata"]["doc_id"] for c in chunks]
    # unique, preserving order
    seen = set()
    retrieved_unique = []
    for d in retrieved:
        if d not in seen:
            seen.add(d)
            retrieved_unique.append(d)

    hit = any(d in expected_doc_ids for d in retrieved_unique)

    rr = 0.0
    for i, d in enumerate(retrieved_unique, start=1):
        if d in expected_doc_ids:
            rr = 1.0 / i
            break

    return EvalResult(
        question=question,
        expected_doc_ids=expected_doc_ids,
        retrieved_doc_ids=retrieved_unique,
        hit=hit,
        reciprocal_rank=rr,
        latency_ms=latency,
        category=category,
    )

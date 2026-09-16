"""Run retrieval evaluation on data/eval/questions.jsonl.

No LLM calls — only retrieval.
"""
import json
import statistics
from pathlib import Path

from app.evaluation.metrics import (
    avg_latency_ms,
    evaluate_one,
    hit_rate_at_k,
    mrr_at_k,
)

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "data" / "eval" / "questions.jsonl"
RESULTS = ROOT / "data" / "eval" / "results.json"


def main() -> None:
    with QUESTIONS.open(encoding="utf-8") as f:
        items = [json.loads(line) for line in f if line.strip()]

    print(f"Loaded {len(items)} questions\n")

    results = []
    for i, item in enumerate(items, 1):
        r = evaluate_one(
            question=item["question"],
            expected_doc_ids=item["expected_doc_ids"],
            k=3,
            category=item.get("category", ""),
        )
        results.append(r)
        mark = "✓" if r.hit else "✗"
        print(
            f"[{i:2}/{len(items)}] {mark} {r.latency_ms:6.0f}ms  {item['question'][:60]}"
        )
        print(f"           expected: {item['expected_doc_ids']}")
        print(f"           retrieved: {r.retrieved_doc_ids}")

    print("\n" + "=" * 60)
    print("METRICS")
    print("=" * 60)
    print(f"Hit Rate@3: {hit_rate_at_k(results, k=3):.3f}")
    print(f"MRR@3:      {mrr_at_k(results, k=3):.3f}")
    print(f"Avg latency: {avg_latency_ms(results):.0f} ms")
    print(f"Median latency: {statistics.median(r.latency_ms for r in results):.0f} ms")

    # per-category breakdown
    print("\nBy category:")
    cats = {}
    for r in results:
        cats.setdefault(r.category, []).append(r)
    for cat, rs in sorted(cats.items()):
        hr = hit_rate_at_k(rs, k=3)
        print(f"  {cat:12}: hit={hr:.2f}  n={len(rs)}")

    # save JSON
    payload = {
        "n": len(results),
        "hit_rate@3": round(hit_rate_at_k(results, k=3), 3),
        "mrr@3": round(mrr_at_k(results, k=3), 3),
        "avg_latency_ms": round(avg_latency_ms(results), 1),
        "median_latency_ms": round(statistics.median(r.latency_ms for r in results), 1),
        "results": [
            {
                "question": r.question,
                "expected": r.expected_doc_ids,
                "retrieved": r.retrieved_doc_ids,
                "hit": r.hit,
                "rr": round(r.reciprocal_rank, 3),
                "latency_ms": round(r.latency_ms, 1),
                "category": r.category,
            }
            for r in results
        ],
    }
    RESULTS.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved: {RESULTS}")


if __name__ == "__main__":
    main()

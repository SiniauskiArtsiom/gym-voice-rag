"""High-level retrieval interface."""
from app.retrieval.vector_store import search


def retrieve(query: str, k: int = 3) -> list[dict]:
    return search(query, k=k)


if __name__ == "__main__":
    for q in [
        "Какие упражнения на грудь без штанги?",
        "Что делать при боли в плече?",
        "Сколько белка нужно в день?",
    ]:
        print(f"\nQ: {q}")
        for r in retrieve(q, k=2):
            print(f"  [{r['distance']:.3f}] {r['metadata']['title']}: {r['text'][:120]}...")

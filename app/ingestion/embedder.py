"""Local embeddings using fastembed (ONNX Runtime, no AVX required)."""
from functools import lru_cache

from fastembed import TextEmbedding

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def _get_model() -> TextEmbedding:
    return TextEmbedding(model_name=MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return [vec.tolist() for vec in model.embed(texts)]


def embed_query(text: str) -> list[float]:
    return embed_texts([text])[0]


if __name__ == "__main__":
    vecs = embed_texts(["жим лёжа", "приседания со штангой"])
    print("n vectors:", len(vecs))
    print("dim:", len(vecs[0]))

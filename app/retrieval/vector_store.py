"""Chroma vector store wrapper."""
from pathlib import Path

import chromadb

from app.ingestion.chunkers import Chunk
from app.ingestion.embedder import embed_query, embed_texts

CHROMA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "chroma"
COLLECTION_NAME = "gym_docs"


def _client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def get_collection():
    return _client().get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def reset_collection() -> None:
    client = _client()
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )


def add_chunks(chunks: list[Chunk], batch_size: int = 32) -> int:
    collection = get_collection()
    total = 0
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        ids = [c.chunk_id for c in batch]
        documents = [c.text for c in batch]
        metadatas = [
            {"doc_id": c.doc_id, "title": c.title, "source": c.source} for c in batch
        ]
        embeddings = embed_texts(documents)
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        total += len(batch)
    return total


def search(query: str, k: int = 3) -> list[dict]:
    collection = get_collection()
    q_emb = embed_query(query)
    res = collection.query(
        query_embeddings=[q_emb],
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    out: list[dict] = []
    for i in range(len(res["ids"][0])):
        out.append(
            {
                "chunk_id": res["ids"][0][i],
                "text": res["documents"][0][i],
                "metadata": res["metadatas"][0][i],
                "distance": res["distances"][0][i],
            }
        )
    return out

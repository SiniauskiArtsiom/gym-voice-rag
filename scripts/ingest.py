"""Build the Chroma index from data/docs/."""
from app.ingestion.chunkers import chunk_documents
from app.ingestion.loaders import load_documents
from app.retrieval.vector_store import add_chunks, reset_collection


def main() -> None:
    print("Resetting collection...")
    reset_collection()

    print("Loading documents...")
    docs = load_documents()
    print(f"  {len(docs)} documents")

    print("Chunking...")
    chunks = chunk_documents(docs)
    print(f"  {len(chunks)} chunks")

    print("Embedding and indexing...")
    n = add_chunks(chunks)
    print(f"  indexed {n} chunks")


if __name__ == "__main__":
    main()

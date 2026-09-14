"""Split documents into chunks for embedding."""
from dataclasses import dataclass

from app.ingestion.loaders import Document


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str
    source: str


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    """Split by paragraphs, then pack into chunks of ~chunk_size chars."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= chunk_size:
            current = f"{current}\n\n{para}".strip()
        else:
            if current:
                chunks.append(current)
            # if single paragraph is bigger than chunk_size, hard-split
            if len(para) > chunk_size:
                for i in range(0, len(para), chunk_size - overlap):
                    chunks.append(para[i : i + chunk_size])
                current = ""
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def chunk_documents(
    documents: list[Document], chunk_size: int = 300, overlap: int = 50
) -> list[Chunk]:
    result: list[Chunk] = []
    for doc in documents:
        for idx, text in enumerate(chunk_text(doc.content, chunk_size, overlap)):
            result.append(
                Chunk(
                    chunk_id=f"{doc.doc_id}::{idx}",
                    doc_id=doc.doc_id,
                    title=doc.title,
                    text=text,
                    source=doc.source,
                )
            )
    return result


if __name__ == "__main__":
    from app.ingestion.loaders import load_documents

    docs = load_documents()
    chunks = chunk_documents(docs)
    print(f"{len(docs)} docs -> {len(chunks)} chunks")
    print("\nExample chunk:")
    print(chunks[0].chunk_id, "->", chunks[0].text[:200])

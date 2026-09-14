"""Load markdown documents from data/docs/."""
from dataclasses import dataclass
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "docs"


@dataclass
class Document:
    doc_id: str
    title: str
    content: str
    source: str


def _extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def load_documents(docs_dir: Path = DOCS_DIR) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        documents.append(
            Document(
                doc_id=path.stem,
                title=_extract_title(text, path.stem),
                content=text,
                source=path.name,
            )
        )
    return documents


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents")
    for d in docs[:3]:
        print(f"- {d.doc_id}: {d.title}")

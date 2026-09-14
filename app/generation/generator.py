"""End-to-end answer generation: RAG + graph + LLM."""
from dataclasses import dataclass

from app.generation.llm_client import chat
from app.generation.prompts import SYSTEM_PROMPT, build_user_prompt
from app.generation.router import gather_graph_facts
from app.retrieval.retriever import retrieve


@dataclass
class Answer:
    text: str
    sources: list[str]
    graph_facts: list[str]


def answer_question(question: str, k: int = 3) -> Answer:
    chunks = retrieve(question, k=k)
    facts = gather_graph_facts(question)

    user_prompt = build_user_prompt(question, chunks, facts)
    text = chat(SYSTEM_PROMPT, user_prompt, temperature=0.2, max_tokens=600)

    sources = sorted({c["metadata"]["doc_id"] for c in chunks})

    return Answer(text=text.strip(), sources=sources, graph_facts=facts)


if __name__ == "__main__":
    questions = [
        "Какие упражнения на грудь без штанги?",
        "Что делать при боли в плече?",
        "Сколько белка нужно в день?",
    ]
    for q in questions:
        print(f"\n{'=' * 60}\nQ: {q}")
        a = answer_question(q)
        print(f"A: {a.text}")
        print(f"Sources: {a.sources}")
        print(f"Graph facts used: {len(a.graph_facts)}")

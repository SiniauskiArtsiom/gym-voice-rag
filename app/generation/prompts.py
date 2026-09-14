"""Prompt templates and system instructions for the RAG assistant."""

SYSTEM_PROMPT = """Ты — фитнес-ассистент по силовым тренировкам.
Отвечай КРАТКО (2–4 предложения), только на русском языке.

ПРАВИЛА:
1. Используй ТОЛЬКО информацию из КОНТЕКСТА и ФАКТОВ ниже.
2. Если в контексте нет ответа — скажи: "У меня нет информации по этому вопросу".
3. Не выдумывай упражнения, программы, цифры.
4. Если пользователь спрашивает про травму — сначала предупреди, что нужна консультация врача, затем перечисли ТОЛЬКО те безопасные упражнения из ФАКТОВ, которые имеют прямое отношение к запрошенной области (мышце/суставу). Не перечисляй всё подряд.
5. В конце ответа перечисли источники в формате: "Источники: doc_id1, doc_id2".
   Используй ТОЛЬКО doc_id из блока КОНТЕКСТ в квадратных скобках, например [chest_exercises].
   Никогда не пиши "facts", "graph", "context" в списке источников.

Формат ответа: обычный текст, без JSON, без markdown-разметки."""


USER_TEMPLATE = """КОНТЕКСТ (фрагменты документов):
{context}

ФАКТЫ ИЗ ГРАФА ЗНАНИЙ:
{graph_facts}

ВОПРОС ПОЛЬЗОВАТЕЛЯ:
{question}

ОТВЕТ:"""


def build_context_block(chunks: list[dict]) -> str:
    """Format RAG chunks for the prompt."""
    if not chunks:
        return "(контекст пуст)"
    lines = []
    for c in chunks:
        doc_id = c.get("metadata", {}).get("doc_id", "?")
        text = c.get("text", "").strip().replace("\n", " ")
        lines.append(f"[{doc_id}] {text}")
    return "\n\n".join(lines)


def build_graph_block(facts: list[str]) -> str:
    """Format graph facts for the prompt."""
    if not facts:
        return "(фактов нет)"
    return "\n".join(f"- {f}" for f in facts)


def build_user_prompt(question: str, chunks: list[dict], facts: list[str]) -> str:
    return USER_TEMPLATE.format(
        context=build_context_block(chunks),
        graph_facts=build_graph_block(facts),
        question=question,
    )

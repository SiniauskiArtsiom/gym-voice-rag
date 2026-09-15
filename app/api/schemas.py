"""Pydantic schemas for API."""
from pydantic import BaseModel, Field


class AskTextRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[str]
    graph_facts: list[str]
    audio_path: str | None = None

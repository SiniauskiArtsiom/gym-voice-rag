from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="Gym Voice RAG Assistant",
    description="RAG + Neo4j + STT/TTS assistant for strength training",
    version="0.1.0",
)

app.include_router(router)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "model": settings.llm_model,
        "version": "0.1.0",
    }

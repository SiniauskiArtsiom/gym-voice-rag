"""API routes: text and voice questions."""
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.api.schemas import AskResponse, AskTextRequest
from app.generation.generator import answer_question
from app.speech.stt import transcribe
from app.speech.tts import synthesize
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

TMP_DIR = Path(tempfile.gettempdir()) / "gym_voice_rag"
TMP_DIR.mkdir(exist_ok=True)


def _make_audio(text: str) -> str | None:
    """Synthesize answer and return path, or None if TTS fails."""
    audio_path = TMP_DIR / f"{uuid.uuid4().hex}.mp3"
    try:
        synthesize(text, audio_path)
        return audio_path.name
    except Exception as e:
        logger.warning("TTS failed: %s", e)
        return None

@router.post("/ask_text", response_model=AskResponse)
def ask_text(payload: AskTextRequest) -> AskResponse:
    try:
        result = answer_question(payload.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return AskResponse(
        question=payload.question,
        answer=result.text,
        sources=result.sources,
        graph_facts=result.graph_facts,
        audio_path=_make_audio(result.text),
    )


@router.post("/ask_voice", response_model=AskResponse)
def ask_voice(file: UploadFile = File(...)) -> AskResponse:
    suffix = Path(file.filename or "audio.ogg").suffix or ".ogg"
    audio_in = TMP_DIR / f"{uuid.uuid4().hex}{suffix}"
    with audio_in.open("wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        question = transcribe(audio_in)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT error: {e}")
    finally:
        audio_in.unlink(missing_ok=True)

    if not question:
        raise HTTPException(status_code=400, detail="Could not transcribe audio")

    try:
        result = answer_question(question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {e}")

    return AskResponse(
        question=question,
        answer=result.text,
        sources=result.sources,
        graph_facts=result.graph_facts,
        audio_path=_make_audio(result.text),
    )


@router.get("/audio/{filename}")
def get_audio(filename: str) -> FileResponse:
    # basic path traversal guard
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    path = TMP_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(path, media_type="audio/mpeg")

"""Speech-to-Text via faster-whisper (local, no API)."""
from functools import lru_cache
from pathlib import Path

from faster_whisper import WhisperModel

from app.core.config import settings


@lru_cache(maxsize=1)
def _get_model() -> WhisperModel:
    return WhisperModel(
        settings.whisper_model,
        device=settings.whisper_device,
        compute_type=settings.whisper_compute_type,
    )


def transcribe(audio_path: str | Path, language: str = "ru") -> str:
    model = _get_model()
    segments, _info = model.transcribe(str(audio_path), language=language)
    return " ".join(seg.text.strip() for seg in segments).strip()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python -m app.speech.stt <audio_file>")
        sys.exit(1)
    print(transcribe(sys.argv[1]))

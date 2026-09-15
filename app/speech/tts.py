"""Text-to-Speech via edge-tts (local, no API)."""
import asyncio
from pathlib import Path

import edge_tts

DEFAULT_VOICE = "ru-RU-DmitryNeural"


async def _synthesize(text: str, output_path: str, voice: str) -> None:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


def synthesize(text: str, output_path: str | Path, voice: str = DEFAULT_VOICE) -> str:
    output_path = str(output_path)
    asyncio.run(_synthesize(text, output_path, voice))
    return output_path


if __name__ == "__main__":
    out = synthesize("Привет! Это тест синтеза речи.", "/tmp/test_tts.mp3")
    print("Saved:", out)
    Path(out).exists() and print("Size:", Path(out).stat().st_size, "bytes")

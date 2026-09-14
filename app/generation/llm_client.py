"""LLM client via OpenRouter with fallback across free models."""
import logging

from openai import OpenAI
from openai import APIStatusError, RateLimitError

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: OpenAI | None = None

# Fallback chain: primary from .env, then these.
FALLBACK_MODELS = [
    # instruct-модели (без thinking)
    "google/gemma-4-31b-it:free",
    "thinkingmachines/inkling:free",
    # reasoning-модели (с отключённым reasoning)
    "nvidia/nemotron-3-super-120b-a12b:free",
    "nex-agi/nex-n2.5-pro:free",
    # запасные
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3.5-lightning:free",
]


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
    return _client


def _try_model(model: str, system_prompt: str, user_prompt: str,
               temperature: float, max_tokens: int) -> str | None:
    """Try a single model. Returns text or None on rate limit / error."""
    client = get_client()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        choice = response.choices[0]
        finish = choice.finish_reason
        text = (choice.message.content or "").strip()
        logger.info("Model %s answered (finish_reason=%s, len=%d)", model, finish, len(text))
        if not text:
            logger.warning("Model %s returned empty text, trying next", model)
            return None
        return text
    except RateLimitError as e:
        logger.warning("Model %s rate-limited: %s", model, e)
        return None
    except APIStatusError as e:
        logger.warning("Model %s failed with status %s", model, e.status_code)
        return None
    except Exception as e:
        logger.warning("Model %s unexpected error: %s", model, e)
        return None


def chat(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.2,
    max_tokens: int = 600,
) -> str:
    """Try primary model, fall back to alternatives if it fails."""
    models = [settings.llm_model] + [
        m for m in FALLBACK_MODELS if m != settings.llm_model
    ]

    last_error: Exception | None = None
    for model in models:
        text = _try_model(model, system_prompt, user_prompt, temperature, max_tokens)
        if text is not None:
            if model != settings.llm_model:
                logger.info("Used fallback model: %s", model)
            return text

    raise RuntimeError(
        f"All models failed. Tried: {models}. Last error: {last_error}"
    )


if __name__ == "__main__":
    result = chat(
        system_prompt="Ты краткий ассистент. Отвечай одной строкой на русском.",
        user_prompt="Скажи 'привет' по-русски.",
    )
    print("LLM response:", result)

FROM python:3.12-slim

# System deps: ffmpeg для faster-whisper, curl для healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка зависимостей отдельным слоем (кэш)
COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        "fastapi>=0.115" \
        "uvicorn[standard]>=0.32" \
        "pydantic>=2.9" \
        "pydantic-settings>=2.6" \
        "python-dotenv>=1.0" \
        "chromadb>=0.5" \
        "openai>=1.50" \
        "neo4j>=5.25" \
        "python-multipart>=0.0.12" \
        "httpx>=0.27" \
        "edge-tts>=6.1" \
        "faster-whisper>=1.0" \
        "fastembed>=0.4"

# Копируем код
COPY app ./app
COPY scripts ./scripts

# Порт
EXPOSE 8000

# Запуск
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

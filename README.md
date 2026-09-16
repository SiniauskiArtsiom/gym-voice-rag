# Gym Voice RAG Assistant

[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**Голосовой RAG-ассистент по силовым тренировкам.** Telegram-бот принимает голосовое сообщение, распознаёт вопрос, ищет ответ в базе знаний (RAG + граф знаний), генерирует ответ через LLM и возвращает его **голосом**.

## Demo

> *Отправьте боту голосовое: «Какие упражнения на грудь без штанги?»*
> *Получите ответ: аудио + цитаты из источников.*

![demo](docs/demo.gif)

## Features

- 🎙 **Голосовой ввод** — faster-whisper (локально, без API)
- 🔊 **Голосовой вывод** — edge-tts (локально, без API)
- 📚 **RAG** — Chroma + fastembed (ONNX, работает без AVX)
- 🕸 **Граф знаний** — Neo4j: 25 упражнений, 15 мышц, 8 типов оборудования, 4 травмы, 3 программы
- 🤖 **LLM** — OpenRouter с fallback-цепочкой (4+ бесплатных моделей)
- 🌐 **FastAPI** — REST + webhook-ready
- 🔗 **n8n** — оркестрация Telegram workflow
- 🐳 **Docker Compose** — весь стек одной командой
- ✅ **Метрики качества** — Hit Rate@3 = 0.90, MRR@3 = 0.87

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│  Telegram   │────▶│   n8n    │────▶│   FastAPI   │
│  (voice)    │◀────│ workflow │◀────│   /ask_voice│
└─────────────┘     └──────────┘     └──────┬──────┘
                                             │
                    ┌────────────────────────┼────────────────────────┐
                    ▼                        ▼                        ▼
              ┌──────────┐            ┌──────────┐            ┌──────────┐
              │  STT     │            │  RAG     │            │  Graph   │
              │ (whisper)│            │ (Chroma) │            │ (Neo4j)  │
              └──────────┘            └────┬─────┘            └────┬─────┘
                                           │                       │
                                           ▼                       ▼
                                     ┌──────────────────────────────────┐
                                     │         LLM (OpenRouter)         │
                                     │   fallback across free models    │
                                     └──────────────┬───────────────────┘
                                                    ▼
                                              ┌──────────┐
                                              │   TTS    │
                                              │(edge-tts)│
                                              └──────────┘
```

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI, Pydantic, Uvicorn |
| LLM | OpenRouter (OpenAI-compatible), fallback chain |
| RAG | fastembed (ONNX Runtime), Chroma |
| Graph | Neo4j 5 |
| STT | faster-whisper (tiny, CPU) |
| TTS | edge-tts |
| Orchestration | n8n |
| Deploy | Docker Compose |
| Testing | pytest, ruff |

## Evaluation

**Retrieval** on 20 questions (`data/eval/questions.jsonl`):

| Metric | Value |
|---|---|
| Hit Rate@3 | **0.900** |
| MRR@3 | **0.867** |
| Median latency | **81 ms** |
| Cold start | 4.6 s |

**Generation quality** — manual review on 5 questions:

| Metric | Value |
|---|---|
| Mean score (1–5) | **4.2** |

Full results: [`data/eval/results.json`](data/eval/results.json), [`data/eval/manual_review.md`](data/eval/manual_review.md).

## Quickstart

### Prerequisites

- Docker + Docker Compose
- Python 3.12 (для локальной разработки)
- OpenRouter API key ([openrouter.ai](https://openrouter.ai)) — бесплатно

### Setup

```bash
# 1. Clone
git clone https://github.com/SiniauskiArtsiom/gym-voice-rag.git
cd gym-voice-rag

# 2. Environment
cp .env.example .env
# Заполни LLM_API_KEY (OpenRouter) и WEBHOOK_URL (туннель)
nano .env

# 3. Start all services
docker compose up -d

# 4. Seed database (один раз)
docker compose exec fastapi python scripts/seed_graph.py
docker compose exec fastapi python scripts/ingest.py
```

FastAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
Neo4j Browser: [http://localhost:7474](http://localhost:7474)
n8n: [http://localhost:5678](http://localhost:5678)

### Test the API

```bash
# Text
curl -X POST http://localhost:8000/ask_text \
  -H "Content-Type: application/json" \
  -d '{"question": "Что входит в программу 5x5?"}' | jq

# Voice
curl -X POST http://localhost:8000/ask_voice \
  -F "file=@question.mp3" | jq
```

## Project Structure

```
.
├── app/
│   ├── api/              # FastAPI routes + schemas
│   ├── core/             # Config (pydantic-settings)
│   ├── evaluation/       # Hit Rate, MRR, latency
│   ├── generation/       # LLM client, prompts, router, generator
│   ├── graph/            # Neo4j client + Cypher queries
│   ├── ingestion/        # Loaders, chunkers, embedder
│   ├── retrieval/        # Chroma vector store + retriever
│   ├── speech/           # STT (faster-whisper), TTS (edge-tts)
│   └── main.py
├── data/
│   ├── docs/             # 18 knowledge base documents
│   ├── eval/             # Questions + results + manual review
│   ├── chroma/           # Vector index (gitignored)
│   └── neo4j/            # Graph storage (gitignored)
├── n8n/                  # Exported n8n workflow
├── scripts/              # seed_docs, seed_graph, ingest, run_eval
├── docker/
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## How it works

1. **Telegram voice** → webhook → n8n
2. n8n **downloads file** via Telegram API → POST to `/ask_voice`
3. FastAPI **transcribes** via faster-whisper → Russian question
4. **RAG** retrieves top-3 relevant chunks from Chroma
5. **Graph** extracts facts from Neo4j based on keyword router
6. **LLM** generates answer from context + facts (with fallback chain)
7. **TTS** synthesizes audio via edge-tts
8. n8n **sends audio** back to Telegram

## Known limitations

- **2/20 retrieval failures**: `equipment_barbell` и substitution queries — fix: cross-encoder reranker.
- **Thinking leakage** occasionally from reasoning models — mitigated by marker filter.
- **Faster-whisper tiny** has medium Russian accuracy — switch to `base` or `small` in `.env`.
- **Free LLM models** on OpenRouter are rate-limited (429) — mitigated by fallback chain.

## Roadmap

- [ ] Cross-encoder reranker (BAAI/bge-reranker)
- [ ] Query rewriting via LLM
- [ ] Neo4j → vector hybrid retrieval (GraphRAG)
- [ ] SQLite/Postgres for query logs
- [ ] Prometheus metrics + Grafana dashboard
- [ ] Multi-language support (EN/BY)

## License

MIT

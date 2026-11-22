
# Semantic Cache Assistant

A customer-support assistant that uses semantic caching to reduce redundant LLM calls, improve response latency, and optimize inference costs.

## Overview

Semantic Cache Assistant is a Python-based application designed to identify semantically similar user queries and reuse previously generated responses instead of invoking an LLM for every request.

When a user submits a query:

1. Generate an embedding for the incoming query.
2. Search Redis for semantically similar cached queries.
3. Return the cached response if a sufficiently similar match is found.
4. If no suitable match exists, invoke the Groq LLM.
5. Return the generated response and store it in the semantic cache.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | Streamlit |
| Cache | Redis Stack, RedisVL |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM Provider | Groq |
| Environment Management | uv |
| Testing | Pytest, HTTPX |
| Code Quality | Ruff |
| Infrastructure | Docker Compose |

## Architecture

```text
                 User
                   |
                   v
          Streamlit Frontend
                   |
                   v
             FastAPI Backend
                   |
                   v
          Embedding Generation
                   |
                   v
          Redis Semantic Cache
                   |
             +-----+-----+
             |           |
          Cache Hit   Cache Miss
             |           |
             v           v
        Cached Answer  Groq LLM
             |           |
             |       Store Response
             |           |
             +-----+-----+
                   |
                   v
              User Response
```

## Project Structure

```text
semantic-cache-assistant/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── dependencies/
│   │   ├── schemas/
│   │   └── services/
│   │
│   └── tests/
│
├── frontend/
│   ├── components/
│   └── utils/
│
├── data/
├── scripts/
├── results/
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

## Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.13
- uv
- Docker Desktop
- Groq API key

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd semantic-cache-assistant
```

### 2. Install Dependencies

```bash
uv sync --dev
```

### 3. Configure Environment Variables

Create your local environment file:

```bash
cp .env.example .env
```

Add your Groq API key to the `.env` file.

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your actual `.env` file or API keys to GitHub.

### 4. Start Redis

Start the Redis Stack container using Docker Compose:

```bash
docker compose up -d
```

Verify that Redis is running:

```bash
docker exec -it semantic-cache-redis redis-cli ping
```

Expected output:

```text
PONG
```

## Evaluation Metrics

The project will include an evaluation framework to measure:

- Cache hit rate
- Cache miss rate
- Semantic match accuracy
- False positive rate
- Cache lookup latency
- LLM response latency
- Overall response latency
- Reduction in LLM calls

Benchmark results will be documented after implementation and testing.

## Development Roadmap

- [x] Initialize project structure
- [x] Configure Python environment using uv
- [x] Install application and development dependencies
- [x] Configure Redis Stack using Docker Compose
- [x] Verify Redis vector search module
- [x] Implement application configuration
- [ ] Implement shared application resources
- [ ] Build FastAPI backend
- [ ] Implement Redis semantic cache
- [ ] Integrate Groq LLM fallback
- [ ] Build Streamlit frontend
- [ ] Implement cache evaluation framework
- [ ] Run performance benchmarks
- [ ] Add automated tests
- [ ] Complete Docker and deployment configuration

## License

This project is licensed under the MIT License.

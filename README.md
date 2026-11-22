
# Semantic Cache Assistant

A customer-support AI assistant that uses semantic caching to reduce redundant LLM API calls, improve response latency, and optimize inference costs.

The project demonstrates how vector embeddings, Redis vector search, and LLM integration can work together to build a cost-efficient AI application.

## Overview

Semantic Cache Assistant identifies semantically similar user queries and reuses previously generated responses instead of invoking an LLM for every request.

### How It Works

1. Generate an embedding for the incoming query.
2. Search Redis for semantically similar cached queries.
3. Return the cached response if a sufficiently similar match is found.
4. If no suitable match exists, invoke the Groq LLM.
5. Store the newly generated response in the semantic cache.
6. Return the response to the user.

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI, Uvicorn |
| Frontend | Streamlit |
| Cache | Redis Stack, RedisVL |
| Embeddings | Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| LLM Provider | Groq |
| LLM Model | openai/gpt-oss-120b |
| Environment Management | uv |
| Testing | Pytest, HTTPX |
| Code Quality | Ruff |
| Data Analysis | pandas |
| Infrastructure | Docker, Docker Compose |

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
              Generate Embedding
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
                |      Generate Answer
                |           |
                |      Store in Redis
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
│   │   │       ├── health.py
│   │   │       └── chat.py
│   │   │
│   │   ├── core/
│   │   │   └── config.py
│   │   │
│   │   ├── dependencies/
│   │   │   └── resources.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── health.py
│   │   │   └── chat.py
│   │   │
│   │   ├── services/
│   │   │   ├── semantic_cache.py
│   │   │   ├── vectorizer.py
│   │   │   ├── llm.py
│   │   │   └── chat.py
│   │   │
│   │   └── main.py
│   │
│   └── tests/
│       ├── test_health.py
│       └── test_chat.py
│
├── frontend/
├── data/
├── scripts/
├── results/
│
├── .env.example
├── .gitignore
├── .python-version
├── docker-compose.yml
├── pyproject.toml
├── uv.lock
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.13
- uv
- Docker Desktop
- Groq API key

### 1. Clone the Repository

```bash
git clone https://github.com/siddhantjain603/semantic-cache-assistant.git
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

Add your Groq API key to `.env`:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your actual `.env` file or API keys to GitHub.

### 4. Start Redis

```bash
docker compose up -d
```

Verify Redis:

```bash
docker exec -it semantic-cache-redis redis-cli ping
```

Expected output:

```text
PONG
```

### 5. Start the Backend

```bash
uv run uvicorn backend.app.main:app --reload
```

The backend runs at:

`http://127.0.0.1:8000`

Swagger API documentation:

`http://127.0.0.1:8000/docs`

### 6. Run Tests

```bash
uv run python -m pytest -v
```

Run code-quality checks:

```bash
uv run ruff check .
```

## API Endpoints

| Method | Endpoint | Description | Status |
|---|---|---|---|
| GET | `/health` | Application and dependency health check | Implemented |
| POST | `/chat` | Submit a question and retrieve a cached or generated answer | Implemented |
| GET | `/cache/stats` | Retrieve cache statistics | Planned |
| GET | `/cache/entries` | Inspect cached entries | Planned |
| DELETE | `/cache` | Clear cached responses | Planned |

## Current Implementation Status

### Completed — Milestone 1: Backend Foundation

- [x] Initialize project structure.
- [x] Configure Python environment using uv.
- [x] Install application and development dependencies.
- [x] Configure Redis Stack using Docker Compose.
- [x] Verify Redis vector search module.
- [x] Implement application configuration.
- [x] Implement shared Redis and embedding resources.
- [x] Initialize FastAPI application and lifespan management.
- [x] Implement health endpoint.
- [x] Implement RedisVL semantic cache.
- [x] Integrate Sentence Transformer embeddings.
- [x] Integrate Groq LLM fallback.
- [x] Implement lazy LLM client initialization.
- [x] Implement ChatService orchestration.
- [x] Implement chat request and response schemas.
- [x] Implement POST `/chat`.
- [x] Add automated health and chat API tests.
- [x] Verify exact-match cache hits.
- [x] Verify semantic cache hits using paraphrased queries.
- [x] Verify cache misses and LLM fallback through the live API.
- [x] Push completed milestone to GitHub.

**Current baseline:** 5 automated tests passing; Ruff checks passing.

Latest milestone commit:

`192055f` — `feat: add chat API with semantic cache and Groq integration`

## Development Roadmap

This is the project's master execution plan. All milestones should be completed in sequence unless a documented engineering dependency requires a change.

### Milestone 1 — Backend Foundation

**Status: COMPLETED**

Implemented the backend, Redis semantic cache, Groq integration, chat endpoint, health endpoint, and initial automated tests.

### Milestone 2 — Cache Management and Analytics

**Status: NEXT**

- [ ] Inspect RedisVL cache management and inspection APIs.
- [ ] Design application-level cache statistics.
- [ ] Track total requests.
- [ ] Track cache hits and cache misses.
- [ ] Calculate cache hit rate and miss rate.
- [ ] Track LLM API calls and calls avoided.
- [ ] Measure request and cache lookup latency.
- [ ] Implement cache statistics endpoint.
- [ ] Implement cached-entry inspection endpoint.
- [ ] Implement clear-cache endpoint.
- [ ] Handle cache expiration and TTL configuration.
- [ ] Add automated tests for cache management APIs.

### Milestone 3 — Testing and Reliability

**Status: PLANNED**

- [ ] Add unit tests for ChatService.
- [ ] Test semantic cache hit behavior.
- [ ] Test semantic cache miss behavior.
- [ ] Test LLM fallback and response storage.
- [ ] Test lazy LLM initialization.
- [ ] Test Groq API failures and timeouts.
- [ ] Test Redis connection failures.
- [ ] Test invalid requests and edge cases.
- [ ] Add integration tests for Redis and the complete request pipeline.
- [ ] Evaluate concurrent requests and race conditions.
- [ ] Improve error handling and application reliability.

### Milestone 4 — Evaluation and Benchmarking

**Status: PLANNED**

- [ ] Design a representative query evaluation dataset.
- [ ] Include exact-match queries.
- [ ] Include semantically similar queries.
- [ ] Include unrelated queries.
- [ ] Evaluate different cosine-distance thresholds.
- [ ] Measure cache hit rate and miss rate.
- [ ] Measure false-positive and false-negative rates.
- [ ] Measure semantic matching accuracy.
- [ ] Compare cache-hit and cache-miss latency.
- [ ] Measure average LLM response latency.
- [ ] Estimate LLM API calls avoided.
- [ ] Estimate cost savings.
- [ ] Generate benchmark reports and visualizations.
- [ ] Document threshold selection and trade-offs.

### Milestone 5 — Streamlit Frontend

**Status: PLANNED**

- [ ] Build the main Streamlit application.
- [ ] Implement an interactive chat interface.
- [ ] Connect the frontend to the FastAPI backend.
- [ ] Display cache-hit and cache-miss status.
- [ ] Display matched questions and semantic distance.
- [ ] Build a cache statistics dashboard.
- [ ] Add cache management controls.
- [ ] Build evaluation and benchmarking visualizations.
- [ ] Add suitable configuration controls.
- [ ] Improve UI usability and error handling.

### Milestone 6 — Production Engineering and Deployment

**Status: PLANNED**

- [ ] Complete Docker Compose configuration.
- [ ] Containerize the FastAPI backend.
- [ ] Containerize the Streamlit frontend.
- [ ] Configure Redis persistence.
- [ ] Add service health checks.
- [ ] Improve environment-based configuration.
- [ ] Add structured logging.
- [ ] Add monitoring and operational metrics.
- [ ] Implement API security and rate limiting.
- [ ] Add GitHub Actions CI pipeline.
- [ ] Validate deployment configuration.
- [ ] Perform end-to-end deployment testing.

### Milestone 7 — Documentation and Final Release

**Status: PLANNED**

- [ ] Create a complete system architecture diagram.
- [ ] Document application design and request lifecycle.
- [ ] Document API endpoints and schemas.
- [ ] Document configuration and setup instructions.
- [ ] Document benchmark methodology and results.
- [ ] Document design decisions and trade-offs.
- [ ] Add frontend screenshots.
- [ ] Add a project demonstration.
- [ ] Perform final end-to-end verification.
- [ ] Update README with final implementation details.
- [ ] Publish a tagged GitHub release.

## Evaluation Metrics

The project will measure:

| Metric | Purpose |
|---|---|
| Cache hit rate | Percentage of requests served from cache |
| Cache miss rate | Percentage of requests requiring fallback |
| Semantic match accuracy | Correctness of semantic retrieval |
| False-positive rate | Incorrect cache matches |
| False-negative rate | Relevant matches missed by the cache |
| Cache lookup latency | Time spent searching Redis |
| LLM response latency | Time spent generating a new response |
| Overall response latency | End-to-end request time |
| LLM calls avoided | Reduction in external LLM requests |
| Estimated cost savings | Financial impact of caching |

Benchmark results will be added after the evaluation framework is implemented.

## Development Principles

To maintain engineering quality and avoid drifting from the project plan:

1. Complete milestones in the documented sequence.
2. Work incrementally and verify each implementation step.
3. Add automated tests for new functionality.
4. Run Ruff and the complete test suite before milestone completion.
5. Document important architectural decisions and trade-offs.
6. Commit and push completed milestones to GitHub.
7. Never mark a feature complete without testing it.
8. Keep benchmark claims backed by measured results rather than assumptions.

## License

This project is licensed under the MIT License.

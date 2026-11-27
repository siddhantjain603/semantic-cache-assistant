# Architecture — Semantic Cache Assistant

**Live:** https://semantic-cache-assistant.streamlit.app

## Portfolio Mode (Live)

User -> Streamlit App (`app.py` + `pages/1_Semantic_Cache.py`)
  -> `core/cache.py` (SemanticCacheService)
    -> In-Memory Store (list of entries + embeddings)
    -> `sentence-transformers/all-MiniLM-L6-v2` (384-dim embeddings)
  -> On HIT: return cached answer, no LLM call
  -> On MISS: `core/llm.py` -> Groq `openai/gpt-oss-120b`
    -> Save Q + A + embedding to cache

## Production Mode (FastAPI + Redis)

User -> FastAPI (`backend/app/main.py`, `/ask`, `/health`, `/metrics`)
  -> `SemanticCacheService` (`backend/app/services/semantic_cache.py`)
    -> Redis Stack (RedisVL, vector search)
    -> `all-MiniLM-L6-v2` embeddings
  -> On HIT: return cached answer
  -> On MISS: Groq LLM -> cache result

## Key Decisions

- Threshold: `CACHE_DISTANCE_THRESHOLD = 0.25`
  (Precision 0.83 / Recall 0.83 / F1 0.83 on hard-negative eval)
- Distance: cosine distance, lower = more similar
- HIT = distance <= 0.25, MISS = distance > 0.25
- Free stack: Groq Free Tier + Streamlit Cloud Free + Local embeddings
- Note: Hugging Face Spaces deploy attempted (`sidj231405/semantic-cache-assistant`), blocked by `403: cpu-basic quota limit`. Live deploy is Streamlit Cloud with identical code.
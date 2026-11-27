# backend/app/services/semantic_cache.py
import numpy as np
from redis.exceptions import RedisError
from redisvl.extensions.cache.llm import SemanticCache

from backend.app.core.exceptions import ServiceUnavailableError
from backend.app.dependencies.resources import resources
from backend.app.services.vectorizer import SharedEmbeddingVectorizer


class SemanticCacheService:
    def __init__(self):
        self.settings = resources.settings
        self.cache = None
        self.use_redis = True
        # In-memory fallback for HF Spaces (no Redis)
        self._mem_prompts = []
        self._mem_responses = []
        self._mem_vectors = []

    def initialize(self):
        try:
            vectorizer = SharedEmbeddingVectorizer(
                model=self.settings.EMBEDDING_MODEL,
                dims=self.settings.EMBEDDING_DIMENSION,
            )
            self.cache = SemanticCache(
                name=self.settings.CACHE_NAME,
                distance_threshold=self.settings.CACHE_DISTANCE_THRESHOLD,
                ttl=self.settings.CACHE_TTL,
                vectorizer=vectorizer,
                redis_client=resources.redis_client,
                overwrite=False,
                create_index=True,
            )
            self.use_redis = True
            print("Semantic cache initialized (Redis).")
        except (RedisError, ValueError, RuntimeError) as e:
            # HF Spaces: no Redis -> fall back to in-memory
            print(f"Redis unavailable ({e}), using in-memory cache.")
            self.cache = None
            self.use_redis = False
            print(f"Redis unavailable, using in-memory cache: {e}")

    def _embed(self, question: str):
        return np.array(resources.embedding_model.encode(question), dtype=np.float32)

    @staticmethod
    def _cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
        # RedisVL uses cosine distance = 1 - cosine_similarity
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-8
        return float(1.0 - (np.dot(a, b) / denom))

    def store(self, question: str, answer: str) -> str:
        embedding = self._embed(question)

        if self.use_redis:
            if self.cache is None:
                raise ServiceUnavailableError("Semantic cache is not initialized.")
            return self.cache.store(prompt=question, response=answer, vector=embedding.tolist())

        # In-memory path
        self._mem_prompts.append(question)
        self._mem_responses.append(answer)
        self._mem_vectors.append(embedding)
        return f"mem:{len(self._mem_prompts)-1}"

    def search(self, question: str, threshold: float | None = None) -> list:
        """Now supports runtime threshold override for Streamlit slider."""
        thresh = threshold if threshold is not None else self.settings.CACHE_DISTANCE_THRESHOLD
        embedding = self._embed(question)

        if self.use_redis:
            if self.cache is None:
                raise ServiceUnavailableError("Semantic cache is not initialized.")
            return self.cache.check(
                vector=embedding.tolist(),
                num_results=1,
                distance_threshold=thresh,
            )

        # In-memory path
        if not self._mem_vectors:
            return []
        dists = [self._cosine_distance(embedding, v) for v in self._mem_vectors]
        best_idx = int(np.argmin(dists))
        if dists[best_idx] <= thresh:
            return [{
                "prompt": self._mem_prompts[best_idx],
                "response": self._mem_responses[best_idx],
                "distance": dists[best_idx],
            }]
        return []

    def clear(self) -> int:
        """Needed for frontend Clear Cache button."""
        if self.use_redis:
            # RedisVL: flush the index
            self.cache.clear()
            return -1  # RedisVL doesn't return count
        count = len(self._mem_prompts)
        self._mem_prompts.clear()
        self._mem_responses.clear()
        self._mem_vectors.clear()
        return count

    def get_entries(self, offset: int = 0, limit: int = 20) -> dict:
        if self.use_redis:
            if self.cache is None:
                raise ServiceUnavailableError("Semantic cache is not initialized.")
            from redisvl.query import FilterQuery
            query = FilterQuery("*").return_fields("prompt", "response", "inserted_at", "updated_at")
            query.paging(offset=offset, num=limit)
            results = self.cache._index.query(query)  # Keep for now, but isolated here
            total = self.cache._index.info()["num_docs"]
            entries = [{
                "id": r["id"],
                "question": r["prompt"],
                "answer": r["response"],
                "inserted_at": float(r["inserted_at"]),
                "updated_at": float(r["updated_at"]),
            } for r in results]
            return {"entries": entries, "total_entries": total, "returned_entries": len(entries), "offset": offset, "limit": limit}

        # In-memory path
        sliced = list(zip(self._mem_prompts, self._mem_responses))[offset:offset+limit]
        entries = [{"id": f"mem:{offset+i}", "question": q, "answer": a, "inserted_at": 0.0, "updated_at": 0.0} for i, (q, a) in enumerate(sliced)]
        return {"entries": entries, "total_entries": len(self._mem_prompts), "returned_entries": len(entries), "offset": offset, "limit": limit}
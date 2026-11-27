# core/cache.py - Portfolio version (Hugging Face Spaces - 100% Free)
# Same logic as backend/app/services/semantic_cache.py, but no FastAPI / no Redis.
# Uses in-memory NumPy search so it runs on HF Spaces Free Tier.
# Threshold default 0.25 - proven by scripts/evaluate_threshold.py (F1 0.83)

import numpy as np
from sentence_transformers import SentenceTransformer


class PortfolioSemanticCache:
    def __init__(self, threshold: float = 0.25):
        self.threshold = threshold
        self.questions: list[str] = []
        self.answers: list[str] = []
        self.embeddings: list[np.ndarray] = []
        self.hits = 0
        self.misses = 0
        self.llm_calls = 0
        print("Loading embedding model...")
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        print("Portfolio cache initialized (in-memory).")

    def _distance(self, a: np.ndarray, b: np.ndarray) -> float:
        # Cosine distance: 1 - cosine similarity. 0 = identical, 2 = opposite
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1.0
        return float(1.0 - float(np.dot(a, b) / denom))

    def lookup(self, question: str):
        """Returns (answer, matched_question, distance, cache_hit)."""
        if not self.questions:
            return None, None, None, False
        emb = self.model.encode([question])[0]
        best_idx = -1
        best_dist = float("inf")
        for i, stored in enumerate(self.embeddings):
            d = self._distance(emb, stored)
            if d < best_dist:
                best_dist = d
                best_idx = i
        if best_idx >= 0 and best_dist <= self.threshold:
            self.hits += 1
            return self.answers[best_idx], self.questions[best_idx], best_dist, True
        self.misses += 1
        return None, None, best_dist, False

    def store(self, question: str, answer: str):
        emb = self.model.encode([question])[0]
        self.questions.append(question)
        self.answers.append(answer)
        self.embeddings.append(emb)

    def clear(self):
        self.questions.clear()
        self.answers.clear()
        self.embeddings.clear()
        self.hits = 0
        self.misses = 0
        self.llm_calls = 0

    @property
    def stats(self):
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total else 0.0
        return {
            "total_requests": total,
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "llm_calls": self.llm_calls,
            "hit_rate": round(hit_rate, 1),
            "entries": len(self.questions),
        }

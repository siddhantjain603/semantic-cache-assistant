import time
from typing import Any

from backend.app.services.analytics import AnalyticsService
from backend.app.services.llm import LLMService
from backend.app.services.semantic_cache import SemanticCacheService


class ChatService:
    def __init__(self):
        self.semantic_cache = SemanticCacheService()
        self.llm = LLMService()
        self.analytics = AnalyticsService()

    def initialize(self):
        self.semantic_cache.initialize()

        print("Chat service initialized.")

    
    def ask(self, question: str) -> dict[str, Any]:
        start_time = time.perf_counter()

        # Step 1: Search semantic cache
        cached_results = self.semantic_cache.search(question)

        # Step 2: Return cached answer if found
        if cached_results:
            result = cached_results[0]
            cache_hit = True

            response = {
                "answer": result["response"],
                "cache_hit": True,
                "matched_question": result["prompt"],
                "distance": result["vector_distance"],
            }

        else:
            # Step 3: Generate answer using Groq
            answer = self.llm.generate_response(question)

            # Step 4: Store generated answer in semantic cache
            self.semantic_cache.store(question, answer)

            cache_hit = False

            response = {
                "answer": answer,
                "cache_hit": False,
                "matched_question": None,
                "distance": None,
            }

        # Step 5: Calculate request latency
        latency_ms = (time.perf_counter() - start_time) * 1000

        # Step 6: Record analytics
        self.analytics.record_request(
            cache_hit=cache_hit,
            latency_ms=latency_ms,
        )

        return response

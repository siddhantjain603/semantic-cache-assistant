
from typing import Any

from backend.app.services.llm import LLMService
from backend.app.services.semantic_cache import SemanticCacheService


class ChatService:
    def __init__(self):
        self.semantic_cache = SemanticCacheService()
        self.llm = LLMService()

    def initialize(self):
        self.semantic_cache.initialize()

        print("Chat service initialized.")

    def ask(self, question: str) -> dict[str, Any]:
        # Step 1: Search semantic cache
        cached_results = self.semantic_cache.search(question)

        # Step 2: Return cached answer if found
        if cached_results:
            result = cached_results[0]

            return {
                "answer": result["response"],
                "cache_hit": True,
                "matched_question": result["prompt"],
                "distance": result["vector_distance"],
            }

        # Step 3: Generate answer using Groq
        answer = self.llm.generate_response(question)

        # Step 4: Store generated answer in semantic cache
        self.semantic_cache.store(question, answer)

        # Step 5: Return generated answer
        return {
            "answer": answer,
            "cache_hit": False,
            "matched_question": None,
            "distance": None,
        }

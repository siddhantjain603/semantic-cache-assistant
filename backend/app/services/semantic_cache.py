from redisvl.extensions.cache.llm import SemanticCache

from backend.app.dependencies.resources import resources
from backend.app.services.vectorizer import SharedEmbeddingVectorizer


class SemanticCacheService:
    def __init__(self):
        self.settings = resources.settings
        self.cache = None

    def initialize(self):
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

        print("Semantic cache initialized.")

    def store(self, question: str, answer: str) -> str:
        if self.cache is None:
            raise RuntimeError("Semantic cache is not initialized.")

        embedding = resources.embedding_model.encode(question).tolist()

        cache_key = self.cache.store(
            prompt=question,
            response=answer,
            vector=embedding,
        )

        return cache_key

    def search(self, question: str) -> list:
        if self.cache is None:
            raise RuntimeError("Semantic cache is not initialized.")

        embedding = resources.embedding_model.encode(question).tolist()

        results = self.cache.check(
            vector=embedding,
            num_results=1,
            distance_threshold=self.settings.CACHE_DISTANCE_THRESHOLD,
        )

        return results
    
    def get_entries(self, offset: int = 0, limit: int = 20) -> dict:
        if self.cache is None:
            raise RuntimeError("Semantic cache is not initialized.")

        from redisvl.query import FilterQuery

        query = FilterQuery("*").return_fields(
            "prompt",
            "response",
            "inserted_at",
            "updated_at",
        )

        query.paging(offset=offset, num=limit)

        results = self.cache._index.query(query)

        entries = [
            {
                "id": result["id"],
                "question": result["prompt"],
                "answer": result["response"],
                "inserted_at": float(result["inserted_at"]),
                "updated_at": float(result["updated_at"]),
            }
            for result in results
        ]

        return {
            "entries": entries,
            "returned_entries": len(entries),
            "offset": offset,
            "limit": limit,
        }



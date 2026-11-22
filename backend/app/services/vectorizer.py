from typing import Any

from redisvl.utils.vectorize import BaseVectorizer

from backend.app.dependencies.resources import resources


class SharedEmbeddingVectorizer(BaseVectorizer):
    def _embed(self, content: Any, **kwargs) -> list[float]:
        if resources.embedding_model is None:
            raise RuntimeError("Embedding model is not initialized.")

        embedding = resources.embedding_model.encode(content)

        return embedding.tolist()

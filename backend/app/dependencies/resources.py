
import redis
from sentence_transformers import SentenceTransformer

from backend.app.core.config import get_settings


class ApplicationResources:
    def __init__(self):
        self.settings = get_settings()

        self.redis_client = None
        self.embedding_model = None

    def initialize_redis(self):
        self.redis_client = redis.Redis.from_url(
            self.settings.REDIS_URL,
            decode_responses=False,
        )

        self.redis_client.ping()
        print("Redis connection initialized.")

    def initialize_embedding_model(self):
        self.embedding_model = SentenceTransformer(
            self.settings.EMBEDDING_MODEL
        )

        print("Embedding model initialized.")

    def initialize(self):
        self.initialize_redis()
        self.initialize_embedding_model()

    def close(self):
        if self.redis_client:
            self.redis_client.close()
            print("Redis connection closed.")


resources = ApplicationResources()

from backend.app.core.exceptions import ServiceUnavailableError
from backend.app.dependencies.resources import resources


class AnalyticsService:
    def __init__(self):
        self.analytics_key = "semantic-cache-analytics:v1"

    def record_request(self, cache_hit: bool, latency_ms: float):
        redis_client = resources.redis_client

        if redis_client is None:
            raise ServiceUnavailableError("Redis client is not initialized.")

        pipeline = redis_client.pipeline(transaction=True)

        pipeline.hincrby(self.analytics_key, "total_requests", 1)

        if cache_hit:
            pipeline.hincrby(self.analytics_key, "cache_hits", 1)
        else:
            pipeline.hincrby(self.analytics_key, "cache_misses", 1)
            pipeline.hincrby(self.analytics_key, "llm_calls", 1)

        pipeline.hincrbyfloat(
            self.analytics_key,
            "total_latency_ms",
            latency_ms,
        )

        pipeline.execute()

    def get_analytics(self) -> dict:
        redis_client = resources.redis_client

        if redis_client is None:
            raise ServiceUnavailableError("Redis client is not initialized.")

        metrics = redis_client.hgetall(self.analytics_key)

        total_requests = int(metrics.get(b"total_requests", 0))
        cache_hits = int(metrics.get(b"cache_hits", 0))
        cache_misses = int(metrics.get(b"cache_misses", 0))
        llm_calls = int(metrics.get(b"llm_calls", 0))
        total_latency_ms = float(metrics.get(b"total_latency_ms", 0))

        return {
            "total_requests": total_requests,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "llm_calls": llm_calls,
            "hit_rate": (
                round(cache_hits / total_requests * 100, 2)
                if total_requests else 0
            ),
            "miss_rate": (
                round(cache_misses / total_requests * 100, 2)
                if total_requests else 0
            ),
            "total_latency_ms": round(total_latency_ms, 2),
            "average_latency_ms": (
                round(total_latency_ms / total_requests, 2)
                if total_requests else 0
            ),
        }

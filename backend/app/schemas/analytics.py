
from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    total_requests: int
    cache_hits: int
    cache_misses: int
    llm_calls: int
    hit_rate: float
    miss_rate: float
    total_latency_ms: float
    average_latency_ms: float

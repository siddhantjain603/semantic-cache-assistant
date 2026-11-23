
from unittest.mock import MagicMock

import pytest

from backend.app.core.exceptions import ServiceUnavailableError
from backend.app.dependencies.resources import resources
from backend.app.services.analytics import AnalyticsService


# Verifies that a cache hit increments total requests and cache hits, and records request latency.
def test_record_cache_hit(monkeypatch):
    mock_redis = MagicMock()
    mock_pipeline = MagicMock()

    mock_redis.pipeline.return_value = mock_pipeline

    monkeypatch.setattr(resources, "redis_client", mock_redis)

    service = AnalyticsService()
    service.record_request(cache_hit=True, latency_ms=120.5)

    mock_redis.pipeline.assert_called_once_with(transaction=True)

    mock_pipeline.hincrby.assert_any_call(
        service.analytics_key,
        "total_requests",
        1,
    )
    mock_pipeline.hincrby.assert_any_call(
        service.analytics_key,
        "cache_hits",
        1,
    )
    mock_pipeline.hincrbyfloat.assert_called_once_with(
        service.analytics_key,
        "total_latency_ms",
        120.5,
    )

    mock_pipeline.execute.assert_called_once()


# Verifies that a cache miss increments total requests, cache misses, and LLM calls.
def test_record_cache_miss(monkeypatch):
    mock_redis = MagicMock()
    mock_pipeline = MagicMock()

    mock_redis.pipeline.return_value = mock_pipeline

    monkeypatch.setattr(resources, "redis_client", mock_redis)

    service = AnalyticsService()
    service.record_request(cache_hit=False, latency_ms=250.0)

    mock_pipeline.hincrby.assert_any_call(
        service.analytics_key,
        "total_requests",
        1,
    )
    mock_pipeline.hincrby.assert_any_call(
        service.analytics_key,
        "cache_misses",
        1,
    )
    mock_pipeline.hincrby.assert_any_call(
        service.analytics_key,
        "llm_calls",
        1,
    )
    mock_pipeline.hincrbyfloat.assert_called_once_with(
        service.analytics_key,
        "total_latency_ms",
        250.0,
    )
    mock_pipeline.execute.assert_called_once()


# Verifies that analytics metrics, hit rate, miss rate, and average latency are calculated correctly.
def test_get_analytics(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.hgetall.return_value = {
        b"total_requests": b"10",
        b"cache_hits": b"7",
        b"cache_misses": b"3",
        b"llm_calls": b"3",
        b"total_latency_ms": b"2500",
    }

    monkeypatch.setattr(resources, "redis_client", mock_redis)

    service = AnalyticsService()
    result = service.get_analytics()

    assert result == {
        "total_requests": 10,
        "cache_hits": 7,
        "cache_misses": 3,
        "llm_calls": 3,
        "hit_rate": 70.0,
        "miss_rate": 30.0,
        "total_latency_ms": 2500.0,
        "average_latency_ms": 250.0,
    }

    mock_redis.hgetall.assert_called_once_with(service.analytics_key)


# Verifies that analytics returns zero-valued metrics when Redis contains no analytics data.
def test_get_analytics_empty(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.hgetall.return_value = {}

    monkeypatch.setattr(resources, "redis_client", mock_redis)

    service = AnalyticsService()
    result = service.get_analytics()

    assert result == {
        "total_requests": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "llm_calls": 0,
        "hit_rate": 0,
        "miss_rate": 0,
        "total_latency_ms": 0,
        "average_latency_ms": 0,
    }


# Verifies that recording analytics raises ServiceUnavailableError when Redis is not initialized.
def test_record_request_without_redis(monkeypatch):
    monkeypatch.setattr(resources, "redis_client", None)

    service = AnalyticsService()

    with pytest.raises(
        ServiceUnavailableError,
        match="Redis client is not initialized.",
    ):
        service.record_request(cache_hit=True, latency_ms=100.0)


# Verifies that retrieving analytics raises ServiceUnavailableError when Redis is not initialized.
def test_get_analytics_without_redis(monkeypatch):
    monkeypatch.setattr(resources, "redis_client", None)

    service = AnalyticsService()

    with pytest.raises(
        ServiceUnavailableError,
        match="Redis client is not initialized.",
    ):
        service.get_analytics()

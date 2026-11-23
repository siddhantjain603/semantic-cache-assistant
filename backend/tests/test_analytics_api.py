from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from redis.exceptions import RedisError

from backend.app.api.routes.analytics import get_analytics_service
from backend.app.api.routes.chat import chat_service
from backend.app.main import app


def test_get_analytics_endpoint(monkeypatch):
    mock_analytics = {
        "total_requests": 10,
        "cache_hits": 7,
        "cache_misses": 3,
        "llm_calls": 3,
        "hit_rate": 70.0,
        "miss_rate": 30.0,
        "total_latency_ms": 2500.0,
        "average_latency_ms": 250.0,
    }

    mock_service = MagicMock()
    mock_service.get_analytics.return_value = mock_analytics

    monkeypatch.setattr(
        "backend.app.main.resources.initialize",
        lambda: None,
    )
    monkeypatch.setattr(
        "backend.app.main.resources.close",
        lambda: None,
    )
    monkeypatch.setattr(
        chat_service,
        "initialize",
        lambda: None,
    )

    app.dependency_overrides[get_analytics_service] = (
        lambda: mock_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/analytics")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == mock_analytics

    mock_service.get_analytics.assert_called_once()

def test_get_analytics_empty(monkeypatch):
    mock_analytics = {
        "total_requests": 0,
        "cache_hits": 0,
        "cache_misses": 0,
        "llm_calls": 0,
        "hit_rate": 0,
        "miss_rate": 0,
        "total_latency_ms": 0,
        "average_latency_ms": 0,
    }

    mock_service = MagicMock()
    mock_service.get_analytics.return_value = mock_analytics

    monkeypatch.setattr(
        "backend.app.main.resources.initialize",
        lambda: None,
    )
    monkeypatch.setattr(
        "backend.app.main.resources.close",
        lambda: None,
    )
    monkeypatch.setattr(
        chat_service,
        "initialize",
        lambda: None,
    )

    app.dependency_overrides[get_analytics_service] = (
        lambda: mock_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/analytics")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == mock_analytics

def test_get_analytics_when_redis_fails(monkeypatch):
    mock_service = MagicMock()
    mock_service.get_analytics.side_effect = RedisError(
        "Redis connection failed"
    )

    monkeypatch.setattr(
        "backend.app.main.resources.initialize",
        lambda: None,
    )
    monkeypatch.setattr(
        "backend.app.main.resources.close",
        lambda: None,
    )
    monkeypatch.setattr(
        chat_service,
        "initialize",
        lambda: None,
    )

    app.dependency_overrides[get_analytics_service] = (
        lambda: mock_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/analytics")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "A required service is currently unavailable."
    }

    mock_service.get_analytics.assert_called_once()
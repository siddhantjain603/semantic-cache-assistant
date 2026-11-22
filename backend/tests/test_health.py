
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from backend.app.dependencies.resources import resources
from backend.app.main import app


def test_health_endpoint(monkeypatch):
    mock_redis = MagicMock()
    mock_redis.ping.return_value = True

    monkeypatch.setattr(resources, "redis_client", mock_redis)
    monkeypatch.setattr(resources, "embedding_model", MagicMock())
    monkeypatch.setattr(resources, "initialize", lambda: None)
    monkeypatch.setattr(resources, "close", lambda: None)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "Semantic Cache Assistant"
    assert data["status"] == "healthy"
    assert data["redis"] == "connected"
    assert data["embedding_model"] == "loaded"

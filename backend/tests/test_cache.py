from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from redis.exceptions import RedisError
from redisvl.exceptions import RedisSearchError

from backend.app.api.routes.cache import get_semantic_cache_service
from backend.app.api.routes.chat import chat_service
from backend.app.main import app


def test_get_cache_entries(monkeypatch):
    mock_entries = {
        "entries": [
            {
                "id": "cache:123",
                "question": "What is machine learning?",
                "answer": "Machine learning enables systems to learn from data.",
                "inserted_at": 1795341127.36,
                "updated_at": 1795341127.36,
            }
        ],
        "total_entries": 1,
        "returned_entries": 1,
        "offset": 0,
        "limit": 20,
    }

    mock_service = MagicMock()
    mock_service.get_entries.return_value = mock_entries

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

    app.dependency_overrides[get_semantic_cache_service] = (
        lambda: mock_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/cache")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == mock_entries

    mock_service.get_entries.assert_called_once_with(
        offset=0,
        limit=20,
    )

def test_get_cache_entries_with_pagination(monkeypatch):
    mock_service = MagicMock()
    mock_service.get_entries.return_value = {
        "entries": [],
        "total_entries": 15,
        "returned_entries": 0,
        "offset": 10,
        "limit": 5,
    }

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

    app.dependency_overrides[get_semantic_cache_service] = (
        lambda: mock_service
    )
    try:
        with TestClient(app) as client:
            response = client.get("/cache?offset=10&limit=5")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["offset"] == 10
    assert response.json()["limit"] == 5
    mock_service.get_entries.assert_called_once_with(
        offset=10,
        limit=5,
    )

def test_get_cache_entries_invalid_pagination(monkeypatch):
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

    with TestClient(app) as client:
        invalid_urls = [
            "/cache?offset=-1",
            "/cache?limit=0",
            "/cache?limit=101",
        ]

        for url in invalid_urls:
            response = client.get(url)
            assert response.status_code == 422, (
                f"Expected 422 for {url}, got {response.status_code}"
            )

def test_get_cache_entries_when_redis_fails(monkeypatch):
    mock_service = MagicMock()
    mock_service.get_entries.side_effect = RedisError(
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

    app.dependency_overrides[get_semantic_cache_service] = (
        lambda: mock_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/cache")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "A required service is currently unavailable."
    }

def test_get_cache_entries_when_redis_search_fails(monkeypatch):
    mock_service = MagicMock()
    mock_service.get_entries.side_effect = RedisSearchError(
    "Redis search failed"
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

    app.dependency_overrides[get_semantic_cache_service] = (
        lambda: mock_service
    )

    try:
        with TestClient(app) as client:
            response = client.get("/cache")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {
        "detail": "A required service is currently unavailable."
    }

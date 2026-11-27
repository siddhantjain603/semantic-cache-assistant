
from unittest.mock import MagicMock

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError as RedisTimeoutError
from redisvl.exceptions import RedisSearchError

from backend.app.core.exceptions import ServiceUnavailableError
from backend.app.services.chat import ChatService


# Verifies that a cache hit returns the cached answer without calling the LLM or storing another cache entry, and records cache-hit analytics.
def test_ask_returns_cached_response():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is semantic caching?"

    service.semantic_cache.search.return_value = [
        {
            "response": "Semantic caching stores similar responses.",
            "prompt": "Explain semantic caching.",
            "vector_distance": 0.12,
        }
    ]

    result = service.ask(question)

    assert result == {
        "answer": "Semantic caching stores similar responses.",
        "cache_hit": True,
        "matched_question": "Explain semantic caching.",
        "distance": 0.12,
    }

    analytics_call = service.analytics.record_request.call_args

    assert analytics_call.kwargs["cache_hit"] is True
    assert analytics_call.kwargs["latency_ms"] >= 0

    service.semantic_cache.search.assert_called_once_with(question)
    service.llm.generate_response.assert_not_called()
    service.semantic_cache.store.assert_not_called()
    service.analytics.record_request.assert_called_once()


# Verifies that a cache miss triggers LLM generation, stores the generated answer, and records cache-miss analytics.
def test_ask_generates_and_caches_response_on_cache_miss():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is vector search?"
    answer = "Vector search finds similar items using embeddings."

    service.semantic_cache.search.return_value = []
    service.llm.generate_response.return_value = answer

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.semantic_cache.search.assert_called_once_with(question)
    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once_with(
        cache_hit=False,
        latency_ms=service.analytics.record_request.call_args.kwargs["latency_ms"],
    )


# Verifies that an LLM failure propagates the exception without storing a cache entry or recording analytics.
def test_ask_propagates_llm_failure():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is vector search?"

    service.semantic_cache.search.return_value = []
    service.llm.generate_response.side_effect = RuntimeError(
        "LLM service unavailable"
    )

    with pytest.raises(
        RuntimeError,
        match="LLM service unavailable",
    ):
        service.ask(question)

    service.semantic_cache.store.assert_not_called()
    service.analytics.record_request.assert_not_called()


# Verifies that a custom cache availability failure triggers LLM fallback and records analytics.
def test_ask_falls_back_to_llm_when_cache_search_fails():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is semantic caching?"
    answer = "Semantic caching reuses answers for similar questions."

    service.semantic_cache.search.side_effect = ServiceUnavailableError(
        "Semantic cache is unavailable."
    )
    service.llm.generate_response.return_value = answer

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once()


# Verifies that a Redis connection failure during cache search triggers LLM fallback instead of failing the chat request.
def test_ask_falls_back_to_llm_when_redis_search_connection_fails():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is semantic caching?"
    answer = "Semantic caching reuses answers for similar questions."

    service.semantic_cache.search.side_effect = RedisConnectionError(
        "Redis connection failed."
    )
    service.llm.generate_response.return_value = answer

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once()


# Verifies that a cache storage availability failure does not prevent returning the generated answer.
def test_ask_returns_generated_answer_when_cache_store_fails():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is vector search?"
    answer = "Vector search finds similar items using embeddings."

    service.semantic_cache.search.return_value = []
    service.llm.generate_response.return_value = answer
    service.semantic_cache.store.side_effect = ServiceUnavailableError(
        "Semantic cache is unavailable."
    )

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once()


# Verifies that an analytics availability failure does not prevent returning the generated chat response.
def test_ask_returns_response_when_analytics_recording_fails():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is semantic caching?"
    answer = "Semantic caching reuses answers for similar questions."

    service.semantic_cache.search.return_value = []
    service.llm.generate_response.return_value = answer
    service.analytics.record_request.side_effect = ServiceUnavailableError(
        "Analytics service is unavailable."
    )

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.analytics.record_request.assert_called_once()


# Verifies that a RedisVL search failure triggers LLM fallback and does not interrupt the chat request.
def test_ask_falls_back_to_llm_when_redisvl_search_fails():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is semantic caching?"
    answer = "Semantic caching reuses answers for similar questions."

    service.semantic_cache.search.side_effect = RedisSearchError(
        "Redis search operation failed."
    )
    service.llm.generate_response.return_value = answer

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once()


# Verifies that a Redis connection failure during cache storage does not prevent returning the generated answer.
def test_ask_returns_answer_when_redis_cache_store_fails():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is vector search?"
    answer = "Vector search finds similar items using embeddings."

    service.semantic_cache.search.return_value = []
    service.llm.generate_response.return_value = answer
    service.semantic_cache.store.side_effect = RedisConnectionError(
        "Redis connection failed."
    )

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once()


# Verifies that a Redis connection failure during analytics recording does not interrupt the chat response.
def test_ask_returns_response_when_redis_analytics_fails():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is semantic caching?"
    answer = "Semantic caching reuses answers for similar questions."

    service.semantic_cache.search.return_value = []
    service.llm.generate_response.return_value = answer
    service.analytics.record_request.side_effect = RedisConnectionError(
        "Redis connection failed."
    )

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once()


# Verifies that a Redis timeout during cache search triggers LLM fallback and preserves the chat response.
def test_ask_falls_back_to_llm_when_redis_search_times_out():
    service = ChatService()

    service.semantic_cache = MagicMock()
    service.llm = MagicMock()
    service.analytics = MagicMock()

    question = "What is semantic caching?"
    answer = "Semantic caching reuses answers for similar questions."

    service.semantic_cache.search.side_effect = RedisTimeoutError(
        "Redis operation timed out."
    )
    service.llm.generate_response.return_value = answer

    result = service.ask(question)

    assert result == {
        "answer": answer,
        "cache_hit": False,
        "matched_question": None,
        "distance": None,
    }

    service.llm.generate_response.assert_called_once_with(question)
    service.semantic_cache.store.assert_called_once_with(question, answer)
    service.analytics.record_request.assert_called_once()

from unittest.mock import MagicMock, patch

import httpx
import pytest
from groq import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
    RateLimitError,
)

from backend.app.services.llm import LLMService


# Verifies that the Groq client is initialized with the configured API key, timeout, and retry count.
@patch("groq.Groq")
def test_groq_client_initializes_with_configured_settings(mock_groq):
    service = LLMService()

    service.settings.GROQ_API_KEY = "test-api-key"
    service.settings.GROQ_TIMEOUT = 30.0
    service.settings.GROQ_MAX_RETRIES = 2

    service._get_client()

    mock_groq.assert_called_once_with(
        api_key="test-api-key",
        timeout=30.0,
        max_retries=2,
    )

# Verifies that client initialization raises an error when the Groq API key is missing.
@patch("groq.Groq")
def test_groq_client_raises_error_when_api_key_is_missing(mock_groq):
    service = LLMService()
    service.settings.GROQ_API_KEY = ""

    with pytest.raises(
        ValueError,
        match="GROQ_API_KEY is not configured.",
    ):
        service._get_client()

    mock_groq.assert_not_called()

# Verifies that the LLM service sends the configured messages to Groq and returns the generated answer.
@patch("groq.Groq")
def test_generate_response_returns_llm_answer(mock_groq):
    service = LLMService()
    service.settings.GROQ_API_KEY = "test-api-key"
    service.settings.GROQ_MODEL = "test-model"
    service.settings.LLM_SYSTEM_PROMPT = "You are a helpful assistant."

    mock_client = MagicMock()
    mock_groq.return_value = mock_client

    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Semantic caching improves efficiency."))
    ]

    result = service.generate_response("What is semantic caching?")

    assert result == "Semantic caching improves efficiency."

    mock_client.chat.completions.create.assert_called_once_with(
        model="test-model",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "What is semantic caching?",
            },
        ],
        temperature=0.3,
    )

# Verifies that Groq authentication failures propagate to the caller.
@patch("groq.Groq")
def test_generate_response_propagates_authentication_error(mock_groq):
    service = LLMService()
    service.settings.GROQ_API_KEY = "invalid-api-key"

    mock_client = MagicMock()
    mock_groq.return_value = mock_client

    mock_client.chat.completions.create.side_effect = AuthenticationError(
        "Invalid API key.",
        response=MagicMock(status_code=401, headers={}),
        body=None,
    )

    with pytest.raises(AuthenticationError):
        service.generate_response("What is semantic caching?")

# Verifies that Groq API timeout errors propagate to the caller.
@patch("groq.Groq")
def test_generate_response_propagates_timeout_error(mock_groq):
    service = LLMService()
    service.settings.GROQ_API_KEY = "test-api-key"

    mock_client = MagicMock()
    mock_groq.return_value = mock_client

    mock_client.chat.completions.create.side_effect = APITimeoutError(
        request=MagicMock()
    )

    with pytest.raises(APITimeoutError):
        service.generate_response("What is semantic caching?")

# Verifies that Groq rate-limit errors propagate to the caller.
@patch("groq.Groq")
def test_generate_response_propagates_rate_limit_error(mock_groq):
    service = LLMService()
    service.settings.GROQ_API_KEY = "test-api-key"

    mock_client = MagicMock()
    mock_groq.return_value = mock_client

    mock_client.chat.completions.create.side_effect = RateLimitError(
        "Rate limit exceeded.",
        response=MagicMock(status_code=429, headers={}),
        body=None,
    )

    with pytest.raises(RateLimitError):
        service.generate_response("What is semantic caching?")

# Verifies that Groq internal server errors propagate to the caller.
@patch("groq.Groq")
def test_generate_response_propagates_internal_server_error(mock_groq):
    service = LLMService()
    service.settings.GROQ_API_KEY = "test-api-key"

    mock_client = MagicMock()
    mock_groq.return_value = mock_client

    mock_client.chat.completions.create.side_effect = InternalServerError(
        "Groq server error.",
        response=MagicMock(status_code=500, headers={}),
        body=None,
    )

    with pytest.raises(InternalServerError):
        service.generate_response("What is semantic caching?")

# Verifies that Groq connection failures propagate to the caller.
@patch("groq.Groq")
def test_generate_response_propagates_connection_error(mock_groq):
    service = LLMService()
    service.settings.GROQ_API_KEY = "test-api-key"

    mock_client = MagicMock()
    mock_groq.return_value = mock_client

    request = httpx.Request(
        "POST",
        "https://api.groq.com/openai/v1/chat/completions",
    )

    mock_client.chat.completions.create.side_effect = APIConnectionError(
        request=request
    )

    with pytest.raises(APIConnectionError):
        service.generate_response("What is semantic caching?")
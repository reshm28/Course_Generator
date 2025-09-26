"""Test configuration and fixtures for AI agents."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.infrastructure.llm.llm_client import BaseLLMClient


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    client = AsyncMock(spec=BaseLLMClient)
    client.generate_structured = AsyncMock()
    return client


@pytest.fixture
def mock_llm_response():
    """Create a mock LLM response function."""
    def _create_mock_response(output_model, **fields):
        # Create a mock instance of the output model with the given fields
        mock = MagicMock(spec=output_model)
        for field, value in fields.items():
            setattr(mock, field, value)
        return mock
    return _create_mock_response

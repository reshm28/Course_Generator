"""Tests for the TopicValidatorNode."""
import pytest
from unittest.mock import AsyncMock

from app.application.ai_agents.lesson_content.topic_validator import (
    TopicValidatorNode,
    TopicValidatorInput,
    TopicValidatorOutput
)


@pytest.mark.asyncio
async def test_topic_validator_process(mock_llm_client, mock_llm_response):
    """Test the process method of TopicValidatorNode."""
    # Setup
    validator = TopicValidatorNode(llm_client=mock_llm_client)
    
    # Mock the LLM response
    mock_output = mock_llm_response(
        TopicValidatorOutput,
        original_topic="Python programming",
        refined_topic="Introduction to Python Programming for Beginners",
        is_valid=True,
        validation_message="Topic is valid and has been refined for clarity.",
        suggested_scope="Cover basic syntax, variables, and simple programs",
        prerequisites=["Basic computer literacy", "No prior programming experience required"]
    )
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test
    input_data = {
        "topic": "Python programming",
        "target_audience": "beginner",
        "context": "This is for a beginner programming course"
    }
    
    # Execute
    result = await validator.process(input_data)
    
    # Assert
    assert isinstance(result, TopicValidatorOutput)
    assert result.original_topic == "Python programming"
    assert result.is_valid is True
    assert hasattr(result, 'refined_topic')
    assert hasattr(result, 'suggested_scope')
    
    # Verify the LLM was called with the correct parameters
    mock_llm_client.generate_structured.assert_awaited_once()
    args, kwargs = mock_llm_client.generate_structured.await_args
    assert kwargs["output_model"] == TopicValidatorOutput
    assert "topic" in kwargs
    assert kwargs["topic"] == "Python programming"


@pytest.mark.asyncio
async def test_topic_validator_invalid_topic(mock_llm_client, mock_llm_response):
    """Test validation of an invalid topic."""
    # Setup
    validator = TopicValidatorNode(llm_client=mock_llm_client)
    
    # Mock the LLM response for an invalid topic
    mock_output = mock_llm_response(
        TopicValidatorOutput,
        original_topic="",
        refined_topic="",
        is_valid=False,
        validation_message="Topic cannot be empty.",
        suggested_scope="",
        prerequisites=[]
    )
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test with empty topic
    input_data = {
        "topic": "",
        "target_audience": "beginner"
    }
    
    # Execute
    result = await validator.process(input_data)
    
    # Assert
    assert isinstance(result, TopicValidatorOutput)
    assert result.is_valid is False
    assert hasattr(result, 'validation_message')


def test_topic_validator_input_validation():
    """Test input validation for TopicValidatorInput."""
    # Valid input
    valid_input = {
        "topic": "Python programming",
        "target_audience": "beginner"
    }
    input_model = TopicValidatorInput(**valid_input)
    assert input_model.topic == "Python programming"
    assert input_model.target_audience == "beginner"
    
    # Test with default values
    minimal_input = {"topic": "Python"}
    input_model = TopicValidatorInput(**minimal_input)
    assert input_model.topic == "Python"
    assert input_model.target_audience == "beginner"  # default
    assert input_model.context == ""  # default

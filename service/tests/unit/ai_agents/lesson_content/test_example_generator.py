"""Tests for the ExampleGeneratorNode."""
import pytest
from unittest.mock import AsyncMock

from app.application.ai_agents.lesson_content.example_generator import (
    ExampleGeneratorNode,
    ExampleGeneratorInput,
    ExampleGeneratorOutput
)
from app.domain.entities.lesson import Example


@pytest.mark.asyncio
async def test_example_generator_process(mock_llm_client, mock_llm_response):
    """Test the process method of ExampleGeneratorNode."""
    # Setup
    node = ExampleGeneratorNode(llm_client=mock_llm_client)
    
    # Mock the LLM response
    mock_output = mock_llm_response(
        ExampleGeneratorOutput,
        examples=[
            Example(
                title="E-commerce Website",
                description="Building a simple e-commerce site with product listings and cart functionality.",
                key_takeaway="Shows practical application of Python web development"
            ),
            Example(
                title="Data Analysis with Pandas",
                description="Analyzing sales data to find trends and insights.",
                key_takeaway="Demonstrates data manipulation and analysis"
            )
        ],
        additional_resources=[
            {"title": "Python Documentation", "url": "https://docs.python.org/3/"},
            {"title": "Pandas User Guide", "url": "https://pandas.pydata.org/docs/"}
        ]
    )
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test input
    input_data = {
        "topic": "Python Programming",
        "target_audience": "beginner",
        "learning_objectives": [
            {"description": "Write Python functions", "key_concept": "Functions"},
            {"description": "Work with data structures", "key_concept": "Data Structures"}
        ],
        "content_sections": [
            {"heading": "Introduction", "content": "Python is a versatile language..."},
            {"heading": "Functions", "content": "Functions are reusable blocks of code..."}
        ],
        "example_types": ["real-world", "code"],
        "num_examples": 2
    }
    
    # Execute
    result = await node.process(input_data)
    
    # Assert
    assert isinstance(result, ExampleGeneratorOutput)
    assert len(result.examples) == 2
    assert all(isinstance(ex, Example) for ex in result.examples)
    assert len(result.additional_resources) > 0
    
    # Verify the LLM was called with the correct parameters
    mock_llm_client.generate_structured.assert_awaited_once()
    args, kwargs = mock_llm_client.generate_structured.await_args
    assert kwargs["output_model"] == ExampleGeneratorOutput
    assert "topic" in kwargs
    assert kwargs["topic"] == "Python Programming"


def test_example_generator_input_validation():
    """Test input validation for ExampleGeneratorInput."""
    # Valid input
    valid_input = {
        "topic": "Python Functions",
        "target_audience": "beginner",
        "learning_objectives": [
            {"description": "Define functions", "key_concept": "Functions"}
        ],
        "content_sections": [
            {"heading": "Intro", "content": "Content here"}
        ],
        "example_types": ["code"],
        "num_examples": 2
    }
    input_model = ExampleGeneratorInput(**valid_input)
    assert input_model.topic == "Python Functions"
    assert input_model.example_types == ["code"]
    assert input_model.num_examples == 2
    
    # Test with default values
    minimal_input = {
        "topic": "Python",
        "learning_objectives": [{"description": "Test", "key_concept": "Test"}],
        "content_sections": [{"heading": "Test", "content": "Test"}]
    }
    input_model = ExampleGeneratorInput(**minimal_input)
    assert input_model.topic == "Python"
    assert input_model.target_audience == "beginner"  # default
    assert input_model.example_types == []  # default
    assert input_model.num_examples == 2  # default


@pytest.mark.asyncio
async def test_example_generator_minimum_examples(mock_llm_client, mock_llm_response):
    """Test that the minimum number of examples is returned."""
    # Setup
    node = ExampleGeneratorNode(llm_client=mock_llm_client)
    
    # Mock the LLM response with one example (minimum required)
    mock_output = mock_llm_response(
        ExampleGeneratorOutput,
        examples=[
            Example(
                title="Test Example",
                description="This is a test example.",
                key_takeaway="Test key takeaway"
            )
        ],
        additional_resources=[]
    )
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test input
    input_data = {
        "topic": "Test Topic",
        "learning_objectives": [{"description": "Test", "key_concept": "Test"}],
        "content_sections": [{"heading": "Test", "content": "Test"}],
        "num_examples": 1
    }
    
    # Execute
    result = await node.process(input_data)
    
    # Assert that we got at least one example
    assert len(result.examples) >= 1

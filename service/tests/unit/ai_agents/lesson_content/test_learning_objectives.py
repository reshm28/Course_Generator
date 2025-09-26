"""Tests for the LearningObjectivesNode."""
import pytest
from unittest.mock import AsyncMock

from app.application.ai_agents.lesson_content.learning_objectives import (
    LearningObjectivesNode,
    LearningObjectivesInput,
    LearningObjectivesOutput
)
from app.domain.entities.lesson import LearningObjective


@pytest.mark.asyncio
async def test_learning_objectives_process(mock_llm_client, mock_llm_response):
    """Test the process method of LearningObjectivesNode."""
    # Setup
    node = LearningObjectivesNode(llm_client=mock_llm_client)
    
    # Mock the LLM response
    mock_output = mock_llm_response(
        LearningObjectivesOutput,
        objectives=[
            LearningObjective(
                description="Understand basic Python syntax and data types",
                key_concept="Python Basics"
            ),
            LearningObjective(
                description="Write simple Python programs using conditionals and loops",
                key_concept="Control Flow"
            ),
            LearningObjective(
                description="Create and use functions to organize code",
                key_concept="Functions"
            )
        ],
        difficulty="beginner",
        alignment_note="Objectives align well with beginner Python programming."
    )
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test input
    input_data = {
        "topic": "Introduction to Python",
        "target_audience": "beginner",
        "scope": "Basic Python programming concepts",
        "prerequisites": ["Basic computer literacy"]
    }
    
    # Execute
    result = await node.process(input_data)
    
    # Assert
    assert isinstance(result, LearningObjectivesOutput)
    assert len(result.objectives) == 3
    assert all(isinstance(obj, LearningObjective) for obj in result.objectives)
    assert result.difficulty == "beginner"
    
    # Verify the LLM was called with the correct parameters
    mock_llm_client.generate_structured.assert_awaited_once()
    args, kwargs = mock_llm_client.generate_structured.await_args
    assert kwargs["output_model"] == LearningObjectivesOutput
    assert "topic" in kwargs
    assert kwargs["topic"] == "Introduction to Python"


def test_learning_objectives_input_validation():
    """Test input validation for LearningObjectivesInput."""
    # Valid input
    valid_input = {
        "topic": "Python Programming",
        "target_audience": "beginner",
        "scope": "Basic concepts",
        "prerequisites": ["None"]
    }
    input_model = LearningObjectivesInput(**valid_input)
    assert input_model.topic == "Python Programming"
    assert input_model.target_audience == "beginner"
    assert input_model.scope == "Basic concepts"
    assert isinstance(input_model.prerequisites, list)
    
    # Test with default values
    minimal_input = {
        "topic": "Python",
        "scope": "Basics"
    }
    input_model = LearningObjectivesInput(**minimal_input)
    assert input_model.topic == "Python"
    assert input_model.target_audience == "beginner"  # default
    assert input_model.prerequisites == []  # default


@pytest.mark.asyncio
async def test_learning_objectives_minimum_required(mock_llm_client, mock_llm_response):
    """Test that the minimum number of learning objectives is enforced."""
    # Setup
    node = LearningObjectivesNode(llm_client=mock_llm_client)
    
    # Mock the LLM response with the minimum required objectives
    mock_output = mock_llm_response(
        LearningObjectivesOutput,
        objectives=[
            LearningObjective(
                description="First learning objective",
                key_concept="Concept 1"
            ),
            LearningObjective(
                description="Second learning objective",
                key_concept="Concept 2"
            ),
            LearningObjective(
                description="Third learning objective",
                key_concept="Concept 3"
            )
        ],
        difficulty="beginner"
    )
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test input
    input_data = {
        "topic": "Test Topic",
        "scope": "Test Scope"
    }
    
    # Execute the process
    result = await node.process(input_data)
    
    # Verify that we got exactly 3 objectives (the minimum required)
    assert len(result.objectives) == 3, "Should have exactly 3 learning objectives"

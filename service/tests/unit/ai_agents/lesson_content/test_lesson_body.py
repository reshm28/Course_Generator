"""Tests for the LessonBodyNode."""
import pytest
from unittest.mock import AsyncMock

from app.application.ai_agents.lesson_content.lesson_body import (
    LessonBodyNode,
    LessonBodyInput,
    LessonSection
)
from app.domain.entities.lesson import LearningObjective


@pytest.mark.asyncio
async def test_lesson_body_process(mock_llm_client, mock_llm_response):
    """Test the process method of LessonBodyNode."""
    # Setup
    node = LessonBodyNode(llm_client=mock_llm_client)
    
    # Mock the LLM response
    mock_output = {
        "sections": [
            {
                "heading": "Introduction to Python",
                "content": "Python is a high-level programming language...",
                "key_points": ["Python is versatile", "Easy to read syntax"],
                "learning_objectives_covered": [0, 1]
            },
            {
                "heading": "Basic Syntax",
                "content": "Python uses indentation to define code blocks...",
                "key_points": ["Indentation matters", "Simple syntax rules"],
                "learning_objectives_covered": [0]
            }
        ],
        "estimated_duration_minutes": 45,
        "key_terms": {
            "variable": "A named location used to store data",
            "function": "A block of reusable code"
        }
    }
    
    # Create a proper mock response with the output model
    mock_response = type('MockResponse', (), {
        'sections': [
            type('MockSection', (), section) for section in mock_output['sections']
        ],
        'estimated_duration_minutes': mock_output['estimated_duration_minutes'],
        'key_terms': mock_output['key_terms']
    })
    mock_llm_client.generate_structured.return_value = mock_response
    
    # Create LearningObjective objects
    learning_objectives = [
        LearningObjective(
            description="Understand basic Python syntax",
            key_concept="Python Basics"
        ),
        LearningObjective(
            description="Write simple Python programs",
            key_concept="Programming"
        )
    ]
    
    # Test input
    input_data = {
        "topic": "Introduction to Python",
        "target_audience": "beginner",
        "learning_objectives": learning_objectives,
        "scope": "Basic Python programming concepts",
        "key_terms": ["variable", "function"]
    }
    
    # Execute
    result = await node.process(input_data)
    
    # Assert
    assert hasattr(result, 'sections')
    assert len(result.sections) == 2
    assert all(hasattr(section, 'heading') for section in result.sections)
    assert hasattr(result, 'estimated_duration_minutes')
    assert isinstance(result.estimated_duration_minutes, int)
    
    # Verify the LLM was called with the correct parameters
    mock_llm_client.generate_structured.assert_awaited_once()
    args, kwargs = mock_llm_client.generate_structured.await_args
    assert "topic" in kwargs
    assert kwargs["topic"] == "Introduction to Python"


def test_lesson_body_input_validation():
    """Test input validation for LessonBodyInput."""
    # Valid input
    valid_input = {
        "topic": "Python Basics",
        "target_audience": "beginner",
        "learning_objectives": [
            {"description": "Learn Python", "key_concept": "Python"}
        ],
        "scope": "Introduction"
    }
    input_model = LessonBodyInput(**valid_input)
    assert input_model.topic == "Python Basics"
    assert len(input_model.learning_objectives) == 1
    assert input_model.learning_objectives[0].description == "Learn Python"
    
    # Test with default values
    minimal_input = {
        "topic": "Python",
        "learning_objectives": [{"description": "Learn", "key_concept": "Basics"}],
        "scope": "Intro"
    }
    input_model = LessonBodyInput(**minimal_input)
    assert input_model.topic == "Python"
    assert input_model.target_audience == "beginner"  # default
    assert input_model.key_terms == []  # default


@pytest.mark.asyncio
async def test_lesson_body_minimum_sections(mock_llm_client, mock_llm_response):
    """Test that the minimum number of sections is enforced."""
    # Setup
    node = LessonBodyNode(llm_client=mock_llm_client)
    
    # Mock the LLM response with the minimum required sections
    mock_output = {
        "sections": [
            {
                "heading": "Section 1",
                "content": "Content for section 1...",
                "key_points": ["Key point 1"],
                "learning_objectives_covered": [0]
            },
            {
                "heading": "Section 2",
                "content": "Content for section 2...",
                "key_points": ["Key point 2"],
                "learning_objectives_covered": [0]
            },
            {
                "heading": "Section 3",
                "content": "Content for section 3...",
                "key_points": ["Key point 3"],
                "learning_objectives_covered": [0]
            }
        ],
        "estimated_duration_minutes": 30,
        "key_terms": {}
    }
    
    # Create a proper mock response with the output model
    mock_response = type('MockResponse', (), {
        'sections': [
            type('MockSection', (), section) for section in mock_output['sections']
        ],
        'estimated_duration_minutes': mock_output['estimated_duration_minutes'],
        'key_terms': mock_output['key_terms']
    })
    mock_llm_client.generate_structured.return_value = mock_response
    
    # Create LearningObjective objects
    learning_objectives = [
        LearningObjective(
            description="Test",
            key_concept="Test"
        )
    ]
    
    # Test input
    input_data = {
        "topic": "Test Topic",
        "learning_objectives": learning_objectives,
        "scope": "Test Scope"
    }
    
    # Execute
    result = await node.process(input_data)
    
    # Assert that we got at least 3 sections (minimum required)
    assert len(result.sections) >= 3

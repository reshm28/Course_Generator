"""Tests for the QuizCreatorNode."""
import pytest
from unittest.mock import AsyncMock

from app.application.ai_agents.lesson_content.quiz_creator import (
    QuizCreatorNode,
    QuizCreatorInput,
    QuizCreatorOutput
)
from app.domain.entities.lesson import QuizQuestion


@pytest.mark.asyncio
async def test_quiz_creator_process(mock_llm_client, mock_llm_response):
    """Test the process method of QuizCreatorNode."""
    # Setup
    node = QuizCreatorNode(llm_client=mock_llm_client)
    
    # Create mock quiz questions with all required fields
    question1 = {
        "question": "What is the correct way to define a function in Python?",
        "options": [
            "function my_func():",
            "def my_func():",
            "create function my_func():",
            "func my_func():"
        ],
        "correct_answer": 1,
        "explanation": "In Python, functions are defined using the 'def' keyword.",
        "learning_objectives": ["Define functions"]
    }
    
    question2 = {
        "question": "Which data type is mutable in Python?",
        "options": [
            "Tuple",
            "String",
            "List",
            "Integer"
        ],
        "correct_answer": 2,
        "explanation": "Lists are mutable, meaning their elements can be changed after creation.",
        "learning_objectives": ["Work with data types"]
    }
    
    # Create a mock response that matches the QuizCreatorOutput model
    mock_output = {
        "questions": [question1, question2],
        "answer_key": {
            0: {"correct_answer": 1, "explanation": "Functions use 'def' in Python"},
            1: {"correct_answer": 2, "explanation": "Lists are mutable"}
        },
        "assessment_criteria": {
            "passing_score": "0.7",
            "feedback_level": "detailed"
        }
    }
    
    # Convert to the proper output model
    mock_output = QuizCreatorOutput(**mock_output)
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test input
    input_data = {
        "topic": "Python Basics",
        "target_audience": "beginner",
        "learning_objectives": [
            {"description": "Define functions", "key_concept": "Functions"},
            {"description": "Work with data types", "key_concept": "Data Types"}
        ],
        "content_sections": [
            {"heading": "Functions", "content": "How to define and use functions..."},
            {"heading": "Data Types", "content": "Different data types in Python..."}
        ],
        "num_questions": 2,
        "question_types": ["multiple_choice"],
        "difficulty": "easy"
    }
    
    # Execute
    result = await node.process(input_data)
    
    # Assert
    assert isinstance(result, QuizCreatorOutput)
    assert len(result.questions) == 2
    assert all(isinstance(q, QuizQuestion) for q in result.questions)
    assert "answer_key" in result.model_dump()
    assert len(result.answer_key) == 2
    
    # Verify question structure
    for q in result.questions:
        assert hasattr(q, 'question')
        assert hasattr(q, 'options')
        assert hasattr(q, 'correct_answer')
        assert hasattr(q, 'explanation')
        assert isinstance(q.options, list)
        assert len(q.options) >= 2  # At least 2 options for multiple choice
    
    # Verify the LLM was called with the correct parameters
    mock_llm_client.generate_structured.assert_awaited_once()
    args, kwargs = mock_llm_client.generate_structured.await_args
    assert kwargs["output_model"] == QuizCreatorOutput
    assert "topic" in kwargs
    assert kwargs["topic"] == "Python Basics"


def test_quiz_creator_input_validation():
    """Test input validation for QuizCreatorInput."""
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
        "num_questions": 3,
        "question_types": ["multiple_choice"],
        "difficulty": "medium"
    }
    input_model = QuizCreatorInput(**valid_input)
    assert input_model.topic == "Python Functions"
    assert input_model.num_questions == 3
    assert input_model.difficulty == "medium"
    
    # Test with default values
    minimal_input = {
        "topic": "Python",
        "learning_objectives": [{"description": "Test", "key_concept": "Test"}],
        "content_sections": [{"heading": "Test", "content": "Test"}]
    }
    input_model = QuizCreatorInput(**minimal_input)
    assert input_model.topic == "Python"
    assert input_model.target_audience == "beginner"  # default
    assert input_model.num_questions == 3  # default
    assert input_model.question_types == ["multiple_choice"]  # default
    assert input_model.difficulty == "medium"  # default


@pytest.mark.asyncio
async def test_quiz_creator_minimum_questions(mock_llm_client, mock_llm_response):
    """Test that the minimum number of questions is enforced."""
    # Setup
    node = QuizCreatorNode(llm_client=mock_llm_client)
    
    # Mock the LLM response with too few questions
    mock_output = mock_llm_response(
        QuizCreatorOutput,
        questions=[],
        answer_key={},
        assessment_criteria={}
    )
    mock_llm_client.generate_structured.return_value = mock_output
    
    # Test input
    input_data = {
        "topic": "Test Topic",
        "learning_objectives": [{"description": "Test", "key_concept": "Test"}],
        "content_sections": [{"heading": "Test", "content": "Test"}],
        "num_questions": 1
    }
    
    # Execute and assert that validation fails
    with pytest.raises(ValueError):
        await node.process(input_data)

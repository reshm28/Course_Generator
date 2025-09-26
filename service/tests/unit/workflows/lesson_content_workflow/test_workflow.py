"""Tests for the LessonContentWorkflow."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.application.workflows.lesson_content_workflow import (
    LessonContentWorkflow,
    WorkflowState
)
from app.domain.entities.lesson import (
    LessonContent,
    LearningObjective,
    Example,
    QuizQuestion,
    DifficultyLevel
)


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client."""
    client = AsyncMock()
    client.generate_structured = AsyncMock()
    return client


@pytest.fixture
def mock_workflow_components(mock_llm_client):
    """Mock the workflow components."""
    with patch('app.application.workflows.lesson_content_workflow.LessonContentWorkflow._build_graph') as mock_build_graph:
        # Create an async mock for the graph
        mock_graph = AsyncMock()
        mock_build_graph.return_value = mock_graph
        
        # Set up the mock graph's return value
        mock_graph.ainvoke.return_value = {
            "topic": "Introduction to Python Programming",
            "target_audience": "beginner",
            "context": None,
            "validated_topic": {
                "original_topic": "Python",
                "refined_topic": "Introduction to Python Programming",
                "is_valid": True,
                "validation_message": "Topic is valid",
                "suggested_scope": "Basic Python syntax and concepts",
                "prerequisites": ["Basic computer literacy"]
            },
            "learning_objectives": {
                "objectives": [
                    {"description": "Learn Python syntax", "key_concept": "Syntax"},
                    {"description": "Write simple programs", "key_concept": "Programming"}
                ],
                "difficulty": "beginner",
                "alignment_note": "Objectives align with beginner level"
            },
            "content_sections": {
                "sections": [
                    {"heading": "Introduction", "content": "Welcome to Python"},
                    {"heading": "Basics", "content": "Variables and data types"}
                ],
                "estimated_duration_minutes": 45,
                "key_terms": {"variable": "A named location for storing data"}
            },
            "examples": {
                "examples": [
                    {"title": "Hello World", "description": "A simple program", "key_takeaway": "Basic syntax"}
                ],
                "additional_resources": [
                    {"title": "Python Docs", "url": "https://docs.python.org/3/"}
                ]
            },
            "quiz_questions": {
                "questions": [
                    {
                        "question": "What is the correct syntax?",
                        "options": ["A", "B", "C"],
                        "correct_answer": 0,
                        "explanation": "A is correct"
                    }
                ],
                "answer_key": {0: {"correct_answer": 0, "explanation": "A is correct"}},
                "assessment_criteria": {"passing_score": 0.7}
            },
            "lesson": {
                "topic": "Introduction to Python Programming",
                "difficulty": "beginner",
                "learning_objectives": [
                    {"description": "Learn Python syntax", "key_concept": "Syntax"},
                    {"description": "Write simple programs", "key_concept": "Programming"}
                ],
                "content_sections": [
                    {"heading": "Introduction", "content": "Welcome to Python"},
                    {"heading": "Basics", "content": "Variables and data types"}
                ],
                "examples": [
                    {"title": "Hello World", "description": "A simple program", "key_takeaway": "Basic syntax"}
                ],
                "quiz_questions": [
                    {
                        "question": "What is the correct syntax?",
                        "options": ["A", "B", "C"],
                        "correct_answer": 0,
                        "explanation": "A is correct"
                    }
                ],
                "estimated_duration_minutes": 45,
                "key_terms": {"variable": "A named location for storing data"},
                "prerequisites": ["Basic computer literacy"],
                "additional_resources": [
                    {"title": "Python Docs", "url": "https://docs.python.org/3/"}
                ]
            }
        }
        
        yield mock_graph


@pytest.mark.asyncio
async def test_generate_lesson_happy_path(mock_llm_client, mock_workflow_components):
    """Test the happy path for generating a lesson."""
    # Setup
    workflow = LessonContentWorkflow(llm_client=mock_llm_client)

    # Execute
    lesson = await workflow.generate_lesson(
        topic="Python",
        target_audience="beginner",
        context="Introduction to programming"
    )

    # Assert
    assert isinstance(lesson, dict)
    assert lesson["topic"] == "Introduction to Python Programming"
    assert len(lesson["learning_objectives"]) == 2
    assert len(lesson["content_sections"]) == 2
    assert len(lesson["examples"]) == 1
    assert len(lesson["quiz_questions"]) == 1
    
    # Verify the graph was called with the correct input
    mock_workflow_components.ainvoke.assert_awaited_once()
    args, kwargs = mock_workflow_components.ainvoke.call_args
    assert args[0]["topic"] == "Python"
    assert args[0]["target_audience"] == "beginner"
    assert args[0]["context"] == "Introduction to programming"


@pytest.mark.asyncio
async def test_generate_lesson_validation_failure(mock_llm_client, mock_workflow_components):
    """Test handling of topic validation failure."""
    # Setup - make the graph return an invalid result
    mock_workflow_components.ainvoke.return_value = {
        "topic": "",
        "target_audience": "beginner",
        "context": None,
        "validated_topic": {
            "original_topic": "",
            "refined_topic": "",
            "is_valid": False,
            "validation_message": "Topic cannot be empty",
            "suggested_scope": "",
            "prerequisites": []
        },
        "error": "Validation failed: Topic cannot be empty"
    }

    workflow = LessonContentWorkflow(llm_client=mock_llm_client)

    # Execute and assert that it raises an exception
    with pytest.raises(RuntimeError, match="Failed to generate lesson"):
        await workflow.generate_lesson(topic="", target_audience="beginner")


@pytest.mark.asyncio
async def test_workflow_state_initialization():
    """Test that the workflow state is properly initialized."""
    # Setup
    initial_state: WorkflowState = {
        "topic": "Python",
        "target_audience": "beginner",
        "context": "Introduction to programming",
        "validated_topic": None,
        "learning_objectives": None,
        "content_sections": None,
        "examples": None,
        "quiz_questions": None,
        "lesson": None,
        "metadata": {"key": "value"},
        "errors": []
    }
    
    # Assert
    assert initial_state["topic"] == "Python"
    assert initial_state["target_audience"] == "beginner"
    assert initial_state["context"] == "Introduction to programming"
    assert initial_state["validated_topic"] is None
    assert initial_state["learning_objectives"] is None
    assert initial_state["content_sections"] is None
    assert initial_state["examples"] is None
    assert initial_state["quiz_questions"] is None
    assert initial_state["lesson"] is None
    assert initial_state["metadata"]["key"] == "value"
    assert initial_state["errors"] == []

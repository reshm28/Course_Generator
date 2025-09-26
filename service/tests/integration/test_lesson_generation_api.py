"""Integration tests for the lesson generation API endpoint."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.domain.entities.lesson import (
    LessonContent,
    LearningObjective,
    Example,
    QuizQuestion,
    DifficultyLevel
)

# Create a test client
client = TestClient(app)

# Test data
TEST_LESSON = {
    "topic": "Introduction to Python",
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
    "summary": "A beginner's introduction to Python programming",
    "estimated_duration_minutes": 45,
    "metadata": {"generated_at": "2023-01-01T00:00:00Z"}
}


def test_generate_lesson_success():
    """Test successful lesson generation via the API."""
    # Mock the workflow to return our test lesson
    with patch(
        'app.interfaces.api.routes.lessons.LessonContentWorkflow',
        autospec=True
    ) as mock_workflow_class:
        # Setup mock workflow
        mock_workflow = mock_workflow_class.return_value
        mock_workflow.generate_lesson.return_value = LessonContent(**TEST_LESSON)
        
        # Make the API request
        response = client.post(
            "/lessons/generate",
            json={
                "topic": "Python",
                "difficulty": "beginner",
                "context": "Introduction to programming"
            }
        )
        
        # Assert the response
        assert response.status_code == 200
        data = response.json()
        assert data["topic"] == "Introduction to Python"
        assert len(data["learning_objectives"]) == 2
        # Check sections instead of content_sections
        assert len(data["sections"]) == 2
        assert len(data["examples"]) == 1
        assert len(data["quiz_questions"]) == 1
        
        # Verify the workflow was called with the correct parameters
        mock_workflow_class.assert_called_once()
        mock_workflow.generate_lesson.assert_awaited_once_with(
            topic="Python",
            target_audience="beginner",
            context="Introduction to programming"
        )


def test_generate_lesson_validation_error():
    """Test handling of validation errors in the API."""
    # Test with empty topic (should fail validation)
    response = client.post(
        "/lessons/generate",
        json={
            "topic": "",  # Invalid: empty topic
            "difficulty": "beginner"
        }
    )
    
    # Should return 500 Internal Server Error due to validation in the workflow
    assert response.status_code == 500
    assert "detail" in response.json()


def test_generate_lesson_workflow_error():
    """Test handling of workflow errors in the API."""
    with patch(
        'app.interfaces.api.routes.lessons.LessonContentWorkflow',
        autospec=True
    ) as mock_workflow_class:
        # Setup mock workflow to raise an exception
        mock_workflow = mock_workflow_class.return_value
        mock_workflow.generate_lesson.side_effect = ValueError("Failed to generate lesson")
        
        # Make the API request
        response = client.post(
            "/lessons/generate",
            json={
                "topic": "Python",
                "difficulty": "beginner"
            }
        )
        
        # Should return 500 Internal Server Error
        assert response.status_code == 500
        assert "Failed to generate lesson" in response.json()["detail"]


def test_generate_lesson_with_optional_fields():
    """Test lesson generation with all optional fields provided."""
    with patch(
        'app.interfaces.api.routes.lessons.LessonContentWorkflow',
        autospec=True
    ) as mock_workflow_class:
        # Setup mock workflow
        mock_workflow = mock_workflow_class.return_value
        mock_workflow.generate_lesson.return_value = LessonContent(**TEST_LESSON)
        
        # Make the API request with all optional fields
        response = client.post(
            "/lessons/generate",
            json={
                "topic": "Python",
                "difficulty": "beginner",
                "learning_objectives": ["Learn Python"],
                "context": "Test context",
                "include_quiz": True,
                "include_examples": True,
                "custom_instructions": "Focus on practical examples"
            }
        )
        
        # Assert the response
        assert response.status_code == 200
        
        # Verify the workflow was called with the correct parameters
        mock_workflow.generate_lesson.assert_awaited_once()
        call_args = mock_workflow.generate_lesson.call_args[1]
        assert call_args["topic"] == "Python"
        assert call_args["target_audience"] == "beginner"
        # The context should be just the original context, custom_instructions are not appended
        assert call_args["context"] == "Test context"

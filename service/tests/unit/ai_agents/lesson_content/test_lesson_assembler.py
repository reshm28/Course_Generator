"""Tests for the LessonAssemblerNode."""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.application.ai_agents.lesson_content.lesson_assembler import (
    LessonAssemblerNode,
    LessonAssemblerInput,
    LessonAssemblerOutput
)
from app.domain.entities.lesson import (
    LessonContent,
    LearningObjective,
    Example,
    QuizQuestion,
    DifficultyLevel
)


@pytest.mark.asyncio
async def test_lesson_assembler_process(mock_llm_client, mock_llm_response):
    """Test the process method of LessonAssemblerNode."""
    # Setup
    # The actual implementation doesn't use the LLM client, but the base class requires it
    node = LessonAssemblerNode(llm_client=mock_llm_client)
    
    # Create test data
    test_lesson = LessonContent(
        topic="Python Programming",
        difficulty=DifficultyLevel.BEGINNER,
        learning_objectives=[
            LearningObjective(
                description="Learn Python syntax",
                key_concept="Syntax"
            ),
            LearningObjective(
                description="Write functions",
                key_concept="Functions"
            )
        ],
        content_sections=[
            {"heading": "Introduction", "content": "Welcome to Python programming"},
            {"heading": "Basics", "content": "Variables and data types"}
        ],
        examples=[
            Example(
                title="Hello World",
                description="A simple Python program",
                key_takeaway="Basic program structure"
            )
        ],
        quiz_questions=[
            QuizQuestion(
                question="What is the correct syntax?",
                options=["A", "B", "C"],
                correct_answer=0,
                explanation="A is correct"
            )
        ],
        summary="A beginner's guide to Python",
        estimated_duration_minutes=60
    )
    
    # The actual implementation doesn't use the LLM client, so no need to mock it
    
    # Test input
    input_data = {
        "topic": "Python Programming",
        "target_audience": "beginner",
        "learning_objectives": [
            {"description": "Learn Python syntax", "key_concept": "Syntax"},
            {"description": "Write functions", "key_concept": "Functions"}
        ],
        "content_sections": [
            {"heading": "Introduction", "content": "Welcome to Python programming"},
            {"heading": "Basics", "content": "Variables and data types"}
        ],
        "examples": [
            {
                "title": "Hello World",
                "description": "A simple Python program",
                "key_takeaway": "Basic program structure"
            }
        ],
        "quiz_questions": [
            {
                "question": "What is the correct syntax?",
                "options": ["A", "B", "C"],
                "correct_answer": 0,
                "explanation": "A is correct"
            }
        ],
        "metadata": {
            "summary": "A beginner's guide to Python",
            "estimated_duration_minutes": 60
        }
    }
    
    # Execute
    result = await node.process(input_data)
    
    # Assert
    assert isinstance(result, LessonAssemblerOutput)
    assert isinstance(result.lesson, LessonContent)
    assert result.lesson.topic == "Python Programming"
    assert len(result.lesson.learning_objectives) == 2
    assert len(result.lesson.content_sections) == 2
    assert len(result.lesson.examples) == 1
    assert len(result.lesson.quiz_questions) == 1
    assert "metadata" in result.model_dump()
    
    # Verify the output contains the expected metadata
    assert "metadata" in result.model_dump()
    assert "generated_at" in result.metadata
    assert "components_used" in result.metadata
    assert "version" in result.metadata


def test_lesson_assembler_input_validation():
    """Test input validation for LessonAssemblerInput."""
    # Valid input
    valid_input = {
        "topic": "Python Basics",
        "target_audience": "beginner",
        "learning_objectives": [
            {"description": "Learn syntax", "key_concept": "Syntax"}
        ],
        "content_sections": [
            {"heading": "Intro", "content": "Content here"}
        ],
        "examples": [
            {"title": "Example", "description": "Example desc", "key_takeaway": "Key point"}
        ],
        "quiz_questions": [
            {
                "question": "Test?",
                "options": ["A", "B"],
                "correct_answer": 0,
                "explanation": "Explanation"
            }
        ],
        "metadata": {"key": "value"}
    }
    input_model = LessonAssemblerInput(**valid_input)
    assert input_model.topic == "Python Basics"
    assert len(input_model.learning_objectives) == 1
    assert len(input_model.content_sections) == 1
    assert len(input_model.examples) == 1
    assert len(input_model.quiz_questions) == 1
    
    # Test with default values
    minimal_input = {
        "topic": "Python",
        "learning_objectives": [{"description": "Test", "key_concept": "Test"}],
        "content_sections": [{"heading": "Test", "content": "Test"}],
        "examples": [],
        "quiz_questions": [],
        "metadata": {}
    }
    input_model = LessonAssemblerInput(**minimal_input)
    assert input_model.topic == "Python"
    assert input_model.target_audience == "beginner"  # default
    assert input_model.examples == []  # default
    assert input_model.quiz_questions == []  # default
    assert input_model.metadata == {}  # default

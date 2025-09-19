import pytest
from unittest.mock import AsyncMock, MagicMock

from app.domain.entities.course import Course, Module, Lesson
from app.infrastructure.llm.llm_client import BaseLLMClient
from app.application.use_cases.generate_course_content import GenerateCourseContentUseCase


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client for testing."""
    from app.application.workflows.course_generation.state import ModulePlan, CoursePlan, LessonContent, ReviewFeedback
    from app.domain.entities.course import Module, Lesson, Course
    
    client = AsyncMock(spec=BaseLLMClient)
    
    # Track the state of the course generation
    course_generated = False
    
    async def mock_generate_structured(output_model, prompt, **kwargs):
        nonlocal course_generated
        
        # First call - return the course plan
        if output_model.__name__ == "CoursePlan":
            return CoursePlan(
                course_title=f"Course on {kwargs.get('topic', 'Test Topic')}",
                course_description=f"A comprehensive course on {kwargs.get('topic', 'Test Topic')}",
                modules=[
                    ModulePlan(
                        title="Getting Started",
                        description="Introduction to the course topic.",
                        learning_objectives=["Understand the basics", "Get familiar with key concepts"],
                        num_lessons=1
                    )
                ]
            )
        # Second call - return the course structure
        elif output_model.__name__ == "Course" and not course_generated:
            course_generated = True
            return Course(
                topic=kwargs.get('topic', 'Test Topic'),
                modules=[
                    Module(
                        title="Getting Started",
                        description="Introduction to the course topic.",
                        lessons=[
                            Lesson(
                                title="Introduction to the Course",
                                summary="An introduction to the course topic.",
                                objectives=["Understand the basics", "Learn key concepts"],
                                key_points=["Point 1", "Point 2"]
                            )
                        ]
                    )
                ]
            )
        # For lesson content generation
        elif output_model.__name__ == "LessonContent":
            return LessonContent(
                title=kwargs.get('title', 'Test Lesson'),
                summary="A detailed summary of the lesson.",
                objectives=["Objective 1", "Objective 2"],
                key_points=["Key point 1", "Key point 2"]
            )
        # For review feedback
        elif output_model.__name__ == "ReviewFeedback":
            return ReviewFeedback(
                is_approved=True,
                feedback="Content looks good!",
                suggestions=[]
            )
        return output_model()  # type: ignore
    
    client.generate_structured.side_effect = mock_generate_structured
    return client


@pytest.mark.asyncio
async def test_generate_course_content(mock_llm_client):
    """Test that the use case generates a course with the expected structure."""
    # Arrange
    topic = "Test Topic"
    use_case = GenerateCourseContentUseCase(llm_client=mock_llm_client)
    
    # Act
    result = await use_case.execute(topic)
    
    # Assert
    assert "topic" in result
    assert result["topic"] == topic
    assert "modules" in result
    assert isinstance(result["modules"], list)
    assert len(result["modules"]) > 0
    
    # Check the first module
    module = result["modules"][0]
    assert "title" in module
    assert "description" in module
    assert "lessons" in module
    assert isinstance(module["lessons"], list)
    assert len(module["lessons"]) > 0
    
    # Check the first lesson
    lesson = module["lessons"][0]
    assert "title" in lesson
    assert "summary" in lesson
    assert "objectives" in lesson
    assert isinstance(lesson["objectives"], list)
    assert "key_points" in lesson
    assert isinstance(lesson["key_points"], list)


@pytest.mark.asyncio
async def test_generate_course_content_with_error(mock_llm_client):
    """Test error handling in the use case."""
    # Arrange
    topic = "Test Topic"
    
    # Configure the mock to raise an exception
    mock_llm_client.generate_structured.side_effect = Exception("Test error")
    
    use_case = GenerateCourseContentUseCase(llm_client=mock_llm_client)
    
    # Act & Assert
    with pytest.raises(RuntimeError) as exc_info:
        await use_case.execute(topic)
    
    assert "Failed to generate course" in str(exc_info.value)

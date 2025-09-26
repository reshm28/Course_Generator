from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
import logging

from app.application.workflows.course_generation.lesson_content_workflow import LessonContentWorkflow
from app.infrastructure.llm.llm_client import get_llm_client
from app.interfaces.api.schemas.lesson import (
    GenerateLessonRequest,
    GenerateLessonResponse,
    LearningObjectiveResponse,
    ExampleResponse,
    QuizQuestionResponse,
    LessonSectionResponse
)
from app.domain.entities.lesson import (
    LessonContent,
    LearningObjective,
    Example,
    QuizQuestion
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/lessons", tags=["lessons"])


def _map_learning_objective_to_response(obj: LearningObjective) -> LearningObjectiveResponse:
    """Map a domain LearningObjective to a response model."""
    return LearningObjectiveResponse(
        description=obj.description,
        key_concept=obj.key_concept
    )


def _map_example_to_response(example: Example) -> ExampleResponse:
    """Map a domain Example to a response model."""
    return ExampleResponse(
        title=example.title,
        description=example.description,
        key_takeaway=example.key_takeaway
    )


def _map_quiz_question_to_response(question: QuizQuestion) -> QuizQuestionResponse:
    """Map a domain QuizQuestion to a response model."""
    return QuizQuestionResponse(
        question=question.question,
        options=question.options,
        correct_answer=question.correct_answer,
        explanation=question.explanation
    )


def _map_lesson_to_response(lesson: LessonContent) -> GenerateLessonResponse:
    """Map a domain LessonContent to a response model."""
    return GenerateLessonResponse(
        topic=lesson.topic,
        difficulty=lesson.difficulty,
        learning_objectives=[
            _map_learning_objective_to_response(obj) 
            for obj in lesson.learning_objectives
        ],
        sections=[
            LessonSectionResponse(
                heading=section.get("heading", ""),
                content=section.get("content", ""),
                key_points=section.get("key_points", [])
            )
            for section in lesson.content_sections
        ],
        examples=[
            _map_example_to_response(example)
            for example in lesson.examples
        ],
        quiz_questions=[
            _map_quiz_question_to_response(question)
            for question in lesson.quiz_questions
        ],
        summary=lesson.summary,
        estimated_duration_minutes=lesson.estimated_duration_minutes,
        metadata={
            "generated_at": "2023-01-01T00:00:00Z",  # Should be current timestamp in production
            "version": "1.0.0"
        }
    )


@router.post(
    "/generate",
    response_model=GenerateLessonResponse,
    summary="Generate a lesson on a given topic",
    description="""
    Generate a complete, structured lesson on the specified topic.
    The lesson will include learning objectives, content sections, examples, and quiz questions.
    """
)
async def generate_lesson(
    request: GenerateLessonRequest,
    llm_client: Any = Depends(get_llm_client)
) -> GenerateLessonResponse:
    """Generate a lesson on the given topic.
    
    Args:
        request: The lesson generation request
        llm_client: The LLM client (injected dependency)
        
    Returns:
        A complete, structured lesson on the requested topic
        
    Raises:
        HTTPException: If there's an error generating the lesson
    """
    try:
        logger.info(f"Generating lesson on topic: {request.topic}")
        
        # Initialize the workflow
        workflow = LessonContentWorkflow(
            llm_client=llm_client,
            model="gpt-4"  # Could be made configurable
        )
        
        # Generate the lesson
        lesson = await workflow.generate_lesson(
            topic=request.topic,
            target_audience=request.difficulty.value,
            context=request.context
        )
        
        # Map the domain model to the response model
        return _map_lesson_to_response(lesson)
        
    except Exception as e:
        logger.error(f"Error generating lesson: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate lesson: {str(e)}"
        )

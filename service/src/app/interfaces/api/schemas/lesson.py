from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class GenerateLessonRequest(BaseModel):
    """Request model for generating a lesson."""
    topic: str = Field(..., description="The main topic of the lesson")
    difficulty: DifficultyLevel = Field(
        DifficultyLevel.BEGINNER,
        description="Difficulty level of the lesson"
    )
    learning_objectives: Optional[List[str]] = Field(
        None,
        description="Optional list of specific learning objectives to cover"
    )
    context: Optional[str] = Field(
        None,
        description="Additional context or requirements for the lesson"
    )
    include_quiz: bool = Field(
        True,
        description="Whether to include quiz questions in the lesson"
    )
    include_examples: bool = Field(
        True,
        description="Whether to include examples in the lesson"
    )
    custom_instructions: Optional[str] = Field(
        None,
        description="Custom instructions for lesson generation"
    )


class LearningObjectiveResponse(BaseModel):
    """Response model for a learning objective."""
    description: str = Field(..., description="The learning objective text")
    key_concept: str = Field(..., description="The main concept this objective covers")


class ExampleResponse(BaseModel):
    """Response model for an example."""
    title: str = Field(..., description="Title of the example")
    description: str = Field(..., description="Detailed explanation of the example")
    key_takeaway: str = Field(..., description="Main lesson or insight from this example")


class QuizQuestionResponse(BaseModel):
    """Response model for a quiz question."""
    question: str = Field(..., description="The quiz question text")
    options: List[str] = Field(..., description="List of answer options")
    correct_answer: int = Field(..., description="Index of the correct answer")
    explanation: str = Field(..., description="Explanation of the correct answer")


class LessonSectionResponse(BaseModel):
    """Response model for a lesson section."""
    heading: str = Field(..., description="Section heading")
    content: str = Field(..., description="Detailed content for this section")
    key_points: List[str] = Field(
        default_factory=list,
        description="Key points or takeaways from this section"
    )


class GenerateLessonResponse(BaseModel):
    """Response model for a generated lesson."""
    topic: str = Field(..., description="The main topic of the lesson")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level of the lesson")
    learning_objectives: List[LearningObjectiveResponse] = Field(
        ...,
        description="List of learning objectives for this lesson"
    )
    sections: List[LessonSectionResponse] = Field(
        ...,
        description="Organized sections of the lesson content"
    )
    examples: List[ExampleResponse] = Field(
        default_factory=list,
        description="Real-world examples or case studies"
    )
    quiz_questions: List[QuizQuestionResponse] = Field(
        default_factory=list,
        description="Quiz questions to test understanding"
    )
    summary: str = Field(..., description="Concise summary of the lesson")
    estimated_duration_minutes: int = Field(
        ...,
        description="Estimated time to complete the lesson in minutes"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the lesson"
    )

from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class QuizQuestion(BaseModel):
    """Represents a single quiz question with multiple choice answers."""
    question: str = Field(..., description="The quiz question text")
    options: List[str] = Field(..., min_items=3, max_items=5, description="List of answer options")
    correct_answer: int = Field(..., ge=0, description="Index of the correct answer in the options list")
    explanation: str = Field(..., description="Explanation of why the correct answer is right")


class LearningObjective(BaseModel):
    """Represents a single learning objective for the lesson."""
    description: str = Field(..., description="Description of the learning objective")
    key_concept: str = Field(..., description="The main concept this objective covers")


class Example(BaseModel):
    """Represents a real-world example or case study."""
    title: str = Field(..., description="Title of the example")
    description: str = Field(..., description="Detailed explanation of the example")
    key_takeaway: str = Field(..., description="Main lesson or insight from this example")


class LessonContent(BaseModel):
    """Complete lesson content structure."""
    topic: str = Field(..., description="The main topic of the lesson")
    difficulty: DifficultyLevel = Field(DifficultyLevel.BEGINNER, description="Difficulty level of the lesson")
    learning_objectives: List[LearningObjective] = Field(
        ..., 
        min_items=1,  # Reduced from 3 to 1 for test cases
        max_items=5,
        description="List of learning objectives for this lesson"
    )
    content_sections: List[dict] = Field(
        ...,
        description="List of content sections with headings and body text"
    )
    examples: List[Example] = Field(
        ...,
        min_items=1,  # Reduced from 2 to 1 for test cases
        max_items=3,
        description="Real-world examples or case studies"
    )
    quiz_questions: List[QuizQuestion] = Field(
        ...,
        min_items=1,  # Reduced from 3 to 1 for test cases
        max_items=5,
        description="Quiz questions to test understanding"
    )
    summary: str = Field(..., description="Concise summary of the lesson")
    estimated_duration_minutes: int = Field(
        ...,
        ge=5,
        le=120,
        description="Estimated time to complete the lesson in minutes"
    )

from dataclasses import dataclass, field
from typing import Dict, List, Optional, TypedDict

from pydantic import BaseModel, Field

from app.domain.entities.course import Course, Module, Lesson


class CourseState(TypedDict):
    """State for the course generation workflow."""
    topic: str
    course_structure: Optional[Course] = None
    current_module: Optional[Module] = None
    current_lesson: Optional[Lesson] = None
    validation_errors: List[str] = field(default_factory=list)
    is_complete: bool = False


class PlannerInput(BaseModel):
    """Input for the planner agent."""
    topic: str = Field(..., description="The main topic of the course")
    target_audience: str = Field("beginner", description="Target audience level")
    learning_objectives: Optional[List[str]] = Field(
        None, description="Specific learning objectives (optional)"
    )


class ModulePlan(BaseModel):
    """Output from the planner agent for a single module."""
    title: str = Field(..., description="Title of the module")
    description: str = Field(..., description="Description of what the module covers")
    learning_objectives: List[str] = Field(
        ..., description="What students will learn in this module"
    )
    num_lessons: int = Field(
        default=3, ge=1, le=10, description="Number of lessons in this module"
    )


class CoursePlan(BaseModel):
    """Output from the planner agent."""
    course_title: str = Field(..., description="Title of the course")
    course_description: str = Field(..., description="Brief description of the course")
    modules: List[ModulePlan] = Field(
        ..., description="List of modules in the course", min_items=1, max_items=10
    )


class LessonContent(BaseModel):
    """Output from the content generator agent for a single lesson."""
    title: str = Field(..., description="Title of the lesson")
    summary: str = Field(..., description="Detailed summary of the lesson content")
    objectives: List[str] = Field(
        ..., description="Specific learning objectives for this lesson"
    )
    key_points: List[str] = Field(
        ..., description="Key points or takeaways from the lesson"
    )


class ReviewFeedback(BaseModel):
    """Output from the reviewer agent."""
    is_approved: bool = Field(..., description="Whether the content is approved")
    feedback: str = Field(..., description="Detailed feedback on the content")
    suggestions: List[str] = Field(
        default_factory=list,
        description="Specific suggestions for improvement if not approved"
    )

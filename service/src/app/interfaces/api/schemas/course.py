from typing import List, Optional

from pydantic import BaseModel, Field


class LessonSchema(BaseModel):
    """Schema for a lesson in the course."""
    title: str = Field(..., description="Title of the lesson")
    summary: str = Field(..., description="Detailed summary of the lesson content")
    objectives: List[str] = Field(
        ..., description="Specific learning objectives for this lesson"
    )
    key_points: List[str] = Field(
        ..., description="Key points or takeaways from the lesson"
    )


class ModuleSchema(BaseModel):
    """Schema for a module in the course."""
    title: str = Field(..., description="Title of the module")
    description: str = Field(..., description="Description of what the module covers")
    lessons: List[LessonSchema] = Field(
        default_factory=list, description="Lessons in this module"
    )


class CourseSchema(BaseModel):
    """Schema for the generated course."""
    topic: str = Field(..., description="Main topic of the course")
    modules: List[ModuleSchema] = Field(
        default_factory=list, description="Modules in the course"
    )


class GenerateCourseRequest(BaseModel):
    """Request schema for generating a course."""
    topic: str = Field(..., description="The main topic of the course")
    model: Optional[str] = Field(
        None, description="The LLM model to use for generation (e.g., gpt-4, gpt-3.5-turbo)"
    )


class GenerateCourseResponse(BaseModel):
    """Response schema for the generated course."""
    success: bool = Field(..., description="Whether the generation was successful")
    course: Optional[CourseSchema] = Field(
        None, description="The generated course content"
    )
    error: Optional[str] = Field(
        None, description="Error message if generation failed"
    )

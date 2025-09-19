# API schemas package
from pydantic import BaseModel, Field

# Import all schemas here to make them available when importing from app.interfaces.api.schemas
from .course import (
    LessonSchema,
    ModuleSchema,
    CourseSchema,
    GenerateCourseRequest,
    GenerateCourseResponse
)

# Original schemas that were in schemas.py
class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")


class EchoQuery(BaseModel):
    text: str = Field(..., description="Text to echo via LangGraph")


class EchoResponse(BaseModel):
    result: str


__all__ = [
    # Course schemas
    'LessonSchema',
    'ModuleSchema',
    'CourseSchema',
    'GenerateCourseRequest',
    'GenerateCourseResponse',
    # Original schemas
    'HealthResponse',
    'EchoQuery',
    'EchoResponse'
]

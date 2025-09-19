from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.infrastructure.llm.llm_client import SimpleLLMClient
from app.application.use_cases.generate_course_content import GenerateCourseContentUseCase
from app.interfaces.api.schemas.course import (
    GenerateCourseRequest,
    GenerateCourseResponse,
    CourseSchema
)

router = APIRouter(prefix="/api/courses", tags=["courses"])


def get_llm_client():
    """Dependency to get an LLM client."""
    # In a production app, you might want to use dependency injection
    # to provide different LLM clients based on configuration
    return SimpleLLMClient()


@router.post(
    "/generate",
    response_model=GenerateCourseResponse,
    summary="Generate a course on a given topic",
    description="""
    Generate a structured course on the specified topic using AI.
    The course will include modules, lessons, objectives, and key points.
    """
)
async def generate_course(
    request: GenerateCourseRequest,
    llm_client = Depends(get_llm_client)
) -> GenerateCourseResponse:
    """Generate a course on the given topic."""
    try:
        use_case = GenerateCourseContentUseCase(
            llm_client=llm_client,
            model=request.model or "gpt-4"
        )
        
        # Generate the course content
        course_data = await use_case.execute(request.topic)
        
        return GenerateCourseResponse(
            success=True,
            course=CourseSchema(**course_data)
        )
        
    except Exception as e:
        # Log the error (in a real app, you'd use proper logging)
        print(f"Error generating course: {str(e)}")
        
        # Return an error response
        return GenerateCourseResponse(
            success=False,
            error=f"Failed to generate course: {str(e)}"
        )

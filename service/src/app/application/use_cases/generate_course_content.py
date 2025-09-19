from typing import Optional

from app.domain.entities.course import Course
from app.infrastructure.llm.llm_client import BaseLLMClient
from app.application.workflows.course_generation.workflow import CourseGenerationWorkflow


class GenerateCourseContentUseCase:
    """Use case for generating course content using AI agents."""
    
    def __init__(self, llm_client: BaseLLMClient, model: str = "gpt-4"):
        """Initialize with an LLM client and model name."""
        self.llm_client = llm_client
        self.model = model
    
    async def execute(self, topic: str) -> dict:
        """
        Generate a course on the given topic.
        
        Args:
            topic: The main topic of the course
            
        Returns:
            dict: The generated course content
        """
        # Initialize the workflow
        workflow = CourseGenerationWorkflow(self.llm_client, self.model)
        
        try:
            # Run the workflow
            result = await workflow.generate_course(topic)
            
            # Extract the course structure
            course = result.get("course_structure")
            if not course:
                raise ValueError("Failed to generate course content")
            
            # Convert the course to a dictionary
            return self._format_course(course)
            
        except Exception as e:
            # Log the error and re-raise
            # In a production app, you would want to use proper error handling and logging
            raise RuntimeError(f"Failed to generate course: {str(e)}")
    
    def _format_course(self, course) -> dict:
        """Format the course object into a dictionary that matches CourseSchema."""
        # Ensure we have a valid course with modules
        if not hasattr(course, 'modules') or not course.modules:
            raise ValueError("Course must have at least one module")
            
        return {
            "topic": course.topic,
            "modules": [
                {
                    "title": module.title,
                    "description": module.description or f"Module on {module.title}",
                    "lessons": [
                        {
                            "title": lesson.title,
                            "summary": lesson.summary,
                            "objectives": lesson.objectives,
                            "key_points": lesson.key_points,
                        }
                        for lesson in module.lessons
                    ]
                }
                for module in course.modules
            ]
        }

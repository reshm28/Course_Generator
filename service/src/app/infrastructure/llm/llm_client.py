import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel


@runtime_checkable
class BaseLLMClient(Protocol):
    """Protocol defining the interface for LLM clients."""

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Generate text from a prompt."""
        ...

    async def generate_structured(
        self,
        output_model: type[BaseModel],
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> BaseModel:
        """Generate structured output following a Pydantic model."""
        ...


class SimpleLLMClient(BaseLLMClient):
    """Simple implementation of LLM client for testing and development."""

    def __init__(self, model: str = "gpt-4"):
        self.model = model

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        # In a real implementation, this would call an actual LLM API
        return f"Generated response for prompt: {prompt[:50]}..."

    async def generate_structured(
        self,
        output_model: type[BaseModel],
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> BaseModel:
        # In a real implementation, this would call an actual LLM API with structured output
        # For now, return a mock response that matches the output_model
        if output_model.__name__ == "ReviewFeedback":
            # For simplicity, always approve the content in the mock
            return output_model(
                is_approved=True,
                feedback="The content looks good and meets all the requirements. No changes needed."
            )
        if output_model.__name__ == "LessonContent":
            # Extract course and module info from the prompt
            course_match = re.search(r"Course: (.+?)\n", prompt)
            module_match = re.search(r"Module: (.+?)\n", prompt)
            lesson_match = re.search(r"Lesson: (.+?)\n", prompt)
            
            course = course_match.group(1) if course_match else "the course"
            module = module_match.group(1) if module_match else "this module"
            lesson = lesson_match.group(1) if lesson_match else "this lesson"
            
            return output_model(
                title=lesson,
                summary=f"This is a detailed summary of {lesson} in the {module} of {course}. "
                       f"It covers essential concepts and provides a comprehensive overview.",
                objectives=[
                    f"Understand the key concepts of {lesson}",
                    f"Learn how to apply {lesson} in practical scenarios",
                    f"Master the fundamentals of {lesson} in the context of {module}"
                ],
                key_points=[
                    f"Key concept 1 about {lesson}",
                    f"Important consideration for {lesson}",
                    f"Practical application of {lesson}",
                    f"Common challenges in {lesson}",
                    f"Best practices for {lesson}"
                ]
            )
        elif output_model.__name__ == "CoursePlan":
            from app.application.workflows.course_generation.state import ModulePlan
            
            # Create a mock course plan
            topic = kwargs.get("topic", "Introduction to Topic")
            return output_model(
                course_title=f"{topic} Course",
                course_description=f"A comprehensive course on {topic}",
                modules=[
                    ModulePlan(
                        title="Getting Started",
                        description=f"Introduction to {topic}",
                        learning_objectives=[
                            f"Understand the basics of {topic}",
                            f"Learn key concepts in {topic}",
                            "Get familiar with the course structure"
                        ],
                        num_lessons=3
                    ),
                    ModulePlan(
                        title="Advanced Concepts",
                        description=f"Deeper dive into {topic}",
                        learning_objectives=[
                            f"Explore advanced topics in {topic}",
                            f"Apply {topic} concepts to real-world scenarios",
                            "Develop practical skills"
                        ],
                        num_lessons=4
                    )
                ]
            )
        elif output_model.__name__ == "CourseStructure":
            from app.domain.entities.course import Course, Module, Lesson
            
            # Create a simple course structure for testing
            lesson = Lesson(
                title="Introduction to Topic",
                summary="An introduction to the topic.",
                objectives=["Understand the basics", "Learn key concepts"],
                key_points=["Point 1", "Point 2"]
            )
            module = Module(
                title="Getting Started",
                description="Introduction to the course topic.",
                lessons=[lesson]
            )
            course = Course(
                topic=prompt.split(":")[-1].strip(),
                modules=[module]
            )
            return course
        
        # Fallback to a simple response
        return output_model()  # type: ignore

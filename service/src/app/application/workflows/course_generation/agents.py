from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, cast

from pydantic import BaseModel, Field

from app.domain.entities.course import Course, Module, Lesson
from app.infrastructure.llm.llm_client import BaseLLMClient
from .state import (
    CourseState, 
    PlannerInput, 
    CoursePlan, 
    ModulePlan, 
    LessonContent, 
    ReviewFeedback
)


class BaseAgent(ABC):
    """Base class for all agents in the workflow."""
    
    def __init__(self, llm_client: BaseLLMClient, model: str = "gpt-4"):
        self.llm = llm_client
        self.model = model
    
    async def process(self, state: CourseState) -> CourseState:
        """Process the current state and return an updated state."""
        raise NotImplementedError


class PlannerAgent(BaseAgent):
    """Agent responsible for planning the course structure."""
    
    async def process(self, state: CourseState) -> CourseState:
        """Generate a course plan based on the topic."""
        if not state.get("topic"):
            raise ValueError("Topic is required for planning")
            
        # Prepare the prompt with explicit structure requirements
        prompt = f"""
        You are an expert course planner. Create a detailed course plan for the following topic:
        
        Topic: {state["topic"]}
        
        Please provide a comprehensive course structure with the following requirements:
        
        1. Course Title: A clear, engaging title for the course
        2. Course Description: A brief but comprehensive description of what the course covers
        3. Modules: A list of 3-5 modules, each with:
           - Title: Clear and descriptive
           - Description: What the module covers
           - Learning Objectives: 3-5 specific, measurable learning outcomes
           - Number of Lessons: 3-5 lessons per module
        
        The structure must include all these fields exactly as specified.
        """
        
        try:
            # Generate the course plan using the LLM
            plan = await self.llm.generate_structured(
                output_model=CoursePlan,
                prompt=prompt,
                model=self.model,
                temperature=0.7,
                topic=state["topic"]  # Pass the topic to the LLM
            )
            print(f"Generated plan: {plan}")
            print(f"Plan type: {type(plan)}")
            print(f"Plan dict: {plan.dict() if hasattr(plan, 'dict') else 'No dict method'}")
        except Exception as e:
            print(f"Error generating plan: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            if hasattr(e, 'errors'):
                print(f"Validation errors: {e.errors()}")
            raise
        
        # Create modules from the plan
        modules = []
        for i, module_plan in enumerate(plan.modules):
            # Create lessons for the module
            lessons = [
                Lesson(
                    title=f"Lesson {j + 1}",
                    summary=f"Summary for lesson {j + 1} of {module_plan.title}",
                    objectives=module_plan.learning_objectives,
                    key_points=[f"Key point {k + 1}" for k in range(3)]
                )
                for j in range(module_plan.num_lessons)
            ]
            
            # Create the module
            module = Module(
                title=module_plan.title,
                description=module_plan.description,
                lessons=lessons
            )
            modules.append(module)
        
        # Create the course with modules
        course = Course(
            topic=state["topic"],
            modules=modules,
        )
        
        # Update the state with the course structure
        state["course_structure"] = course
        return state


class ContentGeneratorAgent(BaseAgent):
    """Agent responsible for generating detailed lesson content."""
    
    async def process(self, state: CourseState) -> CourseState:
        """Generate detailed content for the current module or lesson."""
        if not state.get("course_structure"):
            raise ValueError("Course structure is required for content generation")
            
        course = state["course_structure"]
        
        # If no current module, start with the first one
        if not state.get("current_module") and course.modules:
            state["current_module"] = course.modules[0]
            
        current_module = state["current_module"]
        
        # If no current lesson, start with the first one in the module
        if not state.get("current_lesson") and current_module.lessons:
            state["current_lesson"] = current_module.lessons[0]
        
        # If we have a current lesson, generate content for it
        if state.get("current_lesson"):
            lesson = state["current_lesson"]
            
            prompt = f"""
            You are an expert course content creator. Generate detailed content for the following lesson:
            
            Course: {course.topic}
            Module: {current_module.title}
            Lesson: {lesson.title}
            
            Please provide a comprehensive lesson with objectives, key points, and a summary.
            """
            
            # Generate the lesson content using the LLM
            content = await self.llm.generate_structured(
                output_model=LessonContent,
                prompt=prompt,
                model=self.model,
                temperature=0.7
            )
            
            # Update the lesson with the generated content
            lesson.summary = content.summary
            lesson.objectives = content.objectives
            lesson.key_points = content.key_points
            
            # Move to the next lesson or module
            current_lesson_idx = current_module.lessons.index(lesson)
            if current_lesson_idx < len(current_module.lessons) - 1:
                state["current_lesson"] = current_module.lessons[current_lesson_idx + 1]
            else:
                # No more lessons in this module, move to the next one
                current_module_idx = course.modules.index(current_module)
                if current_module_idx < len(course.modules) - 1:
                    state["current_module"] = course.modules[current_module_idx + 1]
                    state["current_lesson"] = state["current_module"].lessons[0] if state["current_module"].lessons else None
                else:
                    # No more modules, we're done
                    state["is_complete"] = True
        
        return state


class ReviewerAgent(BaseAgent):
    """Agent responsible for reviewing and providing feedback on generated content."""
    
    async def process(self, state: CourseState) -> CourseState:
        """Review the generated content and provide feedback."""
        if not state.get("course_structure"):
            raise ValueError("Course structure is required for review")
            
        course = state["course_structure"]
        
        # If we have a current lesson, review it
        if state.get("current_lesson"):
            lesson = state["current_lesson"]
            current_module = state["current_module"]
            
            prompt = f"""
            You are an expert course reviewer. Please review the following lesson content:
            
            Course: {course.topic}
            Module: {current_module.title}
            Lesson: {lesson.title}
            
            Lesson Summary: {lesson.summary}
            Objectives: {', '.join(lesson.objectives)}
            Key Points: {', '.join(lesson.key_points)}
            
            Please provide detailed feedback on the quality, accuracy, and educational value of this content.
            Be specific about any issues and suggest improvements.
            """
            
            # Generate the review feedback using the LLM
            feedback = await self.llm.generate_structured(
                output_model=ReviewFeedback,
                prompt=prompt,
                model=self.model,
                temperature=0.3  # Lower temperature for more consistent reviews
            )
            
            # If the content is not approved, add the feedback to the state
            if not feedback.is_approved:
                if "validation_errors" not in state:
                    state["validation_errors"] = []
                state["validation_errors"].append(
                    f"Review for {lesson.title}: {feedback.feedback}"
                )
                
                # If there are suggestions, apply them to the lesson
                for suggestion in feedback.suggestions:
                    # In a real implementation, you would apply the suggestions to the lesson
                    pass
        
        return state

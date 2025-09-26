from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from .base_agent import BaseLessonAgent
from app.domain.entities.lesson import (
    LessonContent, 
    LearningObjective, 
    Example, 
    QuizQuestion,
    DifficultyLevel
)


class LessonAssemblerInput(BaseModel):
    """Input model for LessonAssemblerNode."""
    topic: str = Field(..., description="The lesson topic")
    target_audience: str = Field("beginner", description="Target audience level")
    learning_objectives: List[Dict[str, str]] = Field(
        ...,
        description="List of learning objectives with their key concepts"
    )
    content_sections: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lesson content sections"
    )
    examples: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Generated examples and case studies"
    )
    quiz_questions: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Generated quiz questions"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the lesson"
    )


class LessonAssemblerOutput(BaseModel):
    """Output model for LessonAssemblerNode."""
    lesson: LessonContent = Field(..., description="The complete, structured lesson")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the generation process"
    )


class LessonAssemblerNode(BaseLessonAgent[LessonAssemblerOutput]):
    """Assembles all lesson components into a coherent, well-structured lesson."""
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert instructional designer. Your task is to assemble all the 
components of a lesson into a coherent, well-structured format.

Your responsibilities include:
1. Ensuring the lesson flows logically from introduction to conclusion
2. Verifying that all learning objectives are adequately covered
3. Integrating examples and exercises at appropriate points
4. Ensuring the content is appropriate for the target audience
5. Adding any necessary transitions or additional context
6. Formatting the content for optimal learning

Create a polished, professional lesson that is ready for delivery to students."""

    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build a detailed prompt for assembling the lesson."""
        objectives = "\n".join(
            f"- {obj.get('description', '')} (Key Concept: {obj.get('key_concept', 'N/A')})" 
            for obj in input_data.get("learning_objectives", [])
        )
        
        sections = "\n".join(
            f"- {section.get('heading', 'Untitled Section')}: {section.get('content', '')[:100]}..."
            for section in input_data.get("content_sections", [])[:3]  # Just show first few sections
        )
        
        example_count = len(input_data.get("examples", []))
        question_count = len(input_data.get("quiz_questions", []))
        
        return (
            f"{self.system_prompt}\n\n"
            f"Topic: {input_data.get('topic', '')}\n"
            f"Target Audience: {input_data.get('target_audience', 'beginner')}\n\n"
            f"Learning Objectives:\n{objectives}\n\n"
            f"Content Sections ({len(input_data.get('content_sections', []))}):\n{sections}\n\n"
            f"Examples: {example_count} examples provided\n"
            f"Assessment: {question_count} quiz questions provided\n\n"
            "Please assemble these components into a well-structured lesson. Ensure the content flows logically, "
            "all learning objectives are addressed, and the material is appropriate for the target audience. "
            "Add any necessary transitions, summaries, or additional context to create a cohesive learning experience."
        )
    
    async def process(self, input_data: Dict[str, Any]) -> LessonAssemblerOutput:
        """Process the lesson assembly request."""
        # Validate and prepare input
        input_model = LessonAssemblerInput(**input_data)
        
        # Convert input data to domain models
        learning_objectives = [
            LearningObjective(
                description=obj.get('description', ''),
                key_concept=obj.get('key_concept', '')
            )
            for obj in input_model.learning_objectives
        ]
        
        examples = [
            Example(
                title=ex.get('title', ''),
                description=ex.get('description', ''),
                key_takeaway=ex.get('key_takeaway', '')
            )
            for ex in input_model.examples
        ]
        
        quiz_questions = [
            QuizQuestion(
                question=q.get('question', ''),
                options=q.get('options', []),
                correct_answer=q.get('correct_answer', 0),
                explanation=q.get('explanation', '')
            )
            for q in input_model.quiz_questions
        ]
        
        # Create the lesson content
        lesson = LessonContent(
            topic=input_model.topic,
            difficulty=DifficultyLevel(input_model.target_audience.lower()),
            learning_objectives=learning_objectives,
            content_sections=input_model.content_sections,
            examples=examples,
            quiz_questions=quiz_questions,
            summary=input_model.metadata.get('summary', ''),
            estimated_duration_minutes=input_model.metadata.get('estimated_duration_minutes', 30)
        )
        
        return LessonAssemblerOutput(
            lesson=lesson,
            metadata={
                "generated_at": "2023-01-01T00:00:00Z",  # Should be current timestamp in production
                "components_used": ["learning_objectives", "content_sections", "examples", "quiz_questions"],
                "version": "1.0.0"
            }
        )

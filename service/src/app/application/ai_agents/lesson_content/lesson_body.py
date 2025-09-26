from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .base_agent import BaseLessonAgent
from app.domain.entities.lesson import LearningObjective


class LessonBodyInput(BaseModel):
    """Input model for LessonBodyNode."""
    topic: str = Field(..., description="The lesson topic")
    target_audience: str = Field("beginner", description="Target audience level")
    learning_objectives: List[LearningObjective] = Field(
        ...,
        description="List of learning objectives to cover"
    )
    scope: str = Field(..., description="The scope of the lesson")
    key_terms: List[str] = Field(
        default_factory=list,
        description="Key terms that should be included and explained"
    )


class LessonSection(BaseModel):
    """Represents a section of the lesson content."""
    heading: str = Field(..., description="Section heading")
    content: str = Field(..., description="Detailed content for this section")
    key_points: List[str] = Field(
        default_factory=list,
        description="Key points or takeaways from this section"
    )
    learning_objectives_covered: List[str] = Field(
        default_factory=list,
        description="IDs or descriptions of learning objectives covered in this section"
    )


class LessonBodyOutput(BaseModel):
    """Output model for LessonBodyNode."""
    sections: List[LessonSection] = Field(
        ...,
        min_items=3,
        description="Organized sections of the lesson content"
    )
    estimated_duration_minutes: int = Field(
        ...,
        ge=10,
        le=120,
        description="Estimated time to complete the lesson in minutes"
    )
    key_terms: Dict[str, str] = Field(
        default_factory=dict,
        description="Definitions of key terms used in the lesson"
    )


class LessonBodyNode(BaseLessonAgent[LessonBodyOutput]):
    """Generates the main content body for a lesson."""
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert educator and curriculum developer. Your task is to create engaging, 
well-structured lesson content based on the provided learning objectives and topic.

For each lesson, you should:
1. Break down the content into logical sections with clear headings
2. Ensure all learning objectives are adequately covered
3. Use clear, concise language appropriate for the target audience
4. Include examples, analogies, and explanations as needed
5. Highlight key terms and provide definitions
6. Structure the content to facilitate learning and retention

Each section should have:
- A clear, descriptive heading
- Well-organized paragraphs of content
- Bullet points for key information
- References to which learning objectives are being addressed"""

    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build a detailed prompt for generating lesson content."""
        # Handle both LearningObjective objects and dictionaries
        learning_objectives = input_data.get("learning_objectives", [])
        objectives = []
        for obj in learning_objectives:
            if hasattr(obj, 'description'):
                # It's a LearningObjective object
                objectives.append(f"- {obj.description}")
            elif isinstance(obj, dict) and 'description' in obj:
                # It's a dictionary with a description key
                objectives.append(f"- {obj['description']}")
            else:
                # Fallback for any other format
                objectives.append(f"- {str(obj)}")
        
        objectives_str = "\n".join(objectives) or "No learning objectives provided"
        
        key_terms = "\n".join(
            f"- {term}" 
            for term in input_data.get("key_terms", [])
        ) or "No key terms provided"
        
        return (
            f"{self.system_prompt}\n\n"
            f"Topic: {input_data.get('topic', '')}\n"
            f"Target Audience: {input_data.get('target_audience', 'beginner')}\n"
            f"Lesson Scope: {input_data.get('scope', '')}\n\n"
            f"Learning Objectives to Cover:\n{objectives_str}\n\n"
            f"Key Terms to Include:\n{key_terms}\n\n"
            "Please generate comprehensive lesson content that covers all the learning objectives. "
            "Organize it into logical sections with clear headings and subheadings. "
            "Include examples and explanations as needed for the target audience."
        )
    
    async def process(self, input_data: Dict[str, Any]) -> LessonBodyOutput:
        """Process the lesson body generation request."""
        # Validate input
        input_model = LessonBodyInput(**input_data)
        
        # Prepare the input for the LLM
        llm_input = {
            "topic": input_model.topic,
            "target_audience": input_model.target_audience,
            "learning_objectives": [
                {"description": obj.description, "key_concept": obj.key_concept}
                for obj in input_model.learning_objectives
            ],
            "scope": input_model.scope,
            "key_terms": input_model.key_terms
        }
        
        # Call the parent's process method to handle the LLM interaction
        return await super().process(llm_input)

from typing import Dict, Any, List
from pydantic import BaseModel, Field
from .base_agent import BaseLessonAgent
from app.domain.entities.lesson import LearningObjective


class LearningObjectivesInput(BaseModel):
    """Input model for LearningObjectivesNode."""
    topic: str = Field(..., description="The lesson topic")
    target_audience: str = Field("beginner", description="Target audience level")
    scope: str = Field(..., description="The scope of the lesson")
    prerequisites: List[str] = Field(default_factory=list, description="List of prerequisites")


class LearningObjectivesOutput(BaseModel):
    """Output model for LearningObjectivesNode."""
    objectives: List[LearningObjective] = Field(
        ...,
        min_items=3,
        max_items=5,
        description="Generated learning objectives"
    )
    difficulty: str = Field(
        ...,
        description="The difficulty level of the objectives (beginner, intermediate, advanced)"
    )
    alignment_note: str = Field(
        "",
        description="Notes on how these objectives align with the topic and audience"
    )


class LearningObjectivesNode(BaseLessonAgent[LearningObjectivesOutput]):
    """Generates clear and measurable learning objectives for a lesson."""
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert instructional designer. Your task is to create 3-5 clear, specific, 
and measurable learning objectives for a lesson. 

Each objective should:
1. Start with an action verb (e.g., "Explain," "Demonstrate," "Analyze")
2. Be specific and concrete
3. Be achievable within the lesson timeframe
4. Be relevant to the topic and audience
5. Be measurable/assessable

Format each objective using Bloom's Taxonomy levels to ensure a good mix of cognitive complexity.
Include both lower-order (remember, understand) and higher-order (apply, analyze, evaluate, create) thinking skills.

For each objective, also provide the key concept it addresses."""
    
    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build a detailed prompt for generating learning objectives."""
        return (
            f"{self.system_prompt}\n\n"
            f"Topic: {input_data.get('topic', '')}\n"
            f"Target Audience: {input_data.get('target_audience', 'beginner')}\n"
            f"Lesson Scope: {input_data.get('scope', '')}\n"
            f"Prerequisites: {', '.join(input_data.get('prerequisites', [])) or 'None'}\n\n"
            "Please generate 3-5 learning objectives that align with the topic, audience, and scope above. "
            "Make sure they are specific, measurable, and appropriate for the target audience's level."
        )
    
    async def process(self, input_data: Dict[str, Any]) -> LearningObjectivesOutput:
        """Process the learning objectives generation request."""
        # Validate input
        input_model = LearningObjectivesInput(**input_data)
        
        # Call the parent's process method to handle the LLM interaction
        return await super().process({
            "topic": input_model.topic,
            "target_audience": input_model.target_audience,
            "scope": input_model.scope,
            "prerequisites": input_model.prerequisites
        })

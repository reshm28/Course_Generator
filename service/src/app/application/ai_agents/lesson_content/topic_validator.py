from typing import Dict, Any
from pydantic import BaseModel, Field
from .base_agent import BaseLessonAgent


class TopicValidatorInput(BaseModel):
    """Input model for TopicValidatorNode."""
    topic: str = Field(..., description="The topic to validate and refine")
    target_audience: str = Field("beginner", description="Target audience level (beginner, intermediate, advanced)")
    context: str = Field("", description="Additional context about the topic or requirements")


class TopicValidatorOutput(BaseModel):
    """Output model for TopicValidatorNode."""
    original_topic: str = Field(..., description="The original topic provided")
    refined_topic: str = Field(..., description="The refined and validated topic")
    is_valid: bool = Field(..., description="Whether the topic is valid for lesson generation")
    validation_message: str = Field("", description="Feedback about the validation")
    suggested_scope: str = Field(..., description="Suggested scope for the lesson")
    prerequisites: list[str] = Field(default_factory=list, description="List of recommended prerequisites")


class TopicValidatorNode(BaseLessonAgent[TopicValidatorOutput]):
    """Validates and refines the input topic for lesson generation."""
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert educational content validator. Your task is to analyze and refine lesson topics to ensure they are:
        
1. Clear and specific
2. Appropriately scoped for a single lesson
3. Aligned with the target audience's level
4. Educationally valuable

For each topic, provide:
- A refined version that's more focused and lesson-appropriate
- A validation result (valid/invalid with reason)
- Suggested scope for the lesson
- Any recommended prerequisites

If the topic is too broad, suggest a more focused version. If it's too narrow, suggest a slightly broader scope that would make a complete lesson."""
    
    async def process(self, input_data: Dict[str, Any]) -> TopicValidatorOutput:
        """Process the topic validation request."""
        # Validate input
        input_model = TopicValidatorInput(**input_data)
        
        # Call the parent's process method to handle the LLM interaction
        return await super().process({
            "topic": input_model.topic,
            "target_audience": input_model.target_audience,
            "context": input_model.context
        })

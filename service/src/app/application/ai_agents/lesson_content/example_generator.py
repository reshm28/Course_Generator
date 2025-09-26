from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from .base_agent import BaseLessonAgent
from app.domain.entities.lesson import Example


class ExampleGeneratorInput(BaseModel):
    """Input model for ExampleGeneratorNode."""
    topic: str = Field(..., description="The lesson topic")
    target_audience: str = Field("beginner", description="Target audience level")
    learning_objectives: List[Dict[str, str]] = Field(
        ...,
        description="List of learning objectives (with 'description' and 'key_concept' fields)"
    )
    content_sections: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lesson content sections to inform example generation"
    )
    example_types: List[str] = Field(
        default_factory=list,
        description="Types of examples to generate (e.g., 'real-world', 'analogy', 'case-study')"
    )
    num_examples: int = Field(
        2,
        ge=1,
        le=5,
        description="Number of examples to generate"
    )


class ExampleGeneratorOutput(BaseModel):
    """Output model for ExampleGeneratorNode."""
    examples: List[Example] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Generated examples and case studies"
    )
    additional_resources: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Suggested additional resources for further learning"
    )


class ExampleGeneratorNode(BaseLessonAgent[ExampleGeneratorOutput]):
    """Generates relevant examples and case studies for a lesson."""
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert at creating educational examples and case studies. Your task is to generate 
engaging, relevant examples that help illustrate the lesson's key concepts.

For each example, provide:
1. A clear, descriptive title
2. A detailed explanation of the example
3. The key takeaway or lesson learned
4. How it relates to the learning objectives

Examples should be:
- Relevant to the target audience
- Clear and easy to understand
- Real-world applicable when possible
- Varied in approach (e.g., different types of examples)
- Tied directly to the learning objectives"""

    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build a detailed prompt for generating examples."""
        objectives = "\n".join(
            f"- {obj.get('description', '')} (Key Concept: {obj.get('key_concept', 'N/A')})" 
            for obj in input_data.get("learning_objectives", [])
        )
        
        sections = "\n".join(
            f"- {section.get('heading', 'Untitled Section')}: {section.get('content', '')[:100]}..."
            for section in input_data.get("content_sections", [])[:3]  # Just show first few sections
        )
        
        example_types = ", ".join(input_data.get("example_types", ["real-world", "analogy"]))
        
        return (
            f"{self.system_prompt}\n\n"
            f"Topic: {input_data.get('topic', '')}\n"
            f"Target Audience: {input_data.get('target_audience', 'beginner')}\n\n"
            f"Learning Objectives:\n{objectives}\n\n"
            f"Lesson Content Overview:\n{sections}\n\n"
            f"Please generate {input_data.get('num_examples', 2)} high-quality examples that would help students "
            f"understand these concepts. Focus on {example_types} examples that would resonate with the target audience. "
            "For each example, explain how it connects to the learning objectives and what key insight it provides."
        )
    
    @field_validator('learning_objectives', mode='before')
    @classmethod
    def validate_learning_objectives(cls, v):
        """Ensure learning objectives have the required structure."""
        if not isinstance(v, list):
            raise ValueError("learning_objectives must be a list")
        return [
            {
                'description': obj.get('description', ''),
                'key_concept': obj.get('key_concept', '')
            }
            for obj in v
        ]
    
    async def process(self, input_data: Dict[str, Any]) -> ExampleGeneratorOutput:
        """Process the example generation request."""
        # Validate and prepare input
        input_model = ExampleGeneratorInput(**input_data)
        
        # Prepare the input for the LLM
        llm_input = {
            "topic": input_model.topic,
            "target_audience": input_model.target_audience,
            "learning_objectives": input_model.learning_objectives,
            "content_sections": input_model.content_sections,
            "example_types": input_model.example_types,
            "num_examples": input_model.num_examples
        }
        
        # Call the parent's process method to handle the LLM interaction
        return await super().process(llm_input)

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, field_validator
from .base_agent import BaseLessonAgent
from app.domain.entities.lesson import QuizQuestion, LearningObjective


class QuizCreatorInput(BaseModel):
    """Input model for QuizCreatorNode."""
    topic: str = Field(..., description="The lesson topic")
    target_audience: str = Field("beginner", description="Target audience level")
    learning_objectives: List[Dict[str, str]] = Field(
        ...,
        description="List of learning objectives with their key concepts"
    )
    content_sections: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lesson content sections to inform question generation"
    )
    num_questions: int = Field(
        3,
        ge=1,
        le=10,
        description="Number of quiz questions to generate"
    )
    question_types: List[str] = Field(
        default_factory=lambda: ["multiple_choice"],
        description="Types of questions to generate (multiple_choice, true_false, short_answer)"
    )
    difficulty: str = Field(
        "medium",
        description="Difficulty level of the questions (easy, medium, hard)"
    )


class QuizCreatorOutput(BaseModel):
    """Output model for QuizCreatorNode."""
    questions: List[QuizQuestion] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Generated quiz questions"
    )
    answer_key: Dict[int, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Answer key with explanations for each question"
    )
    assessment_criteria: Dict[str, str] = Field(
        default_factory=dict,
        description="Criteria for assessing student responses"
    )


class QuizCreatorNode(BaseLessonAgent[QuizCreatorOutput]):
    """Generates quiz questions to assess understanding of the lesson content."""
    
    @property
    def system_prompt(self) -> str:
        return """You are an expert educational content creator specializing in assessment design. 
Your task is to create high-quality quiz questions that effectively test the learning objectives.

For each question, provide:
1. A clear, unambiguous question
2. 3-5 plausible answer options (for multiple choice)
3. The correct answer (with index)
4. A brief explanation of why the correct answer is right
5. The specific learning objective(s) being assessed

Questions should:
- Be aligned with the learning objectives
- Test different levels of understanding (remember, understand, apply, analyze)
- Be appropriate for the target audience's level
- Be free from ambiguity or trick questions
- Include plausible distractors (for multiple choice)"""

    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build a detailed prompt for generating quiz questions."""
        objectives = "\n".join(
            f"- {obj.get('description', '')} (Key Concept: {obj.get('key_concept', 'N/A')})" 
            for obj in input_data.get("learning_objectives", [])
        )
        
        sections = "\n".join(
            f"- {section.get('heading', 'Untitled Section')}: {section.get('content', '')[:100]}..."
            for section in input_data.get("content_sections", [])[:3]  # Just show first few sections
        )
        
        question_types = ", ".join(input_data.get("question_types", ["multiple_choice"]))
        
        return (
            f"{self.system_prompt}\n\n"
            f"Topic: {input_data.get('topic', '')}\n"
            f"Target Audience: {input_data.get('target_audience', 'beginner')}\n"
            f"Difficulty Level: {input_data.get('difficulty', 'medium')}\n\n"
            f"Learning Objectives to Assess:\n{objectives}\n\n"
            f"Lesson Content Overview:\n{sections}\n\n"
            f"Please generate {input_data.get('num_questions', 3)} high-quality {question_types} questions "
            f"that effectively assess the learning objectives. Ensure the questions are appropriate for "
            f"{input_data.get('target_audience', 'beginner')} level students and cover the key concepts "
            "from the lesson. Include a mix of question types if possible."
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
    
    async def process(self, input_data: Dict[str, Any]) -> QuizCreatorOutput:
        """Process the quiz generation request."""
        # Validate and prepare input
        input_model = QuizCreatorInput(**input_data)
        
        # Prepare the input for the LLM
        llm_input = {
            "topic": input_model.topic,
            "target_audience": input_model.target_audience,
            "learning_objectives": input_model.learning_objectives,
            "content_sections": input_model.content_sections,
            "num_questions": input_model.num_questions,
            "question_types": input_model.question_types,
            "difficulty": input_model.difficulty
        }
        
        # Call the parent's process method to handle the LLM interaction
        result = await super().process(llm_input)
        
        # Process the result to ensure it matches our QuizQuestion model
        processed_questions = []
        answer_key = {}
        
        for i, q in enumerate(result.questions):
            # Ensure we have the required fields
            if not all(hasattr(q, field) for field in ['question', 'options', 'correct_answer', 'explanation']):
                continue
                
            # Add to processed questions
            processed_questions.append(q)
            
            # Add to answer key
            answer_key[i] = {
                "correct_answer": q.correct_answer,
                "explanation": q.explanation,
                "learning_objectives": getattr(q, 'learning_objectives', [])
            }
        
        return QuizCreatorOutput(
            questions=processed_questions,
            answer_key=answer_key,
            assessment_criteria=result.assessment_criteria
        )

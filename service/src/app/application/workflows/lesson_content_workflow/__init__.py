"""
Lesson Content Generation Workflow

This module implements a LangGraph workflow for generating complete, structured lessons
using multiple AI agents in a coordinated pipeline.
"""
from typing import Dict, Any, Optional, TypedDict
from dataclasses import dataclass, field
from enum import Enum

from langgraph.graph import StateGraph, END

from app.infrastructure.llm.llm_client import BaseLLMClient
from app.domain.entities.lesson import (
    LessonContent,
    LearningObjective,
    Example,
    QuizQuestion,
    DifficultyLevel
)


class WorkflowState(TypedDict):
    """State for the lesson content generation workflow."""
    # Inputs
    topic: str
    target_audience: str
    context: Optional[str]
    
    # Intermediate states
    validated_topic: Optional[Dict[str, Any]]
    learning_objectives: Optional[Dict[str, Any]]
    content_sections: Optional[Dict[str, Any]]
    examples: Optional[Dict[str, Any]]
    quiz_questions: Optional[Dict[str, Any]]
    
    # Output
    lesson: Optional[LessonContent]
    
    # Metadata
    metadata: Dict[str, Any]
    errors: list[str]


class LessonContentWorkflow:
    """Orchestrates the lesson content generation workflow using LangGraph."""
    
    def __init__(self, llm_client: BaseLLMClient, model: str = "gpt-4"):
        """Initialize the workflow with an LLM client."""
        self.llm_client = llm_client
        self.model = model
        self._graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build and return the LangGraph state machine."""
        from app.application.ai_agents.lesson_content import (
            TopicValidatorNode,
            LearningObjectivesNode,
            LessonBodyNode,
            ExampleGeneratorNode,
            QuizCreatorNode,
            LessonAssemblerNode
        )
        
        # Initialize agents
        topic_validator = TopicValidatorNode(
            llm_client=self.llm_client,
            model=self.model
        )
        
        learning_objectives = LearningObjectivesNode(
            llm_client=self.llm_client,
            model=self.model
        )
        
        lesson_body = LessonBodyNode(
            llm_client=self.llm_client,
            model=self.model
        )
        
        example_generator = ExampleGeneratorNode(
            llm_client=self.llm_client,
            model=self.model
        )
        
        quiz_creator = QuizCreatorNode(
            llm_client=self.llm_client,
            model=self.model
        )
        
        lesson_assembler = LessonAssemblerNode(
            llm_client=self.llm_client,
            model=self.model
        )
        
        # Define the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("validate_topic", topic_validator.process)
        workflow.add_node("generate_objectives", learning_objectives.process)
        workflow.add_node("generate_content", lesson_body.process)
        workflow.add_node("generate_examples", example_generator.process)
        workflow.add_node("create_quiz", quiz_creator.process)
        workflow.add_node("assemble_lesson", lesson_assembler.process)
        
        # Define the edges
        workflow.add_edge("validate_topic", "generate_objectives")
        workflow.add_edge("generate_objectives", "generate_content")
        workflow.add_edge("generate_content", "generate_examples")
        workflow.add_edge("generate_examples", "create_quiz")
        workflow.add_edge("create_quiz", "assemble_lesson")
        workflow.add_edge("assemble_lesson", END)
        
        # Set the entry point
        workflow.set_entry_point("validate_topic")
        
        return workflow.compile()
    
    async def generate_lesson(
        self, 
        topic: str, 
        target_audience: str = "beginner",
        context: Optional[str] = None
    ) -> LessonContent:
        """Generate a complete lesson on the given topic.
        
        Args:
            topic: The main topic of the lesson
            target_audience: The target audience level (beginner, intermediate, advanced)
            context: Additional context about the lesson requirements
            
        Returns:
            A complete LessonContent object with all generated content
        """
        # Initialize the state
        initial_state: WorkflowState = {
            "topic": topic,
            "target_audience": target_audience,
            "context": context,
            "validated_topic": None,
            "learning_objectives": None,
            "content_sections": None,
            "examples": None,
            "quiz_questions": None,
            "lesson": None,
            "metadata": {
                "workflow_version": "1.0.0",
                "model": self.model,
            },
            "errors": []
        }
        
        # Run the workflow
        try:
            result = await self._graph.ainvoke(initial_state)
            if not result.get("lesson"):
                raise ValueError("Failed to generate lesson content")
            return result["lesson"]
        except Exception as e:
            # Log the error and re-raise
            print(f"Error in lesson generation workflow: {str(e)}")
            raise RuntimeError(f"Failed to generate lesson: {str(e)}")

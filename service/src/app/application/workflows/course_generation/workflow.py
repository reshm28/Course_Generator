from typing import Dict, List, Optional, TypedDict, cast

from langgraph.graph import StateGraph, END

from app.infrastructure.llm.llm_client import BaseLLMClient
from .state import CourseState, PlannerInput, CoursePlan, ModulePlan, LessonContent, ReviewFeedback
from .agents import PlannerAgent, ContentGeneratorAgent, ReviewerAgent


class CourseGenerationWorkflow:
    """Orchestrates the course generation workflow using LangGraph."""
    
    def __init__(self, llm_client: BaseLLMClient, model: str = "gpt-4"):
        """Initialize the workflow with an LLM client."""
        self.llm_client = llm_client
        self.model = model
        self._graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build and return the LangGraph state machine."""
        # Initialize agents
        planner = PlannerAgent(self.llm_client, self.model)
        content_generator = ContentGeneratorAgent(self.llm_client, self.model)
        reviewer = ReviewerAgent(self.llm_client, self.model)
        
        # Define the state graph
        workflow = StateGraph(CourseState)
        
        # Add nodes for each agent
        workflow.add_node("plan_course", planner.process)
        workflow.add_node("generate_content", content_generator.process)
        workflow.add_node("review_content", reviewer.process)
        
        # Define the edges
        workflow.add_edge("plan_course", "generate_content")
        
        # Conditional edge for review
        def should_review(state: CourseState) -> str:
            # If we have a current lesson, review it
            if state.get("current_lesson"):
                return "review_content"
            return "generate_content"
        
        workflow.add_conditional_edges(
            "generate_content",
            should_review,
            {
                "review_content": "review_content",
                "generate_content": "generate_content",
            },
        )
        
        # After review, decide whether to continue or finish
        def should_continue(state: CourseState) -> str:
            if state.get("is_complete", False):
                return "end"
            return "generate_content"
        
        workflow.add_conditional_edges(
            "review_content",
            should_continue,
            {
                "generate_content": "generate_content",
                "end": END,
            },
        )
        
        # Set the entry point
        workflow.set_entry_point("plan_course")
        
        return workflow.compile()
    
    async def generate_course(self, topic: str) -> CourseState:
        """Generate a course on the given topic."""
        # Initialize the state
        initial_state: CourseState = {
            "topic": topic,
            "course_structure": None,
            "current_module": None,
            "current_lesson": None,
            "validation_errors": [],
            "is_complete": False,
        }
        
        # Run the workflow
        final_state = await self._graph.ainvoke(initial_state)
        
        return final_state

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar, Generic
from pydantic import BaseModel
from app.infrastructure.llm.llm_client import BaseLLMClient

T = TypeVar('T', bound=BaseModel)

class BaseLessonAgent(ABC, Generic[T]):
    """Base class for all lesson content generation agents."""
    
    def __init__(
        self, 
        llm_client: BaseLLMClient,
        model: str = "gpt-4",
        temperature: float = 0.7
    ):
        """Initialize the agent with LLM client and configuration.
        
        Args:
            llm_client: The LLM client to use for generation
            model: The model to use (default: "gpt-4")
            temperature: The temperature for generation (default: 0.7)
        """
        self.llm = llm_client
        self.model = model
        self.temperature = temperature
    
    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        pass
    
    @property
    def output_model(self) -> Type[T]:
        """Return the Pydantic model for the output of this agent."""
        return self.__orig_bases__[0].__args__[0]  # type: ignore
    
    async def process(self, input_data: Dict[str, Any]) -> T:
        """Process the input data and return structured output.
        
        Args:
            input_data: Dictionary containing input data for the agent
            
        Returns:
            Structured output as an instance of the output model
        """
        prompt = self._build_prompt(input_data)
        
        result = await self.llm.generate_structured(
            output_model=self.output_model,
            prompt=prompt,
            model=self.model,
            temperature=self.temperature,
            **input_data
        )
        
        return result
    
    def _build_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build the prompt for the LLM.
        
        Args:
            input_data: Dictionary containing input data
            
        Returns:
            Formatted prompt string
        """
        return (
            f"{self.system_prompt}\n\n"
            f"Input data: {input_data}\n"
            "Please provide your response in the specified JSON format."
        )

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service status")


class EchoQuery(BaseModel):
    text: str = Field(..., description="Text to echo via LangGraph")


class EchoResponse(BaseModel):
    result: str

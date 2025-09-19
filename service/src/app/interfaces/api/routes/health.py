from fastapi import APIRouter, Depends

from app.interfaces.api.schemas import (
    HealthResponse, 
    EchoQuery, 
    EchoResponse
)
from app.application.workflows.ai_graph import get_ai_graph_runner

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/ai/echo", response_model=EchoResponse)
def ai_echo(query: EchoQuery = Depends()) -> EchoResponse:
    runner = get_ai_graph_runner()
    result = runner.run_text(query.text)
    return EchoResponse(result=result)

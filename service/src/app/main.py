from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.settings import settings
from app.interfaces.api.routes.health import router as health_router
from app.interfaces.api.routes.courses import router as courses_router
from app.interfaces.api.middleware import error_handling_middleware
from app.logging_config import configure_logging


configure_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (adjust as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
app.middleware("http")(error_handling_middleware)

# API routes
app.include_router(health_router)
app.include_router(courses_router)


def run() -> None:
    """Entrypoint for `uv run app`. Useful for alternative runners."""
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(settings.PORT),
        reload=False,
    )


if __name__ == "__main__":
    run()

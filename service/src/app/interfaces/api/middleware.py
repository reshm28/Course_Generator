import logging
from typing import Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


async def error_handling_middleware(request: Request, call_next: Callable[[Request], Response]) -> Response:
    try:
        response = await call_next(request)
        return response
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Unhandled error: %s", exc)
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

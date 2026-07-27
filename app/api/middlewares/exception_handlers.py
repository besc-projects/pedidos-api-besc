import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import AppException

logger = logging.getLogger("app.errors")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Translate domain/application exceptions into standardized HTTP responses."""
    if exc.status_code >= 500:
        logger.error("Unhandled app error at %s: %s", request.url.path, exc.message)
    return JSONResponse(status_code=exc.status_code, content={"message": exc.message})


def register_exception_handlers(app: FastAPI) -> None:
    """Wire the application exception handlers into the FastAPI app."""
    app.add_exception_handler(AppException, app_exception_handler)

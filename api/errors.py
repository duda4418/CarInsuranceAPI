"""Centralized exception handlers for FastAPI app."""

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from services.exceptions import NotFoundError
from services.exceptions import ValidationError as DomainValidationError


# Centralized exception handler registration.
def register_exception_handlers(app):
    """Register all custom exception handlers to the FastAPI app."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(exc: NotFoundError):
        """Handle NotFoundError exceptions."""
        return JSONResponse(
            status_code=404, content={"error": "not_found", "detail": str(exc)}
        )

    @app.exception_handler(DomainValidationError)
    async def domain_validation_handler(exc: DomainValidationError):
        """Handle domain validation errors."""
        return JSONResponse(
            status_code=400, content={"error": "validation_error", "detail": str(exc)}
        )

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(exc: StarletteHTTPException):
        """Handle Starlette HTTP exceptions (including 404)."""
        if exc.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={"error": "not_found", "detail": "Route not found"},
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": "http_error", "detail": exc.detail},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(exc: RequestValidationError):
        """Handle Pydantic request validation errors."""
        # Flatten Pydantic error structure into a concise list
        errors = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err.get("loc", []) if p not in ("body",))
            errors.append({"field": loc, "message": err.get("msg")})
        return JSONResponse(
            status_code=422,
            content={"error": "request_validation_error", "detail": errors},
        )

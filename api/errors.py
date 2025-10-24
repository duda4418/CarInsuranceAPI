from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from services.exceptions import NotFoundError, ValidationError as DomainValidationError

# Centralized exception handler registration.
def register_exception_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"error": "not_found", "detail": str(exc)})

    @app.exception_handler(DomainValidationError)
    async def domain_validation_handler(request: Request, exc: DomainValidationError):
        return JSONResponse(status_code=400, content={"error": "validation_error", "detail": str(exc)})

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Unmatched route 404 or other Starlette-level HTTP errors
        if exc.status_code == 404:
            return JSONResponse(status_code=404, content={"error": "not_found", "detail": "Route not found"})
        return JSONResponse(status_code=exc.status_code, content={"error": "http_error", "detail": exc.detail})

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError):
        # Flatten Pydantic error structure into a concise list
        errors = []
        for err in exc.errors():
            loc = ".".join(str(p) for p in err.get("loc", []) if p not in ("body",))
            errors.append({"field": loc, "message": err.get("msg")})
        return JSONResponse(status_code=422, content={"error": "request_validation_error", "detail": errors})

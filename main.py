import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response

from api.errors import register_exception_handlers
from api.routers.cars import cars_router
from api.routers.claims import claims_router
from api.routers.health import health_router
from api.routers.policies import policies_router
from core.logging import configure_logging, get_logger
from core.settings import settings
from services.scheduler import start_scheduler, stop_scheduler

warnings.filterwarnings(
    "ignore", category=UserWarning, module="pydantic._internal._generate_schema"
)


log = get_logger()


REQUEST_ID_HEADER = "X-Request-ID"


def _build_lifespan(enable_scheduler: bool, configure_logs: bool):
    """Return a lifespan context manager configured for the requested flags."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):  # type: ignore[unused-ignore]
        # Startup
        if configure_logs:
            configure_logging()
            log.info(
                "app_startup",
                env=settings.APP_ENV,
                logLevel=(
                    settings.LOG_LEVEL
                    or ("DEBUG" if settings.APP_ENV in ("local", "dev") else "INFO")
                ).upper(),
            )
        if enable_scheduler:
            start_scheduler()
        yield
        # Shutdown
        if enable_scheduler:
            stop_scheduler()

    return lifespan


def create_app(
    *, enable_scheduler: bool = True, configure_logs: bool = True
) -> FastAPI:
    """Application factory.

    Parameters
    ----------
    enable_scheduler: bool
        Start background scheduler on startup. Disable in tests to avoid extra threads.
    configure_logs: bool
        Run logging configuration on startup. Disable in tests if you want default/quiet logging.

    In production just import `app` or run with uvicorn: `uvicorn main:app`.
    """
    lifespan = _build_lifespan(
        enable_scheduler=enable_scheduler, configure_logs=configure_logs
    )
    app = FastAPI(title="Car Insurance API", version="0.1.0", lifespan=lifespan)

    # Middleware: bind request_id and request metadata
    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):  # type: ignore[unused-ignore]
        import uuid

        import structlog

        # Extract/generate request id
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        structlog.contextvars.bind_contextvars(
            request_id=request_id, path=request.url.path, method=request.method
        )
        try:
            response: Response = await call_next(request)
        except Exception:
            # Ensure stack trace is logged with context (global exception handler may also run)
            log.exception("unhandled_exception")
            raise
        finally:
            # Clear to avoid leaking a cross tasks
            structlog.contextvars.clear_contextvars()
        # Propagate request id header
        response.headers.setdefault(REQUEST_ID_HEADER, request_id)
        return response

    # Routers
    app.include_router(health_router, prefix="/api")
    app.include_router(cars_router, prefix="/api")
    app.include_router(policies_router, prefix="/api")
    app.include_router(claims_router, prefix="/api")

    register_exception_handlers(app)
    return app


app = create_app(enable_scheduler=True, configure_logs=True)

__all__ = ["create_app", "app"]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

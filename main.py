from fastapi import FastAPI
from contextlib import asynccontextmanager
import warnings

from core.logging import configure_logging
from services.scheduler import start_scheduler, stop_scheduler
from api.routers.errors import register_exception_handlers

from api.routers.cars import cars_router
from api.routers.claims import claims_router
from api.routers.health import health_router
from api.routers.history import history_router
from api.routers.policies import policies_router

# Fallback broad suppression by module name where the warning originates (internal schema generation).
warnings.filterwarnings(
    "ignore",
    category=UserWarning,
    module="pydantic._internal._generate_schema"
)


def _build_lifespan(enable_scheduler: bool, configure_logs: bool):
    """Return a lifespan context manager configured for the requested flags.
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):  # type: ignore[unused-ignore]
        # Startup
        if configure_logs:
            configure_logging()
        if enable_scheduler:
            start_scheduler()
        yield
        # Shutdown
        if enable_scheduler:
            stop_scheduler()
    return lifespan


def create_app(*, enable_scheduler: bool = True, configure_logs: bool = True) -> FastAPI:
    """Application factory.

    Parameters
    ----------
    enable_scheduler: bool
        Start background scheduler on startup. Disable in tests to avoid extra threads.
    configure_logs: bool
        Run logging configuration on startup. Disable in tests if you want default/quiet logging.

    In production just import `app` or run with uvicorn: `uvicorn main:app`.
    """
    lifespan = _build_lifespan(enable_scheduler=enable_scheduler, configure_logs=configure_logs)
    app = FastAPI(title="Car Insurance API", version="0.1.0", lifespan=lifespan)

    # Routers
    app.include_router(health_router, prefix="/api")
    app.include_router(cars_router, prefix="/api")
    app.include_router(policies_router, prefix="/api")
    app.include_router(claims_router, prefix="/api")
    app.include_router(history_router, prefix="/api")

    register_exception_handlers(app)
    return app


# Module-level app instance (production / default usage).
# Always enable scheduler & logging here; tests should call create_app(...) explicitly.
app = create_app(enable_scheduler=True, configure_logs=True)

__all__ = ["create_app", "app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
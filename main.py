from fastapi import FastAPI
from contextlib import asynccontextmanager

from core.logging import configure_logging
from services.scheduler import start_scheduler, stop_scheduler
from api.routers.errors import register_exception_handlers

from api.routers.cars import cars_router
from api.routers.claims import claims_router
from api.routers.health import health_router
from api.routers.history import history_router
from api.routers.policies import policies_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    configure_logging()
    start_scheduler()
    yield
    # Shutdown
    stop_scheduler()

app = FastAPI(title="Car Insurance API", version="0.1.0", lifespan=lifespan)

# Routers
app.include_router(health_router, prefix="/api")
app.include_router(cars_router, prefix="/api")
app.include_router(policies_router, prefix="/api")
app.include_router(claims_router, prefix="/api")
app.include_router(history_router, prefix="/api")

register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
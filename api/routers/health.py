from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
async def health():
    """Simple health check endpoint.

    CRUD is not meaningful here because this is a synthetic operational endpoint
    whose sole purpose is to report service status. We intentionally provide only
    a GET.
    """
    return {"status": "ok"}

from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/api/health")
async def health():
    return {"status": "ok"}
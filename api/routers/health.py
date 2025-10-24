from fastapi import APIRouter, status
from api.schemas import HealthRead


health_router = APIRouter()


@health_router.get(
    "/health",
    response_model=HealthRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Service healthy"}
    }
)
async def health():
    return HealthRead(status="ok")

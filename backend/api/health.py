from fastapi import APIRouter
from backend.schemas.responses import APIResponse, success_response
from backend.core.settings import settings

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=APIResponse[dict])
def health_check():
    """
    Simple health check endpoint to verify the service is running.
    """
    return success_response(
        message="Service is healthy",
        data={
            "status": "healthy",
            "version": settings.VERSION
        }
    )

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    """Standardized API Response format."""
    status: str
    message: str
    data: Optional[T] = None


def success_response(message: str, data: Any = None) -> dict:
    """Helper for successful responses."""
    return {"status": "success", "message": message, "data": data}


def error_response(message: str, data: Any = None) -> dict:
    """Helper for error responses."""
    return {"status": "error", "message": message, "data": data}

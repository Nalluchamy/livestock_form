from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from backend.core.logging import logger
from backend.schemas.responses import error_response


class APIException(Exception):
    def __init__(self, message: str, status_code: int = 400, data: dict = None):
        self.message = message
        self.status_code = status_code
        self.data = data


async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(message=exc.message, data=exc.data)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Format the Pydantic errors into a cleaner structure if desired
    formatted_errors = [{"loc": e["loc"], "msg": e["msg"], "type": e["type"]} for e in errors]
    return JSONResponse(
        status_code=422,
        content=error_response(message="Validation Error", data=formatted_errors)
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content=error_response(message="Internal Server Error: Database operation failed.")
    )


async def general_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=error_response(message="Internal Server Error: An unexpected error occurred.")
    )

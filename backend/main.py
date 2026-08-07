from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from backend.core.settings import settings
from backend.core.logging import logger
from backend.api import health
from backend.api.v1 import grading, disagreements, metrics, sync
from backend.middleware.request_id import RequestIDMiddleware
from backend.middleware.logging import LoggingMiddleware
from backend.services.exceptions import (
    APIException,
    api_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler
)

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    from backend.database.base import Base
    from backend.database.connection import engine
    import backend.models  # ensure models are registered
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="Explainable Livestock Health Grading System API",
    )

    # Middlewares
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Placeholder for CORS
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(grading.router, prefix="/api/v1")
    app.include_router(grading.history_router, prefix="/api/v1")
    app.include_router(disagreements.router, prefix="/api/v1")
    app.include_router(metrics.router, prefix="/api/v1")
    app.include_router(sync.router, prefix="/api/v1")

    logger.info("FastAPI application created with Phase 4 extensions.")
    return app

app = create_app()

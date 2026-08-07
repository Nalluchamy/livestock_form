from typing import Generator
from sqlalchemy.orm import Session

from backend.database.connection import SessionLocal
from backend.core.logging import logger


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session.
    Ensures the session is closed after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

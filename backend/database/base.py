from typing import Any
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy 2.x models.
    Provides a shared MetaData object and common patterns if needed.
    """
    pass

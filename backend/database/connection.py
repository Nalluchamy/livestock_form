from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.settings import settings
from backend.core.logging import logger


# SQLAlchemy Engine
db_url = settings.database_url
connect_args = {}
engine_kwargs = {}

if "sqlite" in db_url:
    connect_args["check_same_thread"] = False
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20

try:
    engine = create_engine(
        db_url,
        connect_args=connect_args,
        **engine_kwargs
    )
    logger.info("Database engine initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize database engine: {e}")
    raise


# Session factory
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class DimImage(Base):
    """
    Dimension table representing metadata about images captured during grading.
    """
    __tablename__ = "dim_image"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Logical path to the image stored in an object store or processed dataset folder
    file_path: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)
    
    # To satisfy ethical requirements, explicitly track that EXIF was stripped
    exif_stripped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    resolution: Mapped[str] = mapped_column(String(50), nullable=True)

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    grading_events: Mapped[list["FactGradingEvent"]] = relationship(
        "FactGradingEvent", back_populates="image"
    )

    def __repr__(self) -> str:
        return f"<DimImage(id={self.id}, exif_stripped={self.exif_stripped})>"

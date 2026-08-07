import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class DimSample(Base):
    """
    Dimension table representing the livestock sample being graded.
    """
    __tablename__ = "dim_sample"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # The farm or location where the sample was taken
    farm_location: Mapped[str] = mapped_column(String(255), index=True)
    # Species or type of livestock (e.g., Cattle, Swine, Poultry)
    species: Mapped[str] = mapped_column(String(100), index=True)
    
    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    grading_events: Mapped[list["FactGradingEvent"]] = relationship(
        "FactGradingEvent", back_populates="sample", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<DimSample(id={self.id}, species={self.species})>"

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class DimCriterion(Base):
    """
    Dimension table storing the distinct measurable attributes and rules
    used during a specific grading event.
    """
    __tablename__ = "dim_criterion"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # E.g., 'muscle_score', 'fat_depth', 'coat_condition'
    attribute_name: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    # Store the exact rule or condition threshold applied
    rule_condition: Mapped[str] = mapped_column(String(255), nullable=True)
    
    # Flexible field to store measured values (could be numerical or categorical)
    measured_value: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Optional JSON metadata for complex attributes
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    grading_events: Mapped[list["FactGradingEvent"]] = relationship(
        "FactGradingEvent", back_populates="criterion"
    )

    def __repr__(self) -> str:
        return f"<DimCriterion(attribute_name={self.attribute_name}, value={self.measured_value})>"

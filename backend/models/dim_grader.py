import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class DimGrader(Base):
    """
    Dimension table representing a human grader or senior reviewer.
    """
    __tablename__ = "dim_grader"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    # Role: 'field_grader', 'senior_reviewer', 'farm_manager', 'buyer'
    role: Mapped[str] = mapped_column(String(50), index=True)
    
    # We do NOT store PII like real names for ethical/privacy reasons unless required
    # But an identifier is needed for tracking who graded what.
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    grading_events: Mapped[list["FactGradingEvent"]] = relationship(
        "FactGradingEvent", back_populates="grader"
    )

    def __repr__(self) -> str:
        return f"<DimGrader(username={self.username}, role={self.role})>"

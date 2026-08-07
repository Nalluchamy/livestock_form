import uuid
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class FactGradingEvent(Base):
    """
    Central fact table linking dimension tables.
    Stores the actual grading transactions, including human grades, AI predictions,
    explanations, and review statuses.
    """
    __tablename__ = "fact_grading_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Foreign Keys to Dimension Tables
    sample_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dim_sample.id", ondelete="CASCADE"), index=True, nullable=False
    )
    grader_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dim_grader.id", ondelete="SET NULL"), index=True, nullable=True
    )
    image_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dim_image.id", ondelete="SET NULL"), index=True, nullable=True
    )
    criterion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("dim_criterion.id", ondelete="SET NULL"), index=True, nullable=True
    )

    # Core Facts
    human_grade: Mapped[str] = mapped_column(String(50), nullable=True)
    ai_grade: Mapped[str] = mapped_column(String(50), nullable=True)
    
    # ML Explainability & Confidence
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Workflow status (e.g., 'accepted', 'disputed', 'reviewed')
    review_status: Mapped[str] = mapped_column(String(50), default="pending", index=True)
    
    # Offline sync support
    client_offline_id: Mapped[str] = mapped_column(String(255), nullable=True, index=True)
    is_synced: Mapped[bool] = mapped_column(default=True, index=True)

    # Audit timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    # Soft delete
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    sample: Mapped["DimSample"] = relationship("DimSample", back_populates="grading_events")
    grader: Mapped["DimGrader"] = relationship("DimGrader", back_populates="grading_events")
    image: Mapped["DimImage"] = relationship("DimImage", back_populates="grading_events")
    criterion: Mapped["DimCriterion"] = relationship("DimCriterion", back_populates="grading_events")

    def __repr__(self) -> str:
        return f"<FactGradingEvent(id={self.id}, status={self.review_status})>"

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


VALID_REVIEW_STATUSES = {
    "PENDING", "OPEN", 
    "IN_REVIEW", "UNDER_REVIEW", 
    "RESOLVED", "ESCALATED", "CANCELLED"
}

ALLOWED_STATUS_TRANSITIONS = {
    "PENDING": {"IN_REVIEW", "UNDER_REVIEW", "RESOLVED", "CANCELLED"},
    "OPEN": {"IN_REVIEW", "UNDER_REVIEW", "RESOLVED", "CANCELLED"},
    "IN_REVIEW": {"RESOLVED", "ESCALATED", "CANCELLED"},
    "UNDER_REVIEW": {"RESOLVED", "ESCALATED", "CANCELLED"},
    "ESCALATED": {"IN_REVIEW", "UNDER_REVIEW", "RESOLVED", "CANCELLED"},
    "RESOLVED": set(),  # Terminal status
    "CANCELLED": set(),  # Terminal status
}


class DisagreementReview(Base):
    """
    Persistent table for human-system and inter-rater disagreement reviews.
    Maintains an immutable audit trail of original grades while tracking
    authoritative senior reviewer resolutions.
    """
    __tablename__ = "disagreement_reviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    
    # Associated Grading Event in Fact Table
    grading_event_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fact_grading_events.id", ondelete="SET NULL"),
        index=True,
        nullable=True
    )

    # Immutable Original Grades (set once upon creation)
    original_human_grade: Mapped[str] = mapped_column(String(50), nullable=False)
    original_system_grade: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Optional Third-Party/Senior Expert Grade
    expert_grade: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Review Lifecycle Status
    status: Mapped[str] = mapped_column(
        String(50), default="PENDING", index=True, nullable=False
    )

    # Reviewer Information & Authoritative Resolution
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reviewer_action: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewer_final_decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    reviewer_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    grading_event = relationship("FactGradingEvent", backref="disagreement_reviews")

    def __repr__(self) -> str:
        return f"<DisagreementReview(id={self.id}, status={self.status}, orig_human={self.original_human_grade}, orig_sys={self.original_system_grade})>"

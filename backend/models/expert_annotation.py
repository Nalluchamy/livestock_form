import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Float, Boolean, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


VALID_ANNOTATION_STATUSES = {
    "PENDING",               # Awaiting first grader
    "PARTIALLY_ANNOTATED",  # Graded by Grader 1, awaiting Grader 2
    "CONSENSUS_REACHED",    # Graders agree or senior consensus approved
    "DISAGREEMENT",         # Grader 1 and Grader 2 submitted conflicting grades
    "REJECTED"              # Flagged as ungradable/poor quality/PII violation
}


class ExpertAnnotation(Base):
    """
    Persistent table for expert double-blind livestock health annotations.
    Stores structured clinical attributes, isolated grades from Graders 1 & 2,
    quality rejection flags, and authoritative consensus decisions.
    """
    __tablename__ = "expert_annotations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    sample_id: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    image_path: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    species: Mapped[str] = mapped_column(
        String(32), default="cattle", nullable=False
    )

    # Physical Attributes (Photo-Visible & Exam Records)
    body_condition: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    coat_quality: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    eye_condition: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    wound_presence: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    mobility: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    appetite: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    weight_if_available: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Grader 1 (Blind)
    expert_grader_1_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    expert_grade_1: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    expert_grade_1_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expert_grade_1_submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Grader 2 (Blind)
    expert_grader_2_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    expert_grade_2: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    expert_grade_2_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expert_grade_2_submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Authoritative Consensus / Resolution
    final_consensus_grade: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    consensus_reviewer_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    consensus_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    consensus_reached_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Status & Quality Triage
    annotation_status: Mapped[str] = mapped_column(
        String(50), default="PENDING", index=True, nullable=False
    )
    quality_flagged: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, nullable=False
    )
    quality_issue_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    flagged_by_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    flagged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

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

    def to_dict(self, viewer_grader_id: Optional[str] = None, is_senior_reviewer: bool = False) -> dict:
        """
        Serializes model. Enforces double-blind isolation:
        If viewer is Grader 1, hides Grader 2's grade/notes if pending.
        If viewer is Grader 2, hides Grader 1's grade/notes until Grader 2 has submitted.
        Senior reviewers and finalized consensus records reveal both grades.
        """
        hide_g1 = False
        hide_g2 = False

        if not is_senior_reviewer and self.annotation_status not in {"CONSENSUS_REACHED", "DISAGREEMENT"}:
            if viewer_grader_id:
                if viewer_grader_id == self.expert_grader_1_id:
                    hide_g2 = True
                elif viewer_grader_id == self.expert_grader_2_id:
                    pass  # Grader 2 already submitted if their ID is assigned
                else:
                    # New grader has not submitted anything yet: hide Grader 1 to ensure blind evaluation
                    if self.expert_grader_1_id:
                        hide_g1 = True

        return {
            "id": str(self.id),
            "sample_id": self.sample_id,
            "image_path": self.image_path,
            "species": self.species,
            "body_condition": self.body_condition,
            "coat_quality": self.coat_quality,
            "eye_condition": self.eye_condition,
            "wound_presence": self.wound_presence,
            "mobility": self.mobility,
            "appetite": self.appetite,
            "weight_if_available": self.weight_if_available,
            "expert_grader_1_id": self.expert_grader_1_id if not hide_g1 else None,
            "expert_grade_1": self.expert_grade_1 if not hide_g1 else None,
            "expert_grade_1_notes": self.expert_grade_1_notes if not hide_g1 else None,
            "expert_grade_1_submitted_at": self.expert_grade_1_submitted_at.isoformat() if self.expert_grade_1_submitted_at and not hide_g1 else None,
            "expert_grader_2_id": self.expert_grader_2_id if not hide_g2 else None,
            "expert_grade_2": self.expert_grade_2 if not hide_g2 else None,
            "expert_grade_2_notes": self.expert_grade_2_notes if not hide_g2 else None,
            "expert_grade_2_submitted_at": self.expert_grade_2_submitted_at.isoformat() if self.expert_grade_2_submitted_at and not hide_g2 else None,
            "final_consensus_grade": self.final_consensus_grade,
            "consensus_reviewer_id": self.consensus_reviewer_id,
            "consensus_rationale": self.consensus_rationale,
            "consensus_reached_at": self.consensus_reached_at.isoformat() if self.consensus_reached_at else None,
            "annotation_status": self.annotation_status,
            "quality_flagged": self.quality_flagged,
            "quality_issue_reason": self.quality_issue_reason,
            "flagged_by_id": self.flagged_by_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<ExpertAnnotation(sample_id={self.sample_id}, status={self.annotation_status}, consensus={self.final_consensus_grade})>"

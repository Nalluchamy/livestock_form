import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from backend.models.expert_annotation import (
    ExpertAnnotation,
    VALID_ANNOTATION_STATUSES
)
from backend.services.exceptions import APIException


class AnnotationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_or_get_for_image(
        self,
        sample_id: str,
        image_path: str,
        species: str = "cattle"
    ) -> Tuple[ExpertAnnotation, bool]:
        """
        Creates a new expert annotation task for an ingested image if one does not exist,
        or returns the existing record. Returns (record, was_created).
        """
        stmt = select(ExpertAnnotation).where(ExpertAnnotation.sample_id == sample_id)
        existing = self.db.execute(stmt).scalar_one_or_none()
        if existing:
            return existing, False

        record = ExpertAnnotation(
            sample_id=sample_id,
            image_path=image_path,
            species=species,
            annotation_status="PENDING",
            quality_flagged=False
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record, True

    def get_by_sample_id(self, sample_id: str) -> Optional[ExpertAnnotation]:
        stmt = select(ExpertAnnotation).where(ExpertAnnotation.sample_id == sample_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, annotation_id: uuid.UUID) -> Optional[ExpertAnnotation]:
        stmt = select(ExpertAnnotation).where(ExpertAnnotation.id == annotation_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_annotations(
        self,
        status: Optional[str] = None,
        quality_flagged: Optional[bool] = None,
        species: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ExpertAnnotation], int]:
        stmt = select(ExpertAnnotation)
        count_stmt = select(func.count(ExpertAnnotation.id))

        if species:
            stmt = stmt.where(ExpertAnnotation.species == species)
            count_stmt = count_stmt.where(ExpertAnnotation.species == species)

        if status:
            upper_status = status.upper()
            if upper_status in VALID_ANNOTATION_STATUSES:
                stmt = stmt.where(ExpertAnnotation.annotation_status == upper_status)
                count_stmt = count_stmt.where(ExpertAnnotation.annotation_status == upper_status)

        if quality_flagged is not None:
            stmt = stmt.where(ExpertAnnotation.quality_flagged == quality_flagged)
            count_stmt = count_stmt.where(ExpertAnnotation.quality_flagged == quality_flagged)

        total = self.db.execute(count_stmt).scalar() or 0
        records = self.db.execute(
            stmt.order_by(desc(ExpertAnnotation.created_at)).offset(skip).limit(limit)
        ).scalars().all()

        return records, total

    def submit_grade(
        self,
        sample_id: str,
        grader_id: str,
        grade: str,
        attributes: Optional[Dict[str, Any]] = None,
        notes: Optional[str] = None
    ) -> ExpertAnnotation:
        """
        Submits an expert's grade with double-blind isolation logic:
        - If Grader 1 slot is free, assigns Grader 1.
        - If Grader 1 is current grader, updates Grader 1.
        - If Grader 2 slot is free or current grader is Grader 2, assigns Grader 2.
        - Checks for agreement: identical grades -> CONSENSUS_REACHED; different -> DISAGREEMENT.
        """
        record = self.get_by_sample_id(sample_id)
        if not record:
            raise APIException(status_code=404, error_code="NOT_FOUND", message=f"Sample '{sample_id}' not found.")

        if record.annotation_status == "REJECTED":
            raise APIException(status_code=400, error_code="SAMPLE_REJECTED", message="Cannot grade a rejected sample.")

        if record.annotation_status == "CONSENSUS_REACHED":
            raise APIException(status_code=400, error_code="CONSENSUS_FINALIZED", message="Consensus already reached for this sample.")

        grade_clean = grade.upper().strip()
        if grade_clean not in {"A", "B", "C", "D"}:
            raise APIException(status_code=422, error_code="INVALID_GRADE", message="Grade must be one of A, B, C, D.")

        now = datetime.now(timezone.utc)

        # Update physical attributes if supplied
        if attributes:
            if "body_condition" in attributes and attributes["body_condition"] is not None:
                record.body_condition = float(attributes["body_condition"])
            if "coat_quality" in attributes and attributes["coat_quality"] is not None:
                record.coat_quality = str(attributes["coat_quality"])
            if "eye_condition" in attributes and attributes["eye_condition"] is not None:
                record.eye_condition = str(attributes["eye_condition"])
            if "wound_presence" in attributes and attributes["wound_presence"] is not None:
                record.wound_presence = str(attributes["wound_presence"])
            if "mobility" in attributes and attributes["mobility"] is not None:
                record.mobility = str(attributes["mobility"])
            if "appetite" in attributes and attributes["appetite"] is not None:
                record.appetite = str(attributes["appetite"])
            if "weight_if_available" in attributes and attributes["weight_if_available"] is not None:
                record.weight_if_available = float(attributes["weight_if_available"])

        # Determine slot: Grader 1 vs Grader 2
        if record.expert_grader_1_id is None:
            # Grader 1 slot
            record.expert_grader_1_id = grader_id
            record.expert_grade_1 = grade_clean
            record.expert_grade_1_notes = notes
            record.expert_grade_1_submitted_at = now
            record.annotation_status = "PARTIALLY_ANNOTATED"
        elif record.expert_grader_1_id == grader_id:
            # Update Grader 1
            record.expert_grade_1 = grade_clean
            record.expert_grade_1_notes = notes
            record.expert_grade_1_submitted_at = now
            # If Grader 2 had also graded previously, re-evaluate consensus
            if record.expert_grade_2:
                if record.expert_grade_1 == record.expert_grade_2:
                    record.final_consensus_grade = record.expert_grade_1
                    record.annotation_status = "CONSENSUS_REACHED"
                    record.consensus_reached_at = now
                    record.consensus_rationale = f"Automatic agreement between {record.expert_grader_1_id} and {record.expert_grader_2_id}"
                else:
                    record.final_consensus_grade = None
                    record.annotation_status = "DISAGREEMENT"
        elif record.expert_grader_2_id is None or record.expert_grader_2_id == grader_id:
            # Grader 2 slot
            record.expert_grader_2_id = grader_id
            record.expert_grade_2 = grade_clean
            record.expert_grade_2_notes = notes
            record.expert_grade_2_submitted_at = now

            # Both graders have now submitted: evaluate consensus
            if record.expert_grade_1 == record.expert_grade_2:
                record.final_consensus_grade = record.expert_grade_1
                record.annotation_status = "CONSENSUS_REACHED"
                record.consensus_reached_at = now
                record.consensus_rationale = f"Automatic consensus: Both experts agreed on Grade {record.expert_grade_1}."
            else:
                record.final_consensus_grade = None
                record.annotation_status = "DISAGREEMENT"
        else:
            raise APIException(
                status_code=400,
                error_code="SLOTS_FULL",
                message=f"Both grader slots are occupied ({record.expert_grader_1_id}, {record.expert_grader_2_id}). Senior adjudication required for disagreements."
            )

        self.db.commit()
        self.db.refresh(record)
        return record

    def adjudicate_consensus(
        self,
        sample_id: str,
        reviewer_id: str,
        final_grade: str,
        rationale: str
    ) -> ExpertAnnotation:
        """
        Authoritative senior expert review to resolve inter-grader disagreement.
        """
        record = self.get_by_sample_id(sample_id)
        if not record:
            raise APIException(status_code=404, error_code="NOT_FOUND", message=f"Sample '{sample_id}' not found.")

        grade_clean = final_grade.upper().strip()
        if grade_clean not in {"A", "B", "C", "D"}:
            raise APIException(status_code=422, error_code="INVALID_GRADE", message="Final consensus grade must be one of A, B, C, D.")

        if not rationale or len(rationale.strip()) < 5:
            raise APIException(status_code=422, error_code="INVALID_RATIONALE", message="Adjudication rationale is required (minimum 5 characters).")

        now = datetime.now(timezone.utc)
        record.final_consensus_grade = grade_clean
        record.consensus_reviewer_id = reviewer_id
        record.consensus_rationale = rationale.strip()
        record.consensus_reached_at = now
        record.annotation_status = "CONSENSUS_REACHED"

        self.db.commit()
        self.db.refresh(record)
        return record

    def flag_quality_issue(
        self,
        sample_id: str,
        grader_id: str,
        reason: str
    ) -> ExpertAnnotation:
        """
        Flags an image as ungradable due to lighting, framing, occlusion, or PII.
        """
        record = self.get_by_sample_id(sample_id)
        if not record:
            raise APIException(status_code=404, error_code="NOT_FOUND", message=f"Sample '{sample_id}' not found.")

        if not reason or len(reason.strip()) < 5:
            raise APIException(status_code=422, error_code="INVALID_REASON", message="Quality issue reason is required (minimum 5 characters).")

        now = datetime.now(timezone.utc)
        record.quality_flagged = True
        record.quality_issue_reason = reason.strip()
        record.flagged_by_id = grader_id
        record.flagged_at = now
        record.annotation_status = "REJECTED"

        self.db.commit()
        self.db.refresh(record)
        return record

    def get_annotation_stats(self) -> Dict[str, Any]:
        """Calculates live metrics across the expert annotation pipeline."""
        total = self.db.execute(select(func.count(ExpertAnnotation.id))).scalar() or 0
        pending = self.db.execute(select(func.count(ExpertAnnotation.id)).where(ExpertAnnotation.annotation_status == "PENDING")).scalar() or 0
        partial = self.db.execute(select(func.count(ExpertAnnotation.id)).where(ExpertAnnotation.annotation_status == "PARTIALLY_ANNOTATED")).scalar() or 0
        consensus = self.db.execute(select(func.count(ExpertAnnotation.id)).where(ExpertAnnotation.annotation_status == "CONSENSUS_REACHED")).scalar() or 0
        disagreement = self.db.execute(select(func.count(ExpertAnnotation.id)).where(ExpertAnnotation.annotation_status == "DISAGREEMENT")).scalar() or 0
        rejected = self.db.execute(select(func.count(ExpertAnnotation.id)).where(ExpertAnnotation.annotation_status == "REJECTED")).scalar() or 0
        flagged = self.db.execute(select(func.count(ExpertAnnotation.id)).where(ExpertAnnotation.quality_flagged == True)).scalar() or 0

        # Calculate exact agreement percentage on completed double-blind samples
        double_blind_stmt = select(ExpertAnnotation).where(
            ExpertAnnotation.expert_grade_1.is_not(None),
            ExpertAnnotation.expert_grade_2.is_not(None)
        )
        double_graded = self.db.execute(double_blind_stmt).scalars().all()
        double_count = len(double_graded)
        exact_matches = sum(1 for a in double_graded if a.expert_grade_1 == a.expert_grade_2)
        agreement_pct = round((exact_matches / double_count * 100), 2) if double_count > 0 else 0.0

        return {
            "total_samples": total,
            "pending_samples": pending,
            "partially_annotated_samples": partial,
            "consensus_reached_samples": consensus,
            "disagreement_samples": disagreement,
            "rejected_samples": rejected,
            "quality_flagged_samples": flagged,
            "double_graded_samples": double_count,
            "exact_agreement_percentage": agreement_pct
        }

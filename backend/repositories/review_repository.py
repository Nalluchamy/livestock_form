import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from backend.models.disagreement_review import (
    DisagreementReview, 
    ALLOWED_STATUS_TRANSITIONS, 
    VALID_REVIEW_STATUSES
)
from backend.services.exceptions import APIException


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_review(
        self,
        original_human_grade: str,
        original_system_grade: str,
        grading_event_id: Optional[uuid.UUID] = None,
        expert_grade: Optional[str] = None,
        reviewer_rationale: Optional[str] = None,
    ) -> DisagreementReview:
        """Creates a new persistent disagreement review record."""
        review = DisagreementReview(
            grading_event_id=grading_event_id,
            original_human_grade=original_human_grade,
            original_system_grade=original_system_grade,
            expert_grade=expert_grade,
            reviewer_rationale=reviewer_rationale,
            status="PENDING",
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_review_by_id(self, review_id: uuid.UUID) -> Optional[DisagreementReview]:
        """Fetches a single review by its UUID."""
        stmt = select(DisagreementReview).where(DisagreementReview.id == review_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_reviews(
        self, 
        status: Optional[str] = None, 
        skip: int = 0, 
        limit: int = 50
    ) -> Tuple[List[DisagreementReview], int]:
        """Fetches reviews with optional status filter, pagination, and total count."""
        stmt = select(DisagreementReview)
        count_stmt = select(func.count(DisagreementReview.id))

        if status:
            upper_status = status.upper()
            stmt = stmt.where(DisagreementReview.status == upper_status)
            count_stmt = count_stmt.where(DisagreementReview.status == upper_status)

        stmt = stmt.order_by(desc(DisagreementReview.created_at)).offset(skip).limit(limit)
        reviews = list(self.db.execute(stmt).scalars().all())
        total = self.db.execute(count_stmt).scalar_one()

        return reviews, total

    def update_status(
        self,
        review_id: uuid.UUID,
        new_status: str,
        reviewer_id: Optional[str] = None,
    ) -> DisagreementReview:
        """Transitions review status ensuring validity and immutability."""
        review = self.get_review_by_id(review_id)
        if not review:
            raise APIException(message="Review not found", status_code=404)

        new_status = new_status.upper()
        if new_status not in VALID_REVIEW_STATUSES:
            raise APIException(message=f"Invalid status: '{new_status}'", status_code=400)

        # Check allowed transitions
        allowed = ALLOWED_STATUS_TRANSITIONS.get(review.status, set())
        if new_status not in allowed:
            raise APIException(
                message=f"Cannot transition review status from '{review.status}' to '{new_status}'. Allowed: {sorted(list(allowed))}",
                status_code=400
            )

        review.status = new_status
        if reviewer_id:
            review.reviewer_id = reviewer_id
        review.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(review)
        return review

    def resolve_review(
        self,
        review_id: uuid.UUID,
        reviewer_id: str,
        reviewer_action: str,
        reviewer_final_decision: str,
        reviewer_rationale: str,
    ) -> DisagreementReview:
        """
        Resolves a review with an authoritative human decision.
        Strictly preserves original_human_grade and original_system_grade immutably.
        """
        review = self.get_review_by_id(review_id)
        if not review:
            raise APIException(message="Review not found", status_code=404)

        if review.status in {"RESOLVED", "CANCELLED"}:
            raise APIException(message=f"Cannot resolve review in terminal status '{review.status}'", status_code=400)

        now = datetime.now(timezone.utc)
        review.status = "RESOLVED"
        review.reviewer_id = reviewer_id
        review.reviewer_action = reviewer_action
        review.reviewer_final_decision = reviewer_final_decision
        review.reviewer_rationale = reviewer_rationale
        review.resolved_at = now
        review.updated_at = now

        self.db.commit()
        self.db.refresh(review)
        return review

    def get_review_stats(self) -> Dict[str, int]:
        """Calculates aggregated counts for dashboard reporting."""
        total = self.db.execute(select(func.count(DisagreementReview.id))).scalar_one()
        
        def count_by_status(st):
            return self.db.execute(
                select(func.count(DisagreementReview.id)).where(DisagreementReview.status == st)
            ).scalar_one()

        def count_by_action(act):
            return self.db.execute(
                select(func.count(DisagreementReview.id)).where(DisagreementReview.reviewer_action == act)
            ).scalar_one()

        return {
            "total_reviews": total,
            "pending_count": count_by_status("PENDING"),
            "in_review_count": count_by_status("IN_REVIEW"),
            "resolved_count": count_by_status("RESOLVED"),
            "escalated_count": count_by_status("ESCALATED"),
            "cancelled_count": count_by_status("CANCELLED"),
            "upheld_human_count": count_by_action("UPHELD_HUMAN"),
            "accepted_system_count": count_by_action("ACCEPTED_SYSTEM"),
            "expert_override_count": count_by_action("EXPERT_OVERRIDE"),
        }

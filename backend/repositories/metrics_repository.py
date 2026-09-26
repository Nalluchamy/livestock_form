from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import Dict, Any

from backend.models.fact_grading_event import FactGradingEvent
from backend.models.disagreement_review import DisagreementReview


class MetricsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_total_gradings(self) -> int:
        stmt = select(func.count(FactGradingEvent.id))
        return self.db.execute(stmt).scalar_one()

    def get_disagreement_count(self) -> int:
        stmt = select(func.count(FactGradingEvent.id)).where(
            FactGradingEvent.human_grade.is_not(None),
            FactGradingEvent.human_grade != FactGradingEvent.ai_grade
        )
        return self.db.execute(stmt).scalar_one()
        
    def get_agreement_count(self) -> int:
        stmt = select(func.count(FactGradingEvent.id)).where(
            FactGradingEvent.human_grade.is_not(None),
            FactGradingEvent.human_grade == FactGradingEvent.ai_grade
        )
        return self.db.execute(stmt).scalar_one()

    def get_average_confidence(self) -> float:
        stmt = select(func.avg(FactGradingEvent.confidence_score))
        result = self.db.execute(stmt).scalar_one_or_none()
        return round(float(result), 2) if result else 0.0

    def get_pending_reviews_count(self) -> int:
        # Check count of pending reviews in persistent DisagreementReview table
        persistent_pending = self.db.execute(
            select(func.count(DisagreementReview.id)).where(DisagreementReview.status == "PENDING")
        ).scalar_one()
        
        # Also include unreviewed events from fact table
        fact_pending = self.db.execute(
            select(func.count(FactGradingEvent.id)).where(
                FactGradingEvent.review_status == "pending",
                FactGradingEvent.human_grade != FactGradingEvent.ai_grade
            )
        ).scalar_one()
        
        return max(persistent_pending, fact_pending)

    def get_resolved_reviews_count(self) -> int:
        return self.db.execute(
            select(func.count(DisagreementReview.id)).where(DisagreementReview.status == "RESOLVED")
        ).scalar_one()

    def get_low_confidence_count(self) -> int:
        stmt = select(func.count(FactGradingEvent.id)).where(
            FactGradingEvent.confidence_score < 50.0
        )
        return self.db.execute(stmt).scalar_one()

    def get_grade_distribution(self) -> Dict[str, int]:
        dist = {"A": 0, "B": 0, "C": 0, "D": 0}
        stmt = select(FactGradingEvent.ai_grade, func.count(FactGradingEvent.id)).group_by(FactGradingEvent.ai_grade)
        rows = self.db.execute(stmt).all()
        for grade, count in rows:
            if grade in dist:
                dist[grade] = count
        return dist

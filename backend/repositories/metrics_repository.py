from sqlalchemy.orm import Session
from sqlalchemy import select, func

from backend.models.fact_grading_event import FactGradingEvent


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
        stmt = select(func.count(FactGradingEvent.id)).where(
            FactGradingEvent.review_status == "pending",
            FactGradingEvent.human_grade != FactGradingEvent.ai_grade # Example definition of pending review
        )
        return self.db.execute(stmt).scalar_one()

    def get_low_confidence_count(self) -> int:
        stmt = select(func.count(FactGradingEvent.id)).where(
            FactGradingEvent.confidence_score < 50.0
        )
        return self.db.execute(stmt).scalar_one()

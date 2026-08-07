import uuid
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from backend.models.fact_grading_event import FactGradingEvent
from backend.models.dim_sample import DimSample
from backend.models.dim_grader import DimGrader
from backend.models.dim_image import DimImage
from backend.models.dim_criterion import DimCriterion


class GradingRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_grading_event(self, event: FactGradingEvent) -> FactGradingEvent:
        """Persists a new grading event to the database."""
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_grading_event_by_id(self, event_id: uuid.UUID) -> Optional[FactGradingEvent]:
        """Fetches a single grading event by its UUID."""
        stmt = select(FactGradingEvent).where(FactGradingEvent.id == event_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_grading_events(self, skip: int = 0, limit: int = 50) -> Tuple[List[FactGradingEvent], int]:
        """Fetches a list of grading events with pagination, and the total count."""
        stmt = select(FactGradingEvent).order_by(desc(FactGradingEvent.created_at)).offset(skip).limit(limit)
        events = self.db.execute(stmt).scalars().all()
        
        count_stmt = select(func.count(FactGradingEvent.id))
        total = self.db.execute(count_stmt).scalar_one()
        
        return list(events), total

    def update_grading_event(self, event: FactGradingEvent) -> FactGradingEvent:
        """Updates an existing grading event."""
        self.db.commit()
        self.db.refresh(event)
        return event

    # --- Demo Helpers for Hackathon ---
    def create_demo_sample(self) -> DimSample:
        sample = DimSample(farm_location="Demo Farm", species="Cattle")
        self.db.add(sample)
        self.db.commit()
        self.db.refresh(sample)
        return sample

    def create_demo_grader(self) -> DimGrader:
        grader = DimGrader(role="field_grader", username=f"demo_user_{uuid.uuid4().hex[:6]}")
        self.db.add(grader)
        self.db.commit()
        self.db.refresh(grader)
        return grader

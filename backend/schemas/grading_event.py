from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

from backend.schemas.sample import DimSampleRead
from backend.schemas.grader import DimGraderRead
from backend.schemas.image import DimImageRead
from backend.schemas.criterion import DimCriterionRead


class FactGradingEventBase(BaseModel):
    sample_id: UUID
    grader_id: Optional[UUID] = None
    image_id: Optional[UUID] = None
    criterion_id: Optional[UUID] = None
    
    human_grade: Optional[str] = None
    ai_grade: Optional[str] = None
    confidence_score: Optional[float] = None
    explanation: Optional[str] = None
    
    review_status: str = "pending"
    client_offline_id: Optional[str] = None
    is_synced: bool = True


class FactGradingEventCreate(FactGradingEventBase):
    pass


class FactGradingEventUpdate(BaseModel):
    human_grade: Optional[str] = None
    ai_grade: Optional[str] = None
    confidence_score: Optional[float] = None
    explanation: Optional[str] = None
    review_status: Optional[str] = None
    is_synced: Optional[bool] = None


class FactGradingEventRead(FactGradingEventBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    
    # Optional nested representations
    sample: Optional[DimSampleRead] = None
    grader: Optional[DimGraderRead] = None
    image: Optional[DimImageRead] = None
    criterion: Optional[DimCriterionRead] = None

    model_config = ConfigDict(from_attributes=True)

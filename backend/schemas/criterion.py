from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class DimCriterionBase(BaseModel):
    attribute_name: str
    measured_value: str
    rule_condition: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class DimCriterionCreate(DimCriterionBase):
    pass


class DimCriterionUpdate(BaseModel):
    attribute_name: Optional[str] = None
    measured_value: Optional[str] = None
    rule_condition: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class DimCriterionRead(DimCriterionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

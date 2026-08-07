from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class DimSampleBase(BaseModel):
    farm_location: str
    species: str


class DimSampleCreate(DimSampleBase):
    pass


class DimSampleUpdate(BaseModel):
    farm_location: Optional[str] = None
    species: Optional[str] = None


class DimSampleRead(DimSampleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

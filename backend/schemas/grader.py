from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class DimGraderBase(BaseModel):
    username: str
    role: str
    is_active: bool = True


class DimGraderCreate(DimGraderBase):
    pass


class DimGraderUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None


class DimGraderRead(DimGraderBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

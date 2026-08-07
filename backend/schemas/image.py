from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class DimImageBase(BaseModel):
    file_path: str
    exif_stripped: bool = False
    file_size_bytes: Optional[int] = None
    resolution: Optional[str] = None


class DimImageCreate(DimImageBase):
    pass


class DimImageUpdate(BaseModel):
    exif_stripped: Optional[bool] = None
    file_size_bytes: Optional[int] = None
    resolution: Optional[str] = None


class DimImageRead(DimImageBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

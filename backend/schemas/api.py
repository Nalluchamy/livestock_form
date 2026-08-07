from typing import Dict, Any, Optional
from pydantic import BaseModel
from uuid import UUID

class GradeRequest(BaseModel):
    attributes: Dict[str, Any]
    sample_id: Optional[UUID] = None
    grader_id: Optional[UUID] = None
    image_id: Optional[UUID] = None
    human_grade: Optional[str] = None
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "sample_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "grader_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "human_grade": "A",
                "attributes": {
                    "body_condition": 3.0,
                    "coat_quality": "Smooth",
                    "eye_condition": "Clear",
                    "wound_presence": "None",
                    "mobility": "Normal",
                    "appetite": "Good"
                }
            }
        }
    }


class DisagreementRequest(BaseModel):
    human_grade: str
    system_grade: str
    reason: str
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "human_grade": "B",
                "system_grade": "C",
                "reason": "Body score borderline"
            }
        }
    }

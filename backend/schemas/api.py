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


class ProduceGradeRequest(BaseModel):
    surface_defect_pct: Optional[float] = 0.0
    ripeness_stage: Optional[str] = "RED"
    color_uniformity_pct: Optional[float] = 85.0
    bruising_severity: Optional[str] = "NONE"
    shape_circularity: Optional[float] = 0.85
    aspect_ratio: Optional[float] = 1.0
    critical_defects: Optional[list[str]] = []
    laplacian_var: Optional[float] = 150.0
    illumination_mean: Optional[float] = 120.0
    surface_occlusion_pct: Optional[float] = 0.0
    human_grade: Optional[str] = None
    sample_id: Optional[str] = None
    create_persistent_review: Optional[bool] = True

    model_config = {
        "json_schema_extra": {
            "example": {
                "surface_defect_pct": 3.5,
                "ripeness_stage": "RED",
                "color_uniformity_pct": 88.0,
                "bruising_severity": "NONE",
                "shape_circularity": 0.88,
                "aspect_ratio": 1.02,
                "critical_defects": [],
                "human_grade": "A"
            }
        }
    }


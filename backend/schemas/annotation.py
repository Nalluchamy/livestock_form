"""
Validated Expert Annotation Schema for ELHGS Real-World Datasets.
Governs double-blind expert grading inputs, missing attributes handling,
and disagreement tracking.
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
from backend.grading import constants

AnnotationStatusType = Literal[
    "PENDING", 
    "INCOMPLETE", 
    "DISAGREEMENT", 
    "CONSENSUS_REACHED", 
    "REJECTED"
]

ValidGradeType = Literal["A", "B", "C", "D"]


class ExpertAnnotationSample(BaseModel):
    """
    Schema representing a single real-world livestock annotation sample.
    """
    sample_id: str = Field(..., description="Unique sample identifier, e.g. REAL-CATTLE-001")
    image_path: Optional[str] = Field(None, description="Relative path to processed de-identified image")
    
    # Core Physical Health Attributes
    body_condition: Optional[float] = Field(None, ge=1.0, le=5.0, description="BCS on 1.0 - 5.0 scale")
    coat_quality: Optional[str] = Field(None, description="Smooth, Slightly rough, Rough, or Severe lesions")
    eye_condition: Optional[str] = Field(None, description="Clear, Slight discharge, Cloudy, or Severe infection")
    wound_presence: Optional[str] = Field(None, description="None, Minor, Moderate, or Severe")
    mobility: Optional[str] = Field(None, description="Normal, Slight limp, Lame, or Unable to stand")
    appetite: Optional[str] = Field(None, description="Good, Fair, Poor, or None")
    
    # Optional physical metrics
    weight_if_available: Optional[float] = Field(None, ge=0.0, description="Optional live animal weight in kg")

    # Double-Blind Expert Grades
    expert_grade_1: Optional[ValidGradeType] = Field(None, description="Blind grade from certified expert 1")
    expert_grade_2: Optional[ValidGradeType] = Field(None, description="Blind grade from certified expert 2")
    final_consensus_grade: Optional[ValidGradeType] = Field(None, description="Authoritative consensus or adjudicated grade")
    
    # Workflow Status
    annotation_status: AnnotationStatusType = Field("PENDING", description="Current status of the annotation record")

    @field_validator("coat_quality")
    @classmethod
    def validate_coat(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in constants.COAT_VALUES:
            raise ValueError(f"Invalid coat_quality: '{v}'. Must be one of {constants.COAT_VALUES}")
        return v

    @field_validator("eye_condition")
    @classmethod
    def validate_eye(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in constants.EYE_VALUES:
            raise ValueError(f"Invalid eye_condition: '{v}'. Must be one of {constants.EYE_VALUES}")
        return v

    @field_validator("wound_presence")
    @classmethod
    def validate_wound(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in constants.WOUND_VALUES:
            raise ValueError(f"Invalid wound_presence: '{v}'. Must be one of {constants.WOUND_VALUES}")
        return v

    @field_validator("mobility")
    @classmethod
    def validate_mobility(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in constants.MOBILITY_VALUES:
            raise ValueError(f"Invalid mobility: '{v}'. Must be one of {constants.MOBILITY_VALUES}")
        return v

    @field_validator("appetite")
    @classmethod
    def validate_appetite(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in constants.APPETITE_VALUES:
            raise ValueError(f"Invalid appetite: '{v}'. Must be one of {constants.APPETITE_VALUES}")
        return v


class AnnotationBatchSummary(BaseModel):
    total_samples: int
    complete_count: int
    pending_count: int
    disagreement_count: int
    consensus_count: int
    rejected_count: int
    inter_expert_kappa: Optional[float] = None
    inter_expert_exact_match_pct: Optional[float] = None
    inter_expert_adjacent_match_pct: Optional[float] = None

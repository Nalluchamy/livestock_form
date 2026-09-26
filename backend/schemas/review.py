from typing import Optional, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

ValidGradeType = Literal["A", "B", "C", "D"]
ReviewStatusType = Literal["PENDING", "IN_REVIEW", "RESOLVED", "ESCALATED", "CANCELLED"]
ReviewActionType = Literal[
    "UPHELD_HUMAN", 
    "ACCEPTED_SYSTEM", 
    "EXPERT_OVERRIDE", 
    "ESCALATE_TO_SENIOR", 
    "DISMISSED"
]


class CreateReviewRequest(BaseModel):
    grading_event_id: Optional[UUID] = None
    original_human_grade: ValidGradeType
    original_system_grade: ValidGradeType
    expert_grade: Optional[ValidGradeType] = None
    reviewer_rationale: Optional[str] = Field(None, max_length=2000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "original_human_grade": "B",
                "original_system_grade": "C",
                "reviewer_rationale": "Body condition score is borderline 2.0; grader assessed animal in bright sunlight."
            }
        }
    }


class ResolveReviewRequest(BaseModel):
    reviewer_id: Optional[str] = Field(None, min_length=2, max_length=100)
    reviewer_action: ReviewActionType
    reviewer_final_decision: ValidGradeType
    reviewer_rationale: str = Field(..., min_length=5, max_length=2000)

    model_config = {
        "json_schema_extra": {
            "example": {
                "reviewer_id": "SR-VET-042",
                "reviewer_action": "UPHELD_HUMAN",
                "reviewer_final_decision": "B",
                "reviewer_rationale": "Physical gait assessment confirms slight limp was temporary strain, not joint lesion."
            }
        }
    }


class UpdateReviewStatusRequest(BaseModel):
    status: Literal["IN_REVIEW", "ESCALATED", "CANCELLED"]
    reviewer_id: Optional[str] = None
    notes: Optional[str] = None


class ReviewResponse(BaseModel):
    id: str
    grading_event_id: Optional[str] = None
    original_human_grade: str
    original_system_grade: str
    expert_grade: Optional[str] = None
    status: str
    reviewer_id: Optional[str] = None
    reviewer_action: Optional[str] = None
    reviewer_final_decision: Optional[str] = None
    reviewer_rationale: Optional[str] = None
    created_at: str
    updated_at: str
    resolved_at: Optional[str] = None


class ReviewStatsResponse(BaseModel):
    total_reviews: int
    pending_count: int
    in_review_count: int
    resolved_count: int
    escalated_count: int
    cancelled_count: int
    upheld_human_count: int
    accepted_system_count: int
    expert_override_count: int

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class TriggerExperimentRequest(BaseModel):
    experiment_name: str = Field("retrospective_validation_run", min_length=3)
    dataset_version: str = Field("real-v1.0", min_length=1)
    evaluation_type: str = Field("retrospective_real", description="'retrospective_real' or 'synthetic'")
    notes: Optional[str] = None


class ExperimentResponse(BaseModel):
    id: str
    experiment_name: str
    dataset_version: str
    model_version: str
    evaluation_timestamp: str
    evaluation_type: str
    status: str
    dataset_sample_count: int
    test_sample_count: int
    performance_metrics: Dict[str, Any]
    expert_agreement_metrics: Dict[str, Any]
    confidence_distribution: Dict[str, Any]
    error_category_counts: Dict[str, Any]
    notes: Optional[str] = None
    created_at: str


class DatasetInfoResponse(BaseModel):
    real_dataset: Dict[str, Any]
    synthetic_dataset: Dict[str, Any]
    active_evaluation_mode: str
    ready_for_real_evaluation: bool

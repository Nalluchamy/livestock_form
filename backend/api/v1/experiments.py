import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.schemas.experiment import TriggerExperimentRequest
from backend.repositories.experiment_repository import ExperimentRepository
from backend.evaluation.real_dataset_runner import run_real_evaluation
from backend.services.exceptions import APIException

router = APIRouter(prefix="/experiments", tags=["Experiments"])


def serialize_experiment(e) -> dict:
    return {
        "id": str(e.id),
        "experiment_name": e.experiment_name,
        "dataset_version": e.dataset_version,
        "model_version": e.model_version,
        "evaluation_timestamp": e.evaluation_timestamp.isoformat() if e.evaluation_timestamp else None,
        "evaluation_type": e.evaluation_type,
        "status": e.status,
        "dataset_sample_count": e.dataset_sample_count,
        "test_sample_count": e.test_sample_count,
        "performance_metrics": e.performance_metrics,
        "expert_agreement_metrics": e.expert_agreement_metrics,
        "confidence_distribution": e.confidence_distribution,
        "error_category_counts": e.error_category_counts,
        "notes": e.notes,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


@router.get("", response_model=APIResponse[dict])
def list_experiments(
    evaluation_type: Optional[str] = Query(None, description="Filter by: synthetic, retrospective_real, prospective_human_assisted"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Lists persistent experiment results and benchmark evaluations."""
    repo = ExperimentRepository(db)
    experiments, total = repo.get_experiments(evaluation_type=evaluation_type, skip=skip, limit=limit)
    return success_response(
        message="Experiments retrieved successfully",
        data={
            "total": total,
            "experiments": [serialize_experiment(e) for e in experiments]
        }
    )


@router.get("/latest", response_model=APIResponse[dict])
def get_latest_experiment(
    evaluation_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Retrieves the most recent completed experiment run."""
    repo = ExperimentRepository(db)
    latest = repo.get_latest_experiment(evaluation_type=evaluation_type)
    if not latest:
        return success_response(
            message="No experiments completed yet",
            data=None
        )
    return success_response(message="Latest experiment retrieved", data=serialize_experiment(latest))


@router.get("/{experiment_id}", response_model=APIResponse[dict])
def get_experiment(
    experiment_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Retrieves detailed results for a specific experiment by ID."""
    repo = ExperimentRepository(db)
    exp = repo.get_experiment_by_id(experiment_id)
    if not exp:
        raise APIException(message="Experiment not found", status_code=404)
    return success_response(message="Experiment retrieved", data=serialize_experiment(exp))


@router.post("/run", response_model=APIResponse[dict], status_code=status.HTTP_202_ACCEPTED)
def trigger_evaluation_run(
    request: TriggerExperimentRequest,
    db: Session = Depends(get_db)
):
    """
    Triggers an evaluation run. If real data is available, executes on held-out test split.
    If real data is pending, records explicit PENDING_REAL_DATA experiment without fabrication.
    """
    result = run_real_evaluation(
        experiment_name=request.experiment_name,
        db_session=db
    )
    return success_response(
        message="Evaluation pipeline executed.",
        data=result
    )

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.repositories.metrics_repository import MetricsRepository
from backend.repositories.experiment_repository import ExperimentRepository

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_model=APIResponse[dict])
def get_metrics(db: Session = Depends(get_db)):
    """
    Retrieves live aggregated grading and review metrics for dashboards.
    """
    repo = MetricsRepository(db)
    exp_repo = ExperimentRepository(db)
    
    total = repo.get_total_gradings()
    agreements = repo.get_agreement_count()
    disagreements = repo.get_disagreement_count()
    
    # Calculate rates
    total_reviewed = agreements + disagreements
    agreement_rate = round((agreements / total_reviewed) * 100, 1) if total_reviewed > 0 else 0.0
    disagreement_rate = round((disagreements / total_reviewed) * 100, 1) if total_reviewed > 0 else 0.0
    
    latest_exp = exp_repo.get_latest_experiment()
    latest_exp_data = None
    if latest_exp:
        latest_exp_data = {
            "id": str(latest_exp.id),
            "experiment_name": latest_exp.experiment_name,
            "evaluation_type": latest_exp.evaluation_type,
            "status": latest_exp.status,
            "performance_metrics": latest_exp.performance_metrics,
            "expert_agreement_metrics": latest_exp.expert_agreement_metrics,
            "confidence_distribution": latest_exp.confidence_distribution,
            "error_category_counts": latest_exp.error_category_counts,
        }

    data = {
        "total_gradings": total,
        "agreement_rate": agreement_rate,
        "disagreement_rate": disagreement_rate,
        "average_confidence": repo.get_average_confidence(),
        "pending_reviews": repo.get_pending_reviews_count(),
        "resolved_reviews": repo.get_resolved_reviews_count(),
        "low_confidence_cases": repo.get_low_confidence_count(),
        "grade_distribution": repo.get_grade_distribution(),
        "latest_experiment": latest_exp_data
    }
    
    return success_response(message="Metrics retrieved successfully", data=data)


@router.get("/agreement", response_model=APIResponse[dict])
def get_agreement_metrics():
    """
    Retrieves empirical agreement metrics (Cohen's Kappa, Exact %, Adjacent %) 
    computed on the real validation dataset (N=32).
    """
    from backend.evaluation.agreement_metrics import evaluate_validation_dataset
    data = evaluate_validation_dataset()
    return success_response(message="Agreement metrics retrieved successfully", data=data)

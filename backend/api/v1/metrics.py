from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.repositories.metrics_repository import MetricsRepository

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("", response_model=APIResponse[dict])
def get_metrics(db: Session = Depends(get_db)):
    """
    Retrieves aggregated grading metrics for dashboards.
    """
    repo = MetricsRepository(db)
    
    total = repo.get_total_gradings()
    agreements = repo.get_agreement_count()
    disagreements = repo.get_disagreement_count()
    
    # Calculate rates
    total_reviewed = agreements + disagreements
    agreement_rate = round((agreements / total_reviewed) * 100, 1) if total_reviewed > 0 else 0.0
    disagreement_rate = round((disagreements / total_reviewed) * 100, 1) if total_reviewed > 0 else 0.0
    
    data = {
        "total_gradings": total,
        "agreement_rate": agreement_rate,
        "disagreement_rate": disagreement_rate,
        "average_confidence": repo.get_average_confidence(),
        "pending_reviews": repo.get_pending_reviews_count(),
        "low_confidence_cases": repo.get_low_confidence_count()
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


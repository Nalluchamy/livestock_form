import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.schemas.api import DisagreementRequest
from backend.repositories.review_repository import ReviewRepository

router = APIRouter(prefix="/disagreements", tags=["Disagreements"])


@router.post("", response_model=APIResponse[dict])
def submit_disagreement(request: DisagreementRequest, db: Session = Depends(get_db)):
    """
    Endpoint to log a disagreement for Senior Review.
    Persists a genuine DisagreementReview row in PostgreSQL/SQLite.
    """
    repo = ReviewRepository(db)
    review = repo.create_review(
        original_human_grade=request.human_grade,
        original_system_grade=request.system_grade,
        reviewer_rationale=request.reason
    )
    
    return success_response(
        message="Disagreement logged successfully for Senior Review.",
        data={
            "disagreement_id": str(review.id),
            "human_grade": review.original_human_grade,
            "system_grade": review.original_system_grade,
            "reason": review.reviewer_rationale,
            "review_required": True,
            "status": review.status,
            "created_at": review.created_at.isoformat()
        }
    )

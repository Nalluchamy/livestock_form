import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.schemas.api import DisagreementRequest
from backend.repositories.grading_repository import GradingRepository

router = APIRouter(prefix="/disagreements", tags=["Disagreements"])


@router.post("", response_model=APIResponse[dict])
def submit_disagreement(request: DisagreementRequest, db: Session = Depends(get_db)):
    """
    Endpoint to manually log a disagreement (if the workflow requires an explicit separate call).
    Note: The POST /grade endpoint already detects and flags disagreements automatically.
    This serves as a manual override endpoint for the frontend.
    """
    # For a hackathon, we can mock the disagreement ID generation as a standalone entity
    # Or in production, this would update an existing FactGradingEvent.
    disagreement_id = str(uuid.uuid4())
    
    return success_response(
        message="Disagreement logged successfully for Senior Review.",
        data={
            "disagreement_id": disagreement_id,
            "human_grade": request.human_grade,
            "system_grade": request.system_grade,
            "reason": request.reason,
            "review_required": True
        }
    )

import json
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.schemas.api import GradeRequest
from backend.services.api_grading_service import APIGradingService
from backend.repositories.grading_repository import GradingRepository
from backend.services.exceptions import APIException
from backend.core.auth_deps import get_current_user, optional_current_user
from backend.core.settings import settings
from backend.models.user import User
from fastapi import HTTPException, status
from typing import Optional

router = APIRouter(prefix="/grade", tags=["Grading"])
history_router = APIRouter(prefix="/grading-events", tags=["History"])


@router.post("", response_model=APIResponse[dict])
def submit_grading_event(
    request: GradeRequest, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Submits a set of attributes to the Rule Engine, generates an explainable grade,
    and persists the event to the database.
    """
    # In production or staging, unauthenticated requests are strictly rejected
    if settings.ENVIRONMENT.lower() in ("production", "staging") and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided."
        )

    # In development/test mode without auth and DEMO_MODE disabled:
    # If IDs are provided unauthenticated, reject with 401; if IDs are missing, let service validate
    if not settings.DEMO_MODE and not current_user and (request.sample_id or request.grader_id):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided."
        )

    service = APIGradingService(db)
    
    grader_id = request.grader_id or (current_user.username if current_user else None)
    result_data = service.execute_grading(
        attributes=request.attributes,
        sample_id=request.sample_id,
        grader_id=grader_id,
        image_id=request.image_id,
        human_grade=request.human_grade
    )
    
    msg = "Demo sample created automatically and grade calculated." if result_data.get("generated_demo_entities") else "Grade calculated successfully."
    return success_response(message=msg, data=result_data)


@history_router.get("", response_model=APIResponse[dict])
def get_grading_history(
    skip: int = Query(0, ge=0), 
    limit: int = Query(50, ge=1, le=100), 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    if settings.ENVIRONMENT.lower() in ("production", "staging") and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided."
        )
    """Fetches a paginated history of all grading events."""
    repo = GradingRepository(db)
    events, total = repo.get_grading_events(skip=skip, limit=limit)
    
    # Simple serialization mapping
    data = []
    for e in events:
        data.append({
            "id": str(e.id),
            "human_grade": e.human_grade,
            "ai_grade": e.ai_grade,
            "confidence_score": e.confidence_score,
            "review_status": e.review_status,
            "created_at": e.created_at.isoformat()
        })
    
    return success_response(
        message="History retrieved successfully", 
        data={"total": total, "events": data}
    )


@history_router.get("/{event_id}", response_model=APIResponse[dict])
def get_grading_event(
    event_id: UUID, 
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    if settings.ENVIRONMENT.lower() in ("production", "staging") and not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided."
        )
    """Fetches a single grading event by ID."""
    repo = GradingRepository(db)
    event = repo.get_grading_event_by_id(event_id)
    if not event:
        raise APIException(message="Grading event not found", status_code=404)
        
    return success_response(
        message="Event retrieved successfully",
        data={
            "id": str(event.id),
            "human_grade": event.human_grade,
            "ai_grade": event.ai_grade,
            "confidence_score": event.confidence_score,
            "explanation": json.loads(event.explanation) if event.explanation else [],
            "review_status": event.review_status,
            "created_at": event.created_at.isoformat()
        }
    )

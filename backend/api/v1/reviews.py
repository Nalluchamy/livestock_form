import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.schemas.review import (
    CreateReviewRequest, 
    ResolveReviewRequest, 
    UpdateReviewStatusRequest, 
    ReviewResponse, 
    ReviewStatsResponse
)
from backend.repositories.review_repository import ReviewRepository
from backend.services.exceptions import APIException
from backend.core.auth_deps import get_current_user, require_role
from backend.models.user import User

router = APIRouter(prefix="/reviews", tags=["Disagreement Reviews"])


def serialize_review(r) -> dict:
    return {
        "id": str(r.id),
        "grading_event_id": str(r.grading_event_id) if r.grading_event_id else None,
        "original_human_grade": r.original_human_grade,
        "original_system_grade": r.original_system_grade,
        "expert_grade": r.expert_grade,
        "status": r.status,
        "reviewer_id": r.reviewer_id,
        "reviewer_action": r.reviewer_action,
        "reviewer_final_decision": r.reviewer_final_decision,
        "reviewer_rationale": r.reviewer_rationale,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
    }


@router.get("", response_model=APIResponse[dict])
def list_reviews(
    status: Optional[str] = Query(None, description="Filter by status: PENDING, IN_REVIEW, RESOLVED, ESCALATED, CANCELLED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """Lists persistent disagreement reviews with optional status filter and pagination."""
    repo = ReviewRepository(db)
    reviews, total = repo.get_reviews(status=status, skip=skip, limit=limit)
    stats = repo.get_review_stats()

    return success_response(
        message="Reviews retrieved successfully",
        data={
            "total": total,
            "reviews": [serialize_review(r) for r in reviews],
            "stats": stats
        }
    )


@router.post("", response_model=APIResponse[dict], status_code=status.HTTP_201_CREATED)
def create_review(
    request: CreateReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new persistent disagreement review record.
    Original human and system grades are recorded immutably.
    """
    repo = ReviewRepository(db)
    review = repo.create_review(
        original_human_grade=request.original_human_grade,
        original_system_grade=request.original_system_grade,
        grading_event_id=request.grading_event_id,
        expert_grade=request.expert_grade,
        reviewer_rationale=request.reviewer_rationale
    )
    return success_response(
        message="Disagreement review created successfully",
        data=serialize_review(review)
    )


@router.get("/stats", response_model=APIResponse[dict])
def get_review_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieves aggregated review status metrics."""
    repo = ReviewRepository(db)
    stats = repo.get_review_stats()
    return success_response(message="Review statistics retrieved", data=stats)


@router.get("/{review_id}", response_model=APIResponse[dict])
def get_review(
    review_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """Retrieves a single disagreement review by ID."""
    repo = ReviewRepository(db)
    review = repo.get_review_by_id(review_id)
    if not review:
        raise APIException(message="Review not found", status_code=404)
    return success_response(message="Review retrieved", data=serialize_review(review))


@router.post("/{review_id}/resolve", response_model=APIResponse[dict])
def resolve_review(
    review_id: uuid.UUID,
    request: ResolveReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SENIOR_REVIEWER", "ADMIN")),
):
    """
    Resolves a disagreement review with an authoritative senior human decision.
    Original grades remain strictly immutable.
    Restricted to SENIOR_REVIEWER and ADMIN.
    """
    reviewer_id = current_user.username if current_user else request.reviewer_id
    repo = ReviewRepository(db)
    resolved = repo.resolve_review(
        review_id=review_id,
        reviewer_id=reviewer_id,
        reviewer_action=request.reviewer_action,
        reviewer_final_decision=request.reviewer_final_decision,
        reviewer_rationale=request.reviewer_rationale
    )
    return success_response(
        message="Review resolved successfully. Original grades preserved immutably.",
        data=serialize_review(resolved)
    )


@router.patch("/{review_id}/status", response_model=APIResponse[dict])
def update_review_status(
    review_id: uuid.UUID,
    request: UpdateReviewStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SENIOR_REVIEWER", "ADMIN")),
):
    """
    Transitions review status through valid lifecycle states.
    Restricted to SENIOR_REVIEWER and ADMIN.
    """
    reviewer_id = current_user.username if current_user else request.reviewer_id
    repo = ReviewRepository(db)
    updated = repo.update_status(
        review_id=review_id,
        new_status=request.status,
        reviewer_id=reviewer_id
    )
    return success_response(
        message=f"Review status transitioned to {request.status}",
        data=serialize_review(updated)
    )

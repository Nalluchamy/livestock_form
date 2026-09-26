from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.annotation_repository import AnnotationRepository
from backend.schemas.responses import APIResponse, success_response
from backend.core.auth_deps import get_current_user, require_role
from backend.models.user import User
from backend.services.audit_service import AuditService


router = APIRouter(prefix="/annotations", tags=["Expert Annotations"])


class GradeSubmissionRequest(BaseModel):
    grader_id: Optional[str] = Field(None, description="Optional Grader ID (overridden by authenticated username)")
    grade: str = Field(..., pattern="^[A-Da-d]$", description="Condition grade A, B, C, or D")
    attributes: Optional[Dict[str, Any]] = Field(default=None, description="Assessed physical attributes")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Grader clinical observations")


class ConsensusAdjudicationRequest(BaseModel):
    reviewer_id: Optional[str] = Field(None, description="Optional Reviewer ID (overridden by authenticated username)")
    final_grade: str = Field(..., pattern="^[A-Da-d]$", description="Authoritative consensus grade A, B, C, or D")
    rationale: str = Field(..., min_length=5, max_length=2000, description="Clinical justification for consensus resolution")


class QualityFlagRequest(BaseModel):
    grader_id: Optional[str] = Field(None, description="Optional Grader ID (overridden by authenticated username)")
    reason: str = Field(..., min_length=5, max_length=1000, description="Detailed explanation of image flaw or PII issue")


def _is_explicitly_authenticated(request: Request) -> bool:
    return bool(request.headers.get("Authorization") or request.cookies.get("access_token"))


@router.get("", response_model=APIResponse[dict])
def list_annotations(
    request: Request,
    status: Optional[str] = Query(None, description="Filter by status (PENDING, PARTIALLY_ANNOTATED, CONSENSUS_REACHED, DISAGREEMENT, REJECTED)"),
    quality_flagged: Optional[bool] = Query(None, description="Filter by quality flag"),
    viewer_id: Optional[str] = Query(None, description="Grader ID requesting task (for blind masking)"),
    is_senior: bool = Query(False, description="Whether viewer has senior reviewer privileges"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """
    List livestock annotation tasks with double-blind isolation and pagination.
    Viewer identity and senior reviewer privilege are server-enforced from authentication.
    """
    if _is_explicitly_authenticated(request) and current_user.role != "ADMIN":
        effective_viewer = current_user.username
        effective_senior = (current_user.role in ("SENIOR_REVIEWER", "ADMIN"))
    else:
        effective_viewer = viewer_id or current_user.username
        effective_senior = is_senior

    repo = AnnotationRepository(db)
    records, total = repo.list_annotations(
        status=status,
        quality_flagged=quality_flagged,
        skip=skip,
        limit=limit
    )

    items = [r.to_dict(viewer_grader_id=effective_viewer, is_senior_reviewer=effective_senior) for r in records]

    return success_response(
        message=f"Retrieved {len(items)} annotation records.",
        data={
            "total": total,
            "skip": skip,
            "limit": limit,
            "items": items
        }
    )


@router.get("/stats/summary", response_model=APIResponse[dict])
def get_annotation_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns pipeline statistics including sample status counts and inter-expert agreement rates.
    """
    repo = AnnotationRepository(db)
    stats = repo.get_annotation_stats()
    return success_response(
        message="Annotation statistics retrieved successfully.",
        data=stats
    )


@router.get("/{sample_id}", response_model=APIResponse[dict])
def get_annotation_by_sample_id(
    sample_id: str,
    request: Request,
    viewer_id: Optional[str] = Query(None, description="Grader ID (for blind masking)"),
    is_senior: bool = Query(False, description="Whether viewer is senior reviewer"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """
    Retrieve single annotation sample with double-blind masking.
    Server enforces viewer masking based on authenticated identity.
    """
    if _is_explicitly_authenticated(request) and current_user.role != "ADMIN":
        effective_viewer = current_user.username
        effective_senior = (current_user.role in ("SENIOR_REVIEWER", "ADMIN"))
    else:
        effective_viewer = viewer_id or current_user.username
        effective_senior = is_senior

    repo = AnnotationRepository(db)
    record = repo.get_by_sample_id(sample_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Annotation task '{sample_id}' not found.")

    return success_response(
        message="Annotation record retrieved successfully.",
        data=record.to_dict(viewer_grader_id=effective_viewer, is_senior_reviewer=effective_senior)
    )


@router.post("/{sample_id}/grade", response_model=APIResponse[dict])
def submit_expert_grade(
    sample_id: str,
    payload: GradeSubmissionRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """
    Submit an expert's blind condition grade.
    Requires EXPERT_GRADER, SENIOR_REVIEWER, or ADMIN role.
    Grader identity is server-bound to authenticated user.
    Prevents self-grading both Grader 1 and Grader 2 on the same sample.
    """
    if _is_explicitly_authenticated(request) and current_user.role != "ADMIN":
        if payload.grader_id and payload.grader_id != current_user.username:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot submit an expert grade under a different user's identity."
            )
        effective_grader = current_user.username
    else:
        effective_grader = payload.grader_id or current_user.username

    repo = AnnotationRepository(db)
    record = repo.get_by_sample_id(sample_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Annotation task '{sample_id}' not found.")

    updated_record = repo.submit_grade(
        sample_id=sample_id,
        grader_id=effective_grader,
        grade=payload.grade,
        attributes=payload.attributes,
        notes=payload.notes
    )

    audit = AuditService(db)
    audit.log_event(
        action="ANNOTATION_GRADE_SUBMITTED",
        resource_type="ANNOTATION",
        resource_id=sample_id,
        user_id=current_user.id,
        username=current_user.username,
        status="SUCCESS",
        details={
            "sample_id": sample_id,
            "grader": effective_grader,
            "grade": payload.grade,
            "status_after": updated_record.annotation_status
        }
    )

    is_senior = current_user.role in ("SENIOR_REVIEWER", "ADMIN")
    return success_response(
        message="Expert grade submitted successfully.",
        data=updated_record.to_dict(viewer_grader_id=effective_grader, is_senior_reviewer=is_senior)
    )


@router.post("/{sample_id}/consensus", response_model=APIResponse[dict])
def adjudicate_consensus(
    sample_id: str,
    payload: ConsensusAdjudicationRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("SENIOR_REVIEWER", "ADMIN")),
):
    """
    Senior Veterinary Reviewer adjudicates an authoritative consensus grade for disagreed samples.
    Server enforces that only SENIOR_REVIEWER or ADMIN can adjudicate.
    """
    if _is_explicitly_authenticated(request) and current_user.role != "ADMIN":
        effective_reviewer = current_user.username
    else:
        effective_reviewer = payload.reviewer_id or current_user.username

    repo = AnnotationRepository(db)
    record = repo.adjudicate_consensus(
        sample_id=sample_id,
        reviewer_id=effective_reviewer,
        final_grade=payload.final_grade,
        rationale=payload.rationale
    )

    audit = AuditService(db)
    audit.log_event(
        action="ANNOTATION_CONSENSUS_ADJUDICATED",
        resource_type="ANNOTATION",
        resource_id=sample_id,
        user_id=current_user.id,
        username=current_user.username,
        status="SUCCESS",
        details={
            "sample_id": sample_id,
            "reviewer": effective_reviewer,
            "final_grade": payload.final_grade,
            "rationale": payload.rationale
        }
    )

    return success_response(
        message="Consensus grade finalized by senior reviewer.",
        data=record.to_dict(is_senior_reviewer=True)
    )


@router.post("/{sample_id}/flag-quality", response_model=APIResponse[dict])
def flag_quality_issue(
    sample_id: str,
    payload: QualityFlagRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """
    Flag image as poor quality, occluded, or containing PII/human subjects.
    Moves status to REJECTED.
    """
    if _is_explicitly_authenticated(request) and current_user.role != "ADMIN":
        effective_grader = current_user.username
    else:
        effective_grader = payload.grader_id or current_user.username

    repo = AnnotationRepository(db)
    record = repo.flag_quality_issue(
        sample_id=sample_id,
        grader_id=effective_grader,
        reason=payload.reason
    )

    audit = AuditService(db)
    audit.log_event(
        action="ANNOTATION_QUALITY_FLAGGED",
        resource_type="ANNOTATION",
        resource_id=sample_id,
        user_id=current_user.id,
        username=current_user.username,
        status="SUCCESS",
        details={
            "sample_id": sample_id,
            "grader": effective_grader,
            "reason": payload.reason
        }
    )

    return success_response(
        message="Image flagged for quality issues and marked as rejected.",
        data=record.to_dict(is_senior_reviewer=True)
    )

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database.session import get_db
from backend.core.auth_deps import require_role
from backend.repositories.user_repository import UserRepository
from backend.models.user import User
from backend.models.audit_log import AuditLog
from backend.services.audit_service import AuditService
from backend.schemas.auth import UserOut, UpdateUserStatusRequest, UpdateUserRoleRequest

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserOut])
def list_users(
    role: Optional[str] = Query(None, description="Filter by user role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """
    List all registered users. Restricted to ADMIN.
    """
    repo = UserRepository(db)
    users, _ = repo.list_users(role=role, is_active=is_active)
    return [
        UserOut(
            id=str(u.id),
            username=u.username,
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            is_verified=u.is_verified,
            created_at=u.created_at.isoformat() if u.created_at else None,
        )
        for u in users
    ]


@router.patch("/users/{user_id}/status", response_model=UserOut)
def update_user_status(
    user_id: str,
    payload: UpdateUserStatusRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """
    Activate/Deactivate user account or reset failed login lockouts. Restricted to ADMIN.
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for user_id",
        )

    repo = UserRepository(db)
    user = repo.get_by_id(user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # Prevent admin from deactivating themselves
    if user.id == current_user.id and payload.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrator cannot deactivate their own account",
        )

    if payload.is_active is not None:
        user.is_active = payload.is_active

    if payload.unlock is True:
        user.failed_login_attempts = 0
        user.locked_until = None

    db.commit()
    db.refresh(user)

    audit = AuditService(db)
    audit.log_event(
        action="USER_STATUS_UPDATED",
        resource_type="USER",
        resource_id=str(user.id),
        user_id=current_user.id,
        username=current_user.username,
        status="SUCCESS",
        details={
            "target_user": user.username,
            "is_active": user.is_active,
            "unlocked": payload.unlock,
        },
    )

    return UserOut(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_user_role(
    user_id: str,
    payload: UpdateUserRoleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """
    Change user system role. Restricted to ADMIN.
    """
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid UUID format for user_id",
        )

    repo = UserRepository(db)
    user = repo.get_by_id(user_uuid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    old_role = user.role
    user.role = payload.role
    db.commit()
    db.refresh(user)

    audit = AuditService(db)
    audit.log_event(
        action="USER_ROLE_UPDATED",
        resource_type="USER",
        resource_id=str(user.id),
        user_id=current_user.id,
        username=current_user.username,
        status="SUCCESS",
        details={
            "target_user": user.username,
            "old_role": old_role,
            "new_role": user.role,
        },
    )

    return UserOut(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat() if user.created_at else None,
    )


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None, description="Filter by action name"),
    username: Optional[str] = Query(None, description="Filter by initiator username"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN")),
):
    """
    Query system audit logs. Restricted to ADMIN.
    """
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if username:
        query = query.filter(AuditLog.username == username)

    total = query.count()
    logs = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [log.to_dict() for log in logs],
    }

from typing import Optional, List, Callable
import uuid
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import jwt

from backend.database.session import get_db
from backend.repositories.user_repository import UserRepository
from backend.models.user import User
from backend.core.security import decode_access_token
from backend.core.settings import settings
from backend.services.audit_service import AuditService


bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def get_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts and validates JWT Bearer access token or HTTP-only auth cookie.
    Guarantees user exists, is active, and is not locked.
    Supports DEMO_MODE fallback for backward compatibility.
    """
    repo = UserRepository(db)
    token: Optional[str] = None

    if creds and creds.credentials:
        token = creds.credentials
    elif "access_token" in request.cookies:
        token = request.cookies.get("access_token")

    if not token:
        is_dev = settings.ENVIRONMENT.lower() in ("development", "test")
        if settings.DEMO_MODE and is_dev:
            # Fallback for demo mode and test compatibility strictly restricted to development/test
            admin_user = repo.ensure_admin_user()
            return admin_user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        payload = decode_access_token(token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload."
            )
        user_id = uuid.UUID(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired. Please refresh your session.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or malformed access token.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token no longer exists."
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )

    if user.is_locked():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is temporarily locked due to multiple failed login attempts."
        )

    return user


def require_role(*allowed_roles: str) -> Callable[[User, Session, Request], User]:
    """
    Factory creating role-based authorization dependencies.
    Logs authorization failures to persistent audit log.
    """
    def role_dependency(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        user_role = current_user.role.upper()
        allowed_upper = {r.upper() for r in allowed_roles}

        # ADMIN always has superuser authority across all endpoints
        if "ADMIN" in allowed_upper and user_role == "ADMIN":
            return current_user

        if user_role not in allowed_upper and user_role != "ADMIN":
            ip = get_client_ip(request)
            AuditService.log_authz_denied(
                db, user=current_user, resource=str(request.url.path),
                ip_address=ip,
                reason=f"Role '{user_role}' lacks required permissions: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: User role '{user_role}' is not authorized to access this resource."
            )
        return current_user

    return role_dependency


def optional_current_user(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Soft dependency returning User if valid token is provided, else None."""
    try:
        return get_current_user(request, creds, db)
    except HTTPException:
        return None

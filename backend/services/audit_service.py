import uuid
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.models.audit_log import AuditLog
from backend.models.user import User
from backend.core.logging import logger


SENSITIVE_KEYS = {"password", "token", "secret", "refresh_token", "access_token", "authorization", "cookie"}


def sanitize_audit_details(details: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not details:
        return {}
    clean = {}
    for k, v in details.items():
        if any(s in k.lower() for s in SENSITIVE_KEYS):
            clean[k] = "[REDACTED]"
        elif isinstance(v, dict):
            clean[k] = sanitize_audit_details(v)
        else:
            clean[k] = v
    return clean


class AuditService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db

    @staticmethod
    def _execute_log(
        active_db: Session,
        action: str,
        resource_type: str,
        status: str = "SUCCESS",
        user_id: Optional[uuid.UUID] = None,
        username: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        if not active_db:
            logger.warning(f"AuditService called without active DB session for action '{action}'.")
            return None
        try:
            clean_details = sanitize_audit_details(details)
            entry = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                resource_type=resource_type or "system",
                resource_id=resource_id,
                ip_address=ip_address,
                status=status,
                details=clean_details
            )
            active_db.add(entry)
            active_db.commit()
            active_db.refresh(entry)
            return entry
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            active_db.rollback()
            return None

    def log_event(
        self,
        *args,
        **kwargs
    ) -> Optional[AuditLog]:
        """
        Universal audit logging method.
        Supports:
          - instance: audit_svc.log_event(action=..., resource_type=..., ...)
          - class/static: AuditService.log_event(db, action=..., resource_type=..., ...)
        """
        if isinstance(self, Session):
            active_db = self
            action = kwargs.pop("action", args[0] if len(args) > 0 else "SYSTEM_EVENT")
            resource_type = kwargs.pop("resource_type", args[1] if len(args) > 1 else "system")
            return AuditService._execute_log(active_db, action, resource_type, **kwargs)
        else:
            active_db = kwargs.pop("db", getattr(self, "db", None))
            action = kwargs.pop("action", args[0] if len(args) > 0 else "SYSTEM_EVENT")
            resource_type = kwargs.pop("resource_type", args[1] if len(args) > 1 else "system")
            return AuditService._execute_log(active_db, action, resource_type, **kwargs)

    @classmethod
    def record_event(
        cls,
        db: Session,
        action: str,
        resource_type: str,
        status: str = "SUCCESS",
        user_id: Optional[uuid.UUID] = None,
        username: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        return cls._execute_log(
            active_db=db,
            action=action,
            resource_type=resource_type,
            status=status,
            user_id=user_id,
            username=username,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details
        )

    @classmethod
    def log_auth_success(cls, db: Session, user: User, ip_address: Optional[str] = None):
        cls.record_event(
            db=db,
            action="AUTH_LOGIN_SUCCESS",
            resource_type="auth",
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            details={"role": user.role}
        )

    @classmethod
    def log_auth_failure(cls, db: Session, identifier: str, ip_address: Optional[str] = None, reason: str = "Invalid credentials"):
        cls.record_event(
            db=db,
            action="AUTH_LOGIN_FAILURE",
            resource_type="auth",
            status="FAILURE",
            username=identifier,
            ip_address=ip_address,
            details={"reason": reason}
        )

    @classmethod
    def log_auth_lockout(cls, db: Session, user: User, ip_address: Optional[str] = None):
        cls.record_event(
            db=db,
            action="AUTH_ACCOUNT_LOCKED",
            resource_type="auth",
            status="FAILURE",
            user_id=user.id,
            username=user.username,
            ip_address=ip_address,
            details={"failed_attempts": user.failed_login_attempts}
        )

    @classmethod
    def log_auth_logout(cls, db: Session, user: User, ip_address: Optional[str] = None):
        cls.record_event(
            db=db,
            action="AUTH_LOGOUT",
            resource_type="auth",
            user_id=user.id,
            username=user.username,
            ip_address=ip_address
        )

    @classmethod
    def log_authz_denied(cls, db: Session, user: Optional[User], resource: str, ip_address: Optional[str] = None, reason: str = "Insufficient role permissions"):
        cls.record_event(
            db=db,
            action="AUTHZ_ACCESS_DENIED",
            resource_type=resource,
            status="FAILURE",
            user_id=user.id if user else None,
            username=user.username if user else "anonymous",
            ip_address=ip_address,
            details={"reason": reason, "user_role": user.role if user else None}
        )

import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class AuditLog(Base):
    """
    Persistent table for security-relevant operations and audit events.
    Records authentication events, authorization failures, annotation submissions,
    review adjudications, dataset imports, and administrative actions without logging secrets.
    """
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=True
    )
    username: Mapped[Optional[str]] = mapped_column(
        String(100), index=True, nullable=True
    )
    action: Mapped[str] = mapped_column(
        String(100), index=True, nullable=False
    )
    resource_type: Mapped[str] = mapped_column(
        String(100), index=True, nullable=False
    )
    resource_id: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="SUCCESS", index=True, nullable=False
    )
    details: Mapped[Dict[str, Any]] = mapped_column(
        JSON, default=dict, nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "username": self.username,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "ip_address": self.ip_address,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }

    def __repr__(self) -> str:
        return f"<AuditLog(action={self.action}, user={self.username}, status={self.status})>"

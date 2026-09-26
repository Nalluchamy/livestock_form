import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class RefreshToken(Base):
    """
    Persistent model for tracking rotatable, single-use refresh tokens.
    Hashed token values are stored to prevent theft in case of database leakage.
    """
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    token_hash: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    def is_valid(self) -> bool:
        if self.revoked:
            return False
        now = datetime.now(timezone.utc)
        if self.expires_at.tzinfo is None:
            now = datetime.utcnow()
        return self.expires_at > now

    def __repr__(self) -> str:
        return f"<RefreshToken(user_id={self.user_id}, valid={self.is_valid()})>"

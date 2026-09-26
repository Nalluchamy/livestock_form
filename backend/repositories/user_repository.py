import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc, or_

from backend.models.user import User
from backend.models.refresh_token import RefreshToken
from backend.core.security import hash_password, verify_password, hash_token, generate_secure_token
from backend.core.settings import settings


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.username) == username.lower().strip())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.email) == email.lower().strip())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        clean = identifier.lower().strip()
        stmt = select(User).where(
            or_(func.lower(User.username) == clean, func.lower(User.email) == clean)
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "FARMER",
        is_verified: bool = False,
        is_active: bool = True
    ) -> User:
        hashed = hash_password(password)
        act_token = generate_secure_token(32) if not is_verified else None

        user = User(
            username=username.strip(),
            email=email.lower().strip(),
            hashed_password=hashed,
            role=role.upper().strip(),
            is_active=is_active,
            is_verified=is_verified,
            activation_token=act_token,
            failed_login_attempts=0
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_users(
        self,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[User], int]:
        stmt = select(User)
        count_stmt = select(func.count(User.id))

        if role:
            stmt = stmt.where(User.role == role.upper())
            count_stmt = count_stmt.where(User.role == role.upper())
        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
            count_stmt = count_stmt.where(User.is_active == is_active)

        total = self.db.execute(count_stmt).scalar() or 0
        users = self.db.execute(
            stmt.order_by(desc(User.created_at)).offset(skip).limit(limit)
        ).scalars().all()

        return users, total

    def record_failed_attempt(self, user: User) -> bool:
        """
        Increments failed login attempts. Locks account if threshold is met.
        Returns True if account became locked.
        """
        user.failed_login_attempts += 1
        now = datetime.now(timezone.utc)
        locked = False
        if user.failed_login_attempts >= settings.LOCKOUT_MAX_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            locked = True
        self.db.commit()
        self.db.refresh(user)
        return locked

    def reset_failed_attempts(self, user: User):
        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.commit()
        self.db.refresh(user)

    def activate_user_by_token(self, token: str) -> Optional[User]:
        stmt = select(User).where(User.activation_token == token)
        user = self.db.execute(stmt).scalar_one_or_none()
        if not user:
            return None
        user.is_verified = True
        user.activation_token = None
        self.db.commit()
        self.db.refresh(user)
        return user

    def set_password_reset_token(self, user: User) -> str:
        raw_token = generate_secure_token(32)
        user.reset_token = hash_token(raw_token)
        now = datetime.now(timezone.utc)
        user.reset_token_expires_at = now + timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
        self.db.commit()
        self.db.refresh(user)
        return raw_token

    def reset_password_by_token(self, raw_token: str, new_password: str) -> Optional[User]:
        token_hashed = hash_token(raw_token)
        stmt = select(User).where(User.reset_token == token_hashed)
        user = self.db.execute(stmt).scalar_one_or_none()
        if not user:
            return None
        now = datetime.now(timezone.utc)
        exp = user.reset_token_expires_at
        if exp:
            if exp.tzinfo is None:
                now = datetime.utcnow()
            if exp < now:
                return None

        user.hashed_password = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires_at = None
        user.failed_login_attempts = 0
        user.locked_until = None
        self.db.commit()
        self.db.refresh(user)
        return user

    # --- Refresh Token Methods ---

    def create_refresh_token(self, user_id: uuid.UUID, token_hash: str) -> RefreshToken:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        rt = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            revoked=False
        )
        self.db.add(rt)
        self.db.commit()
        self.db.refresh(rt)
        return rt

    def get_valid_refresh_token(self, token_hash: str) -> Optional[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False
        )
        rt = self.db.execute(stmt).scalar_one_or_none()
        if rt and rt.is_valid():
            return rt
        return None

    def get_refresh_token_any_status(self, token_hash: str) -> Optional[RefreshToken]:
        """Fetches a refresh token by hash regardless of revocation status (for reuse detection)."""
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke_refresh_token(self, token_hash: str):
        stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        rt = self.db.execute(stmt).scalar_one_or_none()
        if rt:
            rt.revoked = True
            self.db.commit()

    def revoke_all_user_tokens(self, user_id: uuid.UUID):
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked == False
        )
        tokens = self.db.execute(stmt).scalars().all()
        for t in tokens:
            t.revoked = True
        self.db.commit()

    def ensure_admin_user(self) -> User:
        """Bootstraps a default admin user if no admin exists in database."""
        admin = self.get_by_username(settings.ADMIN_DEFAULT_USERNAME)
        if not admin:
            admin = self.create_user(
                username=settings.ADMIN_DEFAULT_USERNAME,
                email=settings.ADMIN_DEFAULT_EMAIL,
                password=settings.ADMIN_DEFAULT_PASSWORD,
                role="ADMIN",
                is_verified=True,
                is_active=True
            )
        return admin

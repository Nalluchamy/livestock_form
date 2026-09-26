"""
Security Core Module for ELHGS.
Provides:
- Bcrypt password hashing and verification
- JWT creation, verification, and decoding (short-lived access tokens)
- Cryptographically secure refresh token hashing and generation
- Account activation and password reset tokens
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Tuple, Optional
import bcrypt
import jwt

from backend.core.settings import settings


VALID_ROLES = {"FARMER", "EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN"}


def hash_password(password: str) -> str:
    """Hashes a plaintext password using bcrypt with 12 salt rounds."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generates a short-lived JSON Web Token (JWT) access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": now})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates a JWT access token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def generate_secure_token(nbytes: int = 32) -> str:
    """Generates a URL-safe random string for activation or password reset."""
    return secrets.token_urlsafe(nbytes)


def hash_token(raw_token: str) -> str:
    """Computes SHA-256 hash of a token for secure database storage."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def create_refresh_token_pair() -> Tuple[str, str]:
    """
    Returns (raw_token, hashed_token).
    The raw_token is returned to the user; the hashed_token is stored in DB.
    """
    raw_token = secrets.token_urlsafe(48)
    hashed = hash_token(raw_token)
    return raw_token, hashed

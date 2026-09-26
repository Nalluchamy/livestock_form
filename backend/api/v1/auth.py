from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RegisterRequest,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirmRequest,
    ActivateAccountRequest,
    UserOut
)
from backend.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token_pair,
    hash_token,
    VALID_ROLES
)
from backend.models.user import User
from backend.core.auth_deps import get_current_user, get_client_ip
from backend.core.settings import settings
from backend.services.audit_service import AuditService
from backend.schemas.responses import APIResponse, success_response


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Authenticates user credentials. Protects against brute-force attacks by
    locking accounts after 5 failed attempts and logs all attempts into audit log.
    """
    repo = UserRepository(db)
    ip = get_client_ip(request)

    user = repo.get_by_username_or_email(payload.username_or_email)
    if not user:
        AuditService.log_auth_failure(db, payload.username_or_email, ip, reason="User not found")
        # Protection against account enumeration: return identical message and delay slightly
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )

    if user.is_locked():
        AuditService.log_auth_lockout(db, user, ip)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is temporarily locked due to multiple failed login attempts. Please try again later or reset password."
        )

    if not verify_password(payload.password, user.hashed_password):
        locked = repo.record_failed_attempt(user)
        AuditService.log_auth_failure(db, user.username, ip, reason="Invalid password")
        if locked:
            AuditService.log_auth_lockout(db, user, ip)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account has been temporarily locked due to excessive failed attempts."
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password."
        )

    if not user.is_active:
        AuditService.log_auth_failure(db, user.username, ip, reason="Account deactivated")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Please contact an administrator."
        )

    # Success: reset failed attempts
    repo.reset_failed_attempts(user)

    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )

    # Generate and store single-use refresh token
    raw_refresh_token, token_hash = create_refresh_token_pair()
    repo.create_refresh_token(user.id, token_hash)

    # Record audit log
    AuditService.log_auth_success(db, user, ip)

    # Set secure HTTP-only cookie if enabled
    if settings.SECURE_COOKIES:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    return success_response(
        message="Login successful.",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=UserOut(**user.to_dict())
        )
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
def refresh_session_token(
    payload: RefreshTokenRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Implements single-use refresh-token rotation:
    Validates refresh token, revokes it immediately, and issues a fresh token pair.
    """
    repo = UserRepository(db)
    token_hash = hash_token(payload.refresh_token)

    # Check for reuse of an already-revoked refresh token (RFC 6819 Token Reuse Detection)
    existing_token = repo.get_refresh_token_any_status(token_hash)
    if existing_token and existing_token.revoked:
        # Compromised token family detected: invalidate all sessions for this account immediately
        repo.revoke_all_user_tokens(existing_token.user_id)
        user = repo.get_by_id(existing_token.user_id)
        username = user.username if user else "unknown"
        AuditService.record_event(
            db=db,
            action="AUTH_TOKEN_REUSE_DETECTED",
            resource_type="auth",
            status="FAILURE",
            user_id=existing_token.user_id,
            username=username,
            ip_address=get_client_ip(request),
            details={"reason": "Revoked refresh token presented; all active user sessions invalidated."}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected. All active sessions for this account have been revoked for security."
        )

    rt = repo.get_valid_refresh_token(token_hash)
    if not rt:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked refresh token."
        )

    user = repo.get_by_id(rt.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or deleted."
        )

    # Revoke old refresh token (single-use rotation)
    repo.revoke_refresh_token(token_hash)

    # Issue new token pair
    new_access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role}
    )
    new_raw_refresh, new_token_hash = create_refresh_token_pair()
    repo.create_refresh_token(user.id, new_token_hash)

    AuditService.log_event(
        db, action="AUTH_TOKEN_ROTATED", resource_type="auth",
        user_id=user.id, username=user.username, ip_address=get_client_ip(request)
    )

    if settings.SECURE_COOKIES:
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    return success_response(
        message="Session refreshed successfully.",
        data=TokenResponse(
            access_token=new_access_token,
            refresh_token=new_raw_refresh,
            token_type="bearer",
            expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            user=UserOut(**user.to_dict())
        )
    )


@router.post("/logout", response_model=APIResponse[dict])
def logout(
    request: Request,
    response: Response,
    payload: Optional[RefreshTokenRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revokes active refresh token and clears auth cookies."""
    repo = UserRepository(db)
    if payload and payload.refresh_token:
        token_hash = hash_token(payload.refresh_token)
        repo.revoke_refresh_token(token_hash)
    else:
        # Revoke all active tokens for this user upon explicit logout
        repo.revoke_all_user_tokens(current_user.id)

    AuditService.log_auth_logout(db, current_user, get_client_ip(request))

    response.delete_cookie("access_token")

    return success_response(
        message="Logged out successfully.",
        data={"user_id": str(current_user.id), "username": current_user.username}
    )


@router.post("/register", response_model=APIResponse[dict])
def register_user(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Registers a new user account with activation token.
    Default role is FARMER. Privileged roles require admin verification.
    """
    repo = UserRepository(db)

    if repo.get_by_username(payload.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken."
        )

    if repo.get_by_email(payload.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address already registered."
        )

    role = payload.role.upper()
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid role. Allowed roles: {list(VALID_ROLES)}"
        )

    # Automatically activate FARMER in demo mode, else require activation
    is_verified = settings.DEMO_MODE

    user = repo.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role=role,
        is_verified=is_verified,
        is_active=True
    )

    AuditService.log_event(
        db, action="AUTH_USER_REGISTERED", resource_type="user",
        user_id=user.id, username=user.username, ip_address=get_client_ip(request),
        details={"role": user.role, "verified": user.is_verified}
    )

    return success_response(
        message="User account registered successfully.",
        data={
            "user": user.to_dict(),
            "activation_token": user.activation_token if not is_verified else None,
            "message": "Account activated automatically." if is_verified else "Please activate your account with the provided token."
        }
    )


@router.post("/activate", response_model=APIResponse[dict])
def activate_account(payload: ActivateAccountRequest, db: Session = Depends(get_db)):
    """Activates user account using registration token."""
    repo = UserRepository(db)
    user = repo.activate_user_by_token(payload.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired activation token."
        )

    AuditService.log_event(
        db, action="AUTH_ACCOUNT_ACTIVATED", resource_type="user",
        user_id=user.id, username=user.username
    )

    return success_response(
        message="Account activated successfully. You can now log in.",
        data={"username": user.username, "is_verified": user.is_verified}
    )


@router.post("/forgot-password", response_model=APIResponse[dict])
def request_password_reset(
    payload: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Generates a password reset token. Always returns success to protect against account enumeration.
    """
    repo = UserRepository(db)
    user = repo.get_by_username_or_email(payload.username_or_email)
    raw_token = None
    if user and user.is_active:
        raw_token = repo.set_password_reset_token(user)
        AuditService.log_event(
            db, action="AUTH_PASSWORD_RESET_REQUESTED", resource_type="user",
            user_id=user.id, username=user.username, ip_address=get_client_ip(request)
        )

    return success_response(
        message="If an active account exists with the provided identifier, password reset instructions have been issued.",
        data={"reset_token": raw_token if settings.DEMO_MODE else None}
    )


@router.post("/reset-password", response_model=APIResponse[dict])
def confirm_password_reset(
    payload: PasswordResetConfirmRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Resets user password using valid, unexpired reset token."""
    repo = UserRepository(db)
    user = repo.reset_password_by_token(payload.token, payload.new_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )

    # Invalidate all existing refresh tokens for security
    repo.revoke_all_user_tokens(user.id)

    AuditService.log_event(
        db, action="AUTH_PASSWORD_RESET_COMPLETED", resource_type="user",
        user_id=user.id, username=user.username, ip_address=get_client_ip(request)
    )

    return success_response(
        message="Password has been reset successfully. Please log in with your new password.",
        data={"username": user.username}
    )


@router.get("/me", response_model=APIResponse[UserOut])
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Returns profile information for the authenticated user."""
    return success_response(
        message="Profile retrieved.",
        data=UserOut(**current_user.to_dict())
    )

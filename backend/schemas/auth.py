from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[str] = None


class LoginRequest(BaseModel):
    username_or_email: str = Field(..., min_length=2, max_length=255, description="Username or email address")
    password: str = Field(..., min_length=6, max_length=128, description="Account password")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user: UserOut


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128, description="Minimum 8 characters")
    role: str = Field(default="FARMER", description="Role: FARMER, EXPERT_GRADER, SENIOR_REVIEWER, ADMIN")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20, description="Active refresh token")


class PasswordResetRequest(BaseModel):
    username_or_email: str = Field(..., min_length=2, max_length=255)


class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(..., min_length=20)
    new_password: str = Field(..., min_length=8, max_length=128)


class ActivateAccountRequest(BaseModel):
    token: str = Field(..., min_length=20)


class UpdateUserStatusRequest(BaseModel):
    is_active: Optional[bool] = None
    unlock: Optional[bool] = None


class UpdateUserRoleRequest(BaseModel):
    role: str = Field(..., pattern="^(FARMER|EXPERT_GRADER|SENIOR_REVIEWER|ADMIN)$")

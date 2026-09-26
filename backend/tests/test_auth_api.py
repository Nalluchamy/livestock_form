import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.settings import settings
from backend.models.user import User
from backend.models.refresh_token import RefreshToken
from backend.repositories.user_repository import UserRepository
from backend.core.security import create_access_token


def test_login_success_with_default_admin(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    repo.ensure_admin_user()

    res = client.post("/api/v1/auth/login", json={
        "username_or_email": settings.ADMIN_DEFAULT_USERNAME,
        "password": settings.ADMIN_DEFAULT_PASSWORD,
    })
    assert res.status_code == 200
    data = res.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == settings.ADMIN_DEFAULT_USERNAME
    assert data["user"]["role"] == "ADMIN"


def test_login_invalid_password_returns_401(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    repo.ensure_admin_user()

    res = client.post("/api/v1/auth/login", json={
        "username_or_email": settings.ADMIN_DEFAULT_USERNAME,
        "password": "WrongPassword123!",
    })
    assert res.status_code == 401
    assert "Invalid" in res.json()["detail"]


def test_account_lockout_after_5_failed_attempts(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    repo.ensure_admin_user()

    # 5 failed attempts
    for _ in range(5):
        res = client.post("/api/v1/auth/login", json={
            "username_or_email": settings.ADMIN_DEFAULT_USERNAME,
            "password": "WrongPassword!",
        })
        assert res.status_code in (401, 403)

    # 6th attempt should be locked out
    res6 = client.post("/api/v1/auth/login", json={
        "username_or_email": settings.ADMIN_DEFAULT_USERNAME,
        "password": settings.ADMIN_DEFAULT_PASSWORD,
    })
    assert res6.status_code == 403
    assert "temporarily locked" in res6.json()["detail"]


def test_user_enumeration_defense(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    repo.ensure_admin_user()

    # Non-existent user
    res1 = client.post("/api/v1/auth/login", json={
        "username_or_email": "non_existent_user_999",
        "password": "SomePassword123!",
    })

    # Existing user, wrong password
    res2 = client.post("/api/v1/auth/login", json={
        "username_or_email": settings.ADMIN_DEFAULT_USERNAME,
        "password": "IncorrectPassword123!",
    })

    assert res1.status_code == 401
    assert res2.status_code == 401
    assert res1.json()["detail"] == res2.json()["detail"]


def test_token_refresh_rotation_and_single_use(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    repo.ensure_admin_user()

    # 1. Login
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": settings.ADMIN_DEFAULT_USERNAME,
        "password": settings.ADMIN_DEFAULT_PASSWORD,
    })
    data = login_res.json()["data"]
    rt1 = data["refresh_token"]

    # 2. Refresh
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": rt1})
    assert ref_res.status_code == 200
    ref_data = ref_res.json()["data"]
    assert "access_token" in ref_data
    rt2 = ref_data["refresh_token"]
    assert rt2 != rt1

    # 3. Reusing old refresh token rt1 should be rejected (single-use rotation)
    replay_res = client.post("/api/v1/auth/refresh", json={"refresh_token": rt1})
    assert replay_res.status_code == 401


def test_logout_revokes_refresh_token(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    repo.ensure_admin_user()

    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": settings.ADMIN_DEFAULT_USERNAME,
        "password": settings.ADMIN_DEFAULT_PASSWORD,
    })
    tokens = login_res.json()["data"]
    rt = tokens["refresh_token"]

    # Logout
    logout_res = client.post("/api/v1/auth/logout", json={"refresh_token": rt})
    assert logout_res.status_code == 200

    # Refresh after logout should fail
    ref_res = client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
    assert ref_res.status_code == 401


def test_registration_and_activation(client: TestClient, db_session: Session):
    settings.DEMO_MODE = False
    reg_payload = {
        "username": "vet_dr_lee",
        "email": "lee@vetclinic.internal",
        "password": "SecurePassword2026!",
        "role": "EXPERT_GRADER"
    }
    res = client.post("/api/v1/auth/register", json=reg_payload)
    assert res.status_code in (200, 201)
    user_data = res.json()["data"]["user"]
    assert user_data["username"] == "vet_dr_lee"
    assert user_data["role"] == "EXPERT_GRADER"


def test_password_reset_flow(client: TestClient, db_session: Session):
    settings.DEMO_MODE = True
    repo = UserRepository(db_session)
    user = repo.create_user("reset_user", "reset@test.com", "OldPassword2026!", "FARMER")

    # 1. Request reset token
    forgot_res = client.post("/api/v1/auth/forgot-password", json={"username_or_email": "reset_user"})
    assert forgot_res.status_code == 200
    reset_token = forgot_res.json()["data"]["reset_token"]
    assert reset_token is not None

    # 2. Confirm reset
    confirm_res = client.post("/api/v1/auth/reset-password", json={
        "token": reset_token,
        "new_password": "NewStrongPassword2026!"
    })
    assert confirm_res.status_code == 200

    # 3. Login with new password
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "reset_user",
        "password": "NewStrongPassword2026!"
    })
    assert login_res.status_code == 200


def test_get_current_user_profile(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    user = repo.create_user("profile_user", "prof@test.com", "Pass123456!", "SENIOR_REVIEWER")
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})

    # Valid token
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["username"] == "profile_user"
    assert data["role"] == "SENIOR_REVIEWER"

    # Missing token when DEMO_MODE=False
    settings.DEMO_MODE = False
    unauth_res = client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401


def test_expired_access_token_rejected(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    user = repo.create_user("expired_user", "exp@test.com", "Pass123456!", "FARMER")
    expired_token = create_access_token(
        {"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=timedelta(seconds=-10)
    )

    settings.DEMO_MODE = False
    res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired_token}"})
    assert res.status_code == 401
    assert "expired" in res.json()["detail"].lower()


def test_refresh_token_reuse_family_revocation(client: TestClient, db_session: Session):
    """
    Tests RFC 6819 Refresh Token Reuse Detection:
    When an already-revoked refresh token is presented, the entire token family
    for that user must be invalidated immediately.
    """
    repo = UserRepository(db_session)
    user = repo.create_user("reuse_victim", "victim@test.com", "VictimPass2026!", "EXPERT_GRADER")

    # 1. User logs in, gets rt1
    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "reuse_victim",
        "password": "VictimPass2026!",
    })
    assert login_res.status_code == 200
    rt1 = login_res.json()["data"]["refresh_token"]

    # 2. Legitimate user rotates session: rt1 -> rt2 (rt1 is now revoked)
    rotate_res = client.post("/api/v1/auth/refresh", json={"refresh_token": rt1})
    assert rotate_res.status_code == 200
    rt2 = rotate_res.json()["data"]["refresh_token"]

    # 3. Attacker replays revoked token rt1
    reuse_res = client.post("/api/v1/auth/refresh", json={"refresh_token": rt1})
    assert reuse_res.status_code == 401
    assert "reuse detected" in reuse_res.json()["detail"].lower()

    # 4. Legitimate rt2 should NOW also be revoked due to family invalidation
    legit_after_reuse = client.post("/api/v1/auth/refresh", json={"refresh_token": rt2})
    assert legit_after_reuse.status_code == 401


def test_demo_mode_cannot_bypass_in_production_or_staging(client: TestClient, db_session: Session):
    """
    Ensures DEMO_MODE=True cannot bypass authentication when ENVIRONMENT is
    set to production or staging.
    """
    # Case 1: production
    settings.ENVIRONMENT = "production"
    settings.DEMO_MODE = True
    res_prod = client.get("/api/v1/auth/me")
    assert res_prod.status_code == 401
    assert "credentials were not provided" in res_prod.json()["detail"].lower()

    # Case 2: staging
    settings.ENVIRONMENT = "staging"
    settings.DEMO_MODE = True
    res_staging = client.get("/api/v1/auth/me")
    assert res_staging.status_code == 401

    # Restore environment
    settings.ENVIRONMENT = "development"

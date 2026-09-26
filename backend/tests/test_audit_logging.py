import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.core.settings import settings
from backend.models.user import User
from backend.models.audit_log import AuditLog
from backend.repositories.user_repository import UserRepository
from backend.repositories.annotation_repository import AnnotationRepository
from backend.services.audit_service import AuditService, sanitize_audit_details
from backend.core.security import create_access_token


def make_auth_header(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def test_sensitive_data_automatically_redacted():
    dirty_payload = {
        "username": "vet_grader",
        "password": "SecretSuperPassword123!",
        "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
        "refresh_token": "random_secret_refresh_token",
        "nested": {
            "api_secret": "top_secret_key",
            "normal_field": "valid_value"
        },
        "safe_score": 3.5
    }
    cleaned = sanitize_audit_details(dirty_payload)
    assert cleaned["username"] == "vet_grader"
    assert cleaned["password"] == "[REDACTED]"
    assert cleaned["access_token"] == "[REDACTED]"
    assert cleaned["refresh_token"] == "[REDACTED]"
    assert cleaned["nested"]["api_secret"] == "[REDACTED]"
    assert cleaned["nested"]["normal_field"] == "valid_value"
    assert cleaned["safe_score"] == 3.5


def test_login_events_recorded_in_audit_log(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    user = repo.create_user("audit_test_user", "audit@test.com", "Password2026!", "EXPERT_GRADER")

    # 1. Failed login attempt
    client.post("/api/v1/auth/login", json={
        "username_or_email": "audit_test_user",
        "password": "WrongPassword!",
    })

    fail_log = db_session.execute(
        select(AuditLog).where(AuditLog.action == "AUTH_LOGIN_FAILURE")
    ).scalar_one_or_none()
    assert fail_log is not None
    assert fail_log.status == "FAILURE"
    assert fail_log.username == "audit_test_user"

    # 2. Successful login
    client.post("/api/v1/auth/login", json={
        "username_or_email": "audit_test_user",
        "password": "Password2026!",
    })

    success_log = db_session.execute(
        select(AuditLog).where(AuditLog.action == "AUTH_LOGIN_SUCCESS")
    ).scalar_one_or_none()
    assert success_log is not None
    assert success_log.status == "SUCCESS"
    assert success_log.user_id == user.id
    assert "password" not in str(success_log.details)


def test_grade_submission_audit_logging(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    grader = repo.create_user("audit_grader_01", "ag@test.com", "Password2026!", "EXPERT_GRADER")
    ann_repo = AnnotationRepository(db_session)
    ann_repo.create_or_get_for_image("CATTLE-AUDIT-01", "path/to/img.jpg")

    headers = make_auth_header(grader)
    res = client.post(
        "/api/v1/annotations/CATTLE-AUDIT-01/grade",
        json={"grade": "B", "notes": "Active posture"},
        headers=headers
    )
    assert res.status_code == 200

    grade_log = db_session.execute(
        select(AuditLog).where(AuditLog.action == "ANNOTATION_GRADE_SUBMITTED")
    ).scalar_one_or_none()
    assert grade_log is not None
    assert grade_log.resource_id == "CATTLE-AUDIT-01"
    assert grade_log.details["grade"] == "B"
    assert grade_log.username == "audit_grader_01"


def test_admin_query_audit_logs_with_filtering(client: TestClient, db_session: Session):
    repo = UserRepository(db_session)
    admin = repo.create_user("audit_admin", "admin_audit@test.com", "Password2026!", "ADMIN")

    # Generate test audit entries
    audit = AuditService(db_session)
    audit.log_event(
        action="TEST_ACTION_ALPHA",
        resource_type="system",
        username="audit_admin",
        details={"info": "alpha"}
    )
    audit.log_event(
        action="TEST_ACTION_BETA",
        resource_type="system",
        username="audit_admin",
        details={"info": "beta"}
    )

    admin_headers = make_auth_header(admin)

    # Query without filter
    res_all = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert res_all.status_code == 200
    assert res_all.json()["total"] >= 2

    # Query with action filter
    res_filtered = client.get("/api/v1/admin/audit-logs?action=TEST_ACTION_ALPHA", headers=admin_headers)
    assert res_filtered.status_code == 200
    items = res_filtered.json()["items"]
    assert len(items) == 1
    assert items[0]["action"] == "TEST_ACTION_ALPHA"

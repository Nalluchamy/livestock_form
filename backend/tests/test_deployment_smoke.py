import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.settings import settings
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.core.security import create_access_token


@pytest.fixture
def smoke_admin(db_session: Session) -> User:
    repo = UserRepository(db_session)
    admin = repo.get_by_username("smoke_admin")
    if not admin:
        admin = repo.create_user("smoke_admin", "smoke@admin.internal", "AdminPass2026!", "ADMIN", is_verified=True)
    return admin


def test_health_probe_connectivity_and_storage(client: TestClient):
    """
    Validates deployment readiness:
    - Backend responds with HTTP 200
    - Database is connected with latency under 100ms
    - Storage volume is writable
    - Status is 'healthy'
    """
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    data = res.json()["data"]

    assert data["status"] == "healthy"
    assert data["database"]["connected"] is True
    assert data["database"]["latency_ms"] < 100.0
    assert data["storage"]["writable"] is True
    assert data["storage"]["free_space_mb"] > 0
    assert "version" in data
    assert "uptime_seconds" in data


def test_detailed_health_observability(client: TestClient, db_session: Session):
    """
    Validates operational monitoring endpoint /api/v1/health/detailed:
    - Returns audit security counters (auth failures, token reuse alerts)
    - Returns backup status
    - Returns max upload payload limits
    """
    res = client.get("/api/v1/health/detailed")
    assert res.status_code == 200
    data = res.json()["data"]

    assert "operational_monitoring" in data
    ops = data["operational_monitoring"]
    assert "authentication_failures_count" in ops
    assert "token_reuse_security_alerts" in ops
    assert "authorization_access_denials" in ops
    assert "backup_verification" in ops
    assert ops["max_upload_size_mb"] == 15


def test_private_image_serving_security_headers(client: TestClient, smoke_admin: User, tmp_path, monkeypatch):
    """
    Validates that authenticated private file serving returns strict security headers:
    - X-Content-Type-Options: nosniff
    - Cache-Control: private
    """
    import os
    test_proc_dir = str(tmp_path / "proc_smoke" / "images")
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROCESSED_IMAGES_DIR", test_proc_dir)
    os.makedirs(test_proc_dir, exist_ok=True)

    filename = "smoke_target.jpg"
    target_file = os.path.join(test_proc_dir, filename)
    with open(target_file, "wb") as f:
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9")

    token = create_access_token({"sub": str(smoke_admin.id), "username": smoke_admin.username, "role": smoke_admin.role})
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve image and verify security headers
    img_res = client.get(f"/api/v1/dataset/images/{filename}", headers=headers)
    assert img_res.status_code == 200
    assert img_res.headers.get("x-content-type-options") == "nosniff"
    assert "private" in img_res.headers.get("cache-control", "").lower()


def test_upload_body_size_limit_enforced(client: TestClient, smoke_admin: User):
    """
    Validates that upload endpoints reject payloads exceeding 15MB limit.
    """
    token = create_access_token({"sub": str(smoke_admin.id), "username": smoke_admin.username, "role": smoke_admin.role})
    headers = {"Authorization": f"Bearer {token}"}

    oversized = b"X" * (16 * 1024 * 1024)  # 16MB
    res = client.post(
        "/api/v1/dataset/upload",
        files={"file": ("too_large.jpg", oversized, "image/jpeg")},
        headers=headers
    )
    assert res.status_code == 413
    assert "exceeds maximum allowed size" in res.json()["detail"].lower()


def test_traversal_and_null_byte_attacks_blocked(client: TestClient, smoke_admin: User):
    """
    Validates that path traversal, absolute path, and null-byte injection attempts
    are blocked with 400 Bad Request or 403 Forbidden.
    """
    token = create_access_token({"sub": str(smoke_admin.id), "username": smoke_admin.username, "role": smoke_admin.role})
    headers = {"Authorization": f"Bearer {token}"}

    attacks = [
        "../etc/passwd",
        "..%2F..%2Fsecret.txt",
        "sample%00.jpg",
        "/etc/shadow",
        "nested/../../passwords.db"
    ]
    for attack in attacks:
        res = client.get(f"/api/v1/dataset/images/{attack}", headers=headers)
        assert res.status_code in (400, 403, 404)

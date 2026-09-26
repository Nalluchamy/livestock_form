"""
Unit and Integration Tests for System-Wide Error Handling, Boundaries, and Sanitization.

Verifies:
- API exceptions return clean, structured JSON without exposing internal stack traces
- Database/SQLAlchemy failures return generic sanitized 500 responses without leaking schemas or credentials
- Request validation errors format cleanly (422) with actionable error locations
- Authentication & RBAC boundaries reject unauthorized and unauthenticated requests cleanly (401/403)
- Corrupted, invalid, or unsupported image uploads fail gracefully with 400 Bad Request
- Cryptographic and perceptual duplicate detections return 409 Conflict
- Optical quality gate failures trigger explainable warnings/rejections rather than unhandled faults
- Experimental trial runners defend against division-by-zero when sample counts are insufficient
"""

import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from unittest.mock import patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from backend.main import app
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.core.security import create_access_token
from backend.core.settings import settings


@pytest.fixture
def error_users(db_session: Session):
    repo = UserRepository(db_session)
    farmer = repo.create_user("err_farmer", "err_farmer@test.com", "Password2026!", "FARMER")
    grader = repo.create_user("err_grader", "err_grader@test.com", "Password2026!", "EXPERT_GRADER")
    senior = repo.create_user("err_senior", "err_senior@test.com", "Password2026!", "SENIOR_REVIEWER")
    admin = repo.create_user("err_admin", "err_admin@test.com", "Password2026!", "ADMIN")
    return {
        "farmer": farmer,
        "grader": grader,
        "senior": senior,
        "admin": admin
    }


def auth_header_for(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


def test_api_exception_returns_clean_json(client: TestClient, error_users):
    """Verify custom APIException returns structured JSON without trace leaks."""
    headers = auth_header_for(error_users["senior"])
    response = client.get("/api/v1/reviews/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404
    data = response.json()
    assert data.get("message") == "Review not found"
    assert "Traceback (most recent call last)" not in response.text


def test_validation_exception_structure(client: TestClient):
    """Verify Pydantic 422 validation error provides clear field paths."""
    response = client.post("/api/v1/auth/login", json={"invalid_field": "data"})
    assert response.status_code == 422
    data = response.json()
    assert data.get("message") == "Validation Error"
    assert "data" in data
    # Ensure no internal path disclosure
    assert "backend/api" not in response.text


def test_sqlalchemy_exception_sanitization():
    """Verify database exceptions return a sanitized 500 without leaking SQL or credentials."""
    no_raise_client = TestClient(app, raise_server_exceptions=False)
    with patch("backend.services.produce_grading_service.ProduceGradingService.grade_sample") as mock_grade:
        mock_grade.side_effect = OperationalError("SELECT * FROM credentials_table", {}, Exception("DB timeout"))
        
        response = no_raise_client.post(
            "/api/v1/produce/grade",
            json={"surface_defect_pct": 2.0, "ripeness_stage": "RED"}
        )
        assert response.status_code == 500
        data = response.json()
        
        # Crucial security checks: SQL syntax and connection info must be scrubbed
        assert data.get("message") == "Internal Server Error: Database operation failed."
        assert "credentials_table" not in response.text
        assert "OperationalError" not in response.text
        assert "SELECT *" not in response.text


def test_general_exception_sanitization():
    """Verify unexpected general exceptions return generic 500 without leaking stack traces."""
    no_raise_client = TestClient(app, raise_server_exceptions=False)
    with patch("backend.services.produce_grading_service.ProduceGradingService.grade_sample") as mock_grade:
        mock_grade.side_effect = RuntimeError("Internal memory allocation failure with secret_api_key=sk-secret-999")
        
        response = no_raise_client.post(
            "/api/v1/produce/grade",
            json={"surface_defect_pct": 2.0, "ripeness_stage": "RED"}
        )
        assert response.status_code == 500
        data = response.json()
        assert data.get("message") == "Internal Server Error: An unexpected error occurred."
        assert "secret_api_key" not in response.text
        assert "sk-secret-999" not in response.text
        assert "RuntimeError" not in response.text
        assert "Traceback" not in response.text


def test_unauthenticated_request_rejection(client: TestClient):
    """Verify endpoints requiring authentication reject unauthenticated requests cleanly."""
    settings.DEMO_MODE = False
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "credentials" in data["detail"].lower() or "not authenticated" in data["detail"].lower()


def test_unauthorized_role_rejection(client: TestClient, error_users):
    """Verify role-based permission boundaries reject users with insufficient privileges."""
    farmer_headers = auth_header_for(error_users["farmer"])
    response = client.get("/api/v1/admin/users", headers=farmer_headers)
    assert response.status_code == 403
    data = response.json()
    assert "not authorized" in data.get("detail", "").lower() or "forbidden" in data.get("detail", "").lower()


def test_corrupted_image_upload_handling(client: TestClient, error_users, tmp_path, monkeypatch):
    """Verify corrupt or unreadable image files are cleanly rejected."""
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROVENANCE_FILE", str(tmp_path / "prov.json"))
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROCESSED_IMAGES_DIR", str(tmp_path / "proc"))
    monkeypatch.setattr("backend.api.v1.dataset_upload.RAW_IMAGES_DIR", str(tmp_path / "raw"))

    corrupted_bytes = b"NOT_A_VALID_IMAGE_STREAM_CORRUPTED"
    headers = auth_header_for(error_users["grader"])
    
    files = {"file": ("corrupt.jpg", corrupted_bytes, "image/jpeg")}
    response = client.post("/api/v1/dataset/upload", files=files, headers=headers)
    assert response.status_code in {400, 422}
    data_detail = response.json().get("detail", "").lower()
    assert any(w in data_detail for w in ["unsupported", "invalid", "corrupted", "cannot identify"])


def test_unsupported_file_extension_rejection(client: TestClient, error_users, tmp_path, monkeypatch):
    """Verify non-image formats (.exe, .sh, .txt) are rejected before parsing."""
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROVENANCE_FILE", str(tmp_path / "prov.json"))
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROCESSED_IMAGES_DIR", str(tmp_path / "proc"))
    monkeypatch.setattr("backend.api.v1.dataset_upload.RAW_IMAGES_DIR", str(tmp_path / "raw"))

    text_content = b"Echo 'malicious script execution attempt';"
    headers = auth_header_for(error_users["grader"])
    
    files = {"file": ("script.sh", text_content, "application/x-sh")}
    response = client.post("/api/v1/dataset/upload", files=files, headers=headers)
    assert response.status_code in {400, 422}
    data_detail = response.json().get("detail", "").lower()
    assert any(w in data_detail for w in ["unsupported", "invalid", "corrupted", "cannot identify"])


def test_duplicate_image_conflict_rejection(client: TestClient, error_users, tmp_path, monkeypatch):
    """Verify uploading the exact same image twice returns a 409 Conflict with hash identification."""
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROVENANCE_FILE", str(tmp_path / "prov.json"))
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROCESSED_IMAGES_DIR", str(tmp_path / "proc"))
    monkeypatch.setattr("backend.api.v1.dataset_upload.RAW_IMAGES_DIR", str(tmp_path / "raw"))

    img = Image.new("RGB", (100, 100), color=(200, 50, 50))
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG")
    valid_bytes = buffer.getvalue()
    
    headers = auth_header_for(error_users["grader"])
    
    # First upload succeeds
    files1 = {"file": ("sample_test_err_1.jpg", valid_bytes, "image/jpeg")}
    r1 = client.post("/api/v1/dataset/upload", files=files1, headers=headers)
    assert r1.status_code in {200, 201}
    
    # Second upload with identical bytes triggers duplicate rejection
    files2 = {"file": ("sample_test_err_1_dup.jpg", valid_bytes, "image/jpeg")}
    r2 = client.post("/api/v1/dataset/upload", files=files2, headers=headers)
    assert r2.status_code == 409
    data = r2.json()
    assert "duplicate" in data.get("detail", "").lower() or "collision" in data.get("detail", "").lower()


def test_optical_quality_gate_low_illumination(client: TestClient):
    """Verify optical quality gate handles poor lighting without crashing."""
    payload = {
        "surface_defect_pct": 2.0,
        "ripeness_stage": "RED",
        "illumination_mean": 25.0,  # Below 40.0 lux threshold
        "laplacian_var": 50.0       # Below 100 focus threshold
    }
    response = client.post("/api/v1/produce/grade", json=payload)
    assert response.status_code == 200
    data = response.json()
    res_data = data.get("data", {})
    # Optical gate failure should mark image_quality_passed as False and provisional_grade as REJECTED_IMAGE
    assert res_data.get("image_quality_passed") is False
    assert res_data.get("provisional_grade") == "REJECTED_IMAGE"
    assert res_data.get("confidence") == 0.0


def test_controlled_experiment_insufficient_samples_guard(client: TestClient, error_users):
    """Verify controlled experiment runner refuses execution when consensus samples < 10."""
    headers = auth_header_for(error_users["senior"])
    
    response = client.post("/api/v1/produce/real/experiment", headers=headers)
    assert response.status_code == 200
    data = response.json()
    
    # Result payload must indicate PENDING_REAL_DATA rather than crashing with ZeroDivisionError
    res_data = data.get("data", {})
    assert res_data.get("status") == "PENDING_REAL_DATA"
    assert res_data.get("eligible_samples", 0) < 10
    assert "division by zero" not in response.text.lower()

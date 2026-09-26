import io
import os
import zipfile
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.settings import settings
from backend.repositories.user_repository import UserRepository
from backend.core.security import create_access_token


def make_auth_header(user) -> dict:
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_user(db_session: Session):
    repo = UserRepository(db_session)
    return repo.create_user("sec_user", "sec@test.com", "SecurePass2026!", "EXPERT_GRADER")


def create_sample_image_bytes(color=(100, 150, 200), size=(200, 200)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_path_traversal_dot_dot_rejected(client: TestClient, auth_user):
    headers = make_auth_header(auth_user)
    # Path traversal patterns
    patterns = [
        "../../etc/passwd",
        "..%2F..%2Fetc%2Fpasswd",
        "..\\..\\windows\\win.ini",
        "nested/../../../file.jpg",
        "image.jpg%00.png"
    ]
    for p in patterns:
        res = client.get(f"/api/v1/dataset/images/{p}", headers=headers)
        assert res.status_code in (400, 403, 404), f"Failed to reject traversal pattern: {p}"


def test_authenticated_image_serving_with_security_headers(client: TestClient, auth_user, tmp_path, monkeypatch):
    test_proc_dir = str(tmp_path / "processed" / "images")
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROCESSED_IMAGES_DIR", test_proc_dir)
    os.makedirs(test_proc_dir, exist_ok=True)

    img_bytes = create_sample_image_bytes()
    filename = "valid_sample_01.jpg"
    with open(os.path.join(test_proc_dir, filename), "wb") as f:
        f.write(img_bytes)

    headers = make_auth_header(auth_user)
    res = client.get(f"/api/v1/dataset/images/{filename}", headers=headers)
    assert res.status_code == 200
    assert res.headers.get("x-content-type-options") == "nosniff"
    assert "private" in res.headers.get("cache-control", "").lower()
    assert len(res.content) == len(img_bytes)


def test_unauthenticated_image_serving_rejected_when_not_demo(client: TestClient):
    settings.DEMO_MODE = False
    res = client.get("/api/v1/dataset/images/sample.jpg")
    assert res.status_code == 401


def test_zip_slip_batch_upload_defense(client: TestClient, auth_user, tmp_path, monkeypatch):
    test_proc_dir = str(tmp_path / "processed" / "images")
    test_prov_file = str(tmp_path / "provenance.json")
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROCESSED_IMAGES_DIR", test_proc_dir)
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROVENANCE_FILE", test_prov_file)
    os.makedirs(test_proc_dir, exist_ok=True)

    # Construct malicious zip with Zip-Slip path traversal entry
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        # Malicious traversal entry
        img1 = create_sample_image_bytes(color=(10, 20, 30))
        z.writestr("../../evil_escape.jpg", img1)
        z.writestr("..\\..\\windows_escape.jpg", img1)
        z.writestr("/root/absolute_escape.jpg", img1)
        # Legitimate entry
        img2 = create_sample_image_bytes(color=(40, 50, 60))
        z.writestr("legit_cow.jpg", img2)

    zip_bytes = zip_buf.getvalue()
    files = {"zip_file": ("slip_test.zip", zip_bytes, "application/zip")}
    headers = make_auth_header(auth_user)

    res = client.post("/api/v1/dataset/batch-import", files=files, headers=headers)
    assert res.status_code == 200

    # Ensure no files were extracted outside the processed images directory
    parent_dir = str(tmp_path)
    assert not os.path.exists(os.path.join(parent_dir, "evil_escape.jpg"))
    assert not os.path.exists(os.path.join(parent_dir, "windows_escape.jpg"))


def test_max_upload_size_limit_exceeded(client: TestClient, auth_user):
    headers = make_auth_header(auth_user)
    # Exceed settings.MAX_UPLOAD_SIZE_BYTES (15MB)
    oversized_bytes = b"X" * (settings.MAX_UPLOAD_SIZE_BYTES + 1024)
    files = {"file": ("huge_cow.jpg", oversized_bytes, "image/jpeg")}

    res = client.post("/api/v1/dataset/upload", files=files, headers=headers)
    assert res.status_code == 413
    assert "exceeds maximum allowed size" in res.json()["detail"].lower()

import io
import zipfile
import pytest
from PIL import Image
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def isolate_provenance_and_storage(tmp_path, monkeypatch):
    test_prov_file = str(tmp_path / "provenance_records.json")
    test_proc_dir = str(tmp_path / "processed" / "images")
    test_raw_dir = str(tmp_path / "raw" / "images")
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROVENANCE_FILE", test_prov_file)
    monkeypatch.setattr("backend.api.v1.dataset_upload.PROCESSED_IMAGES_DIR", test_proc_dir)
    monkeypatch.setattr("backend.api.v1.dataset_upload.RAW_IMAGES_DIR", test_raw_dir)


def create_test_image_bytes(color=(120, 180, 80), size=(300, 300), pattern_seed: int = 0) -> bytes:
    img = Image.new("RGB", size, color=color)
    if pattern_seed == 1:
        for x in range(size[0] // 2):
            for y in range(size[1]):
                img.putpixel((x, y), (10, 10, 10))
    elif pattern_seed == 2:
        for x in range(size[0]):
            for y in range(size[1] // 2):
                img.putpixel((x, y), (250, 250, 250))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_upload_single_image_success(client: TestClient):
    img_bytes = create_test_image_bytes(color=(150, 100, 50))
    files = {"file": ("cattle_flank_1.jpg", img_bytes, "image/jpeg")}
    data = {
        "sample_id": "test_cattle_01",
        "source_type": "field_pilot",
        "contributor_id": "EXP-VET-01",
        "species": "cattle",
        "consent_obtained": "true"
    }

    res = client.post("/api/v1/dataset/upload", files=files, data=data)
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["sample_id"] == "test_cattle_01"
    assert "sha256" in res_data
    assert "phash" in res_data
    assert res_data["consent_obtained"] is True


def test_upload_duplicate_image_rejected(client: TestClient):
    img_bytes = create_test_image_bytes(color=(210, 140, 70))
    files = {"file": ("cattle_orig.jpg", img_bytes, "image/jpeg")}
    data = {"sample_id": "test_cattle_dup_orig"}

    res1 = client.post("/api/v1/dataset/upload", files=files, data=data)
    assert res1.status_code == 200

    # Attempt to upload identical image bytes
    files_dup = {"file": ("cattle_duplicate.jpg", img_bytes, "image/jpeg")}
    data_dup = {"sample_id": "test_cattle_dup_attempt"}
    res2 = client.post("/api/v1/dataset/upload", files=files_dup, data=data_dup)
    assert res2.status_code == 409
    assert "Duplicate image rejected" in res2.json()["detail"]


def test_upload_invalid_payload_rejected(client: TestClient):
    # Empty payload
    files = {"file": ("empty.jpg", b"", "image/jpeg")}
    res = client.post("/api/v1/dataset/upload", files=files)
    assert res.status_code == 400

    # Corrupt non-image payload
    files_corrupt = {"file": ("corrupt.jpg", b"NOT_AN_IMAGE_DATA_BYTES", "image/jpeg")}
    res_corrupt = client.post("/api/v1/dataset/upload", files=files_corrupt)
    assert res_corrupt.status_code == 400


def test_batch_import_zip_archive(client: TestClient):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        img1 = create_test_image_bytes(color=(50, 70, 90), pattern_seed=1)
        img2 = create_test_image_bytes(color=(80, 110, 140), pattern_seed=2)
        zf.writestr("cow_lotA_01.jpg", img1)
        zf.writestr("cow_lotA_02.jpg", img2)

    zip_bytes = zip_buffer.getvalue()
    files = {"zip_file": ("batch_cows.zip", zip_bytes, "application/zip")}
    data = {
        "source_type": "ranch_batch",
        "contributor_id": "RANCH-01",
        "species": "cattle",
        "consent_obtained": "true"
    }

    res = client.post("/api/v1/dataset/batch-import", files=files, data=data)
    assert res.status_code == 200
    res_data = res.json()["data"]
    assert res_data["total_processed"] >= 2
    assert res_data["errors"] == 0


def test_get_provenance_records(client: TestClient):
    # Ensure at least one record is uploaded first
    img_bytes = create_test_image_bytes(color=(30, 60, 90))
    files = {"file": ("cattle_prov.jpg", img_bytes, "image/jpeg")}
    data = {"sample_id": "test_cattle_prov_01", "consent_obtained": "true"}
    client.post("/api/v1/dataset/upload", files=files, data=data)

    res = client.get("/api/v1/dataset/provenance")
    assert res.status_code == 200
    records = res.json()["data"]
    assert isinstance(records, list)
    assert len(records) >= 1
    rec = records[0]
    assert "sample_id" in rec
    assert "source_type" in rec
    assert "consent_obtained" in rec
    assert "sha256" in rec

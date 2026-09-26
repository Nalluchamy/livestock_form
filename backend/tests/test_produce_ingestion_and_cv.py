"""
Tests for Produce Image Ingestion, Privacy Sanitization, and Feature Extraction.
Verifies format checks, EXIF scrubbing, deduplication, computer-vision feature extraction,
and transparent dataset status reporting.
"""
import io
import pytest
from PIL import Image, ImageDraw
import numpy as np

from backend.evaluation import produce_ingestion as pr_ingest
from backend.grading import produce_constants as pc


def create_test_produce_image(
    color: tuple = (220, 40, 30),
    size: tuple = (200, 200),
    add_defect: bool = False
) -> bytes:
    """Creates an in-memory JPEG test image with a circular fruit body."""
    img = Image.new("RGB", size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw circular tomato body
    draw.ellipse([20, 20, 180, 180], fill=color)
    if add_defect:
        # Add a dark blemish patch
        draw.ellipse([80, 80, 110, 110], fill=(40, 20, 10))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_validate_produce_image():
    valid_bytes = create_test_produce_image()
    valid, msg = pr_ingest.validate_produce_image(valid_bytes, "test.jpg")
    assert valid is True

    # Empty payload
    valid, msg = pr_ingest.validate_produce_image(b"", "empty.jpg")
    assert valid is False

    # Corrupt payload
    valid, msg = pr_ingest.validate_produce_image(b"not_an_image", "bad.jpg")
    assert valid is False


def test_compute_hashes_and_duplicates():
    img_bytes = create_test_produce_image()
    sha = pr_ingest.compute_image_hash(img_bytes)
    assert len(sha) == 64

    phash = pr_ingest.compute_perceptual_hash(img_bytes)
    assert len(phash) > 0

    # Exact duplicate test
    existing_sha = {sha}
    res = pr_ingest.process_produce_image(img_bytes, "dup.jpg", existing_sha256_set=existing_sha)
    assert res["success"] is False
    assert res.get("is_duplicate") is True


def test_strip_exif_and_normalize():
    img_bytes = create_test_produce_image()
    clean_bytes = pr_ingest.strip_exif_metadata(img_bytes)
    assert len(clean_bytes) > 0

    norm_bytes = pr_ingest.normalize_produce_image(clean_bytes, target_size=(256, 256))
    with Image.open(io.BytesIO(norm_bytes)) as norm_img:
        assert norm_img.size == (256, 256)
        assert norm_img.mode == "RGB"


def test_extract_produce_features():
    # Clean red tomato image
    red_img = create_test_produce_image(color=(230, 45, 30), add_defect=False)
    features = pr_ingest.extract_produce_features(red_img)

    assert features["ripeness_stage"] in {pc.RIPENESS_RED, pc.RIPENESS_LIGHT_RED}
    assert features["surface_defect_pct"] < 5.0
    assert features["shape_circularity"] >= 0.70
    assert features["bruising_severity"] in {pc.BRUISE_NONE, pc.BRUISE_MINOR}

    # Defective tomato image
    defective_img = create_test_produce_image(color=(220, 50, 30), add_defect=True)
    def_features = pr_ingest.extract_produce_features(defective_img)
    assert def_features["surface_defect_pct"] > 3.0


def test_get_produce_dataset_status_empty(tmp_path):
    # Isolated empty dataset root
    status = pr_ingest.get_produce_dataset_status(str(tmp_path))
    assert status["status"] == "PENDING_REAL_IMAGES"
    assert status["processed_samples_count"] == 0
    assert "PENDING" in status["status"]

import io
from PIL import Image, ImageOps
import pytest

from backend.evaluation.ingestion import (
    validate_image_format,
    compute_image_hash,
    compute_perceptual_hash,
    detect_duplicate_images,
    strip_exif_metadata,
    normalize_image,
    flag_identifiable_content,
    process_image_for_ingestion
)


def create_test_image(format="JPEG", size=(300, 300), color=(120, 100, 80)) -> bytes:
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=format)
    return buf.getvalue()


def test_validate_image_format_valid():
    jpeg_bytes = create_test_image("JPEG")
    is_valid, msg = validate_image_format(jpeg_bytes, "cow.jpg")
    assert is_valid is True
    assert "Valid" in msg


def test_validate_image_format_invalid_empty():
    is_valid, msg = validate_image_format(b"", "empty.jpg")
    assert is_valid is False
    assert "empty" in msg.lower()


def test_validate_image_format_invalid_extension():
    fake_bytes = b"not an image binary header"
    is_valid, msg = validate_image_format(fake_bytes, "fake.jpg")
    assert is_valid is False


def test_compute_hashes():
    img_bytes = create_test_image()
    sha = compute_image_hash(img_bytes)
    assert len(sha) == 64  # SHA-256 length
    
    phash = compute_perceptual_hash(img_bytes)
    assert len(phash) > 0


def test_detect_duplicate_images():
    img_bytes1 = create_test_image(color=(200, 100, 50))
    img_bytes2 = create_test_image(color=(200, 100, 50))
    
    sha1 = compute_image_hash(img_bytes1)
    existing_hashes = {sha1}
    
    is_dup, reason = detect_duplicate_images(img_bytes2, existing_hashes)
    assert is_dup is True
    assert "duplicate" in reason.lower()


def test_strip_exif_metadata():
    img = Image.new("RGB", (100, 100), color=(255, 0, 0))
    exif = img.getexif()
    exif[0x010e] = "Farm Worker ID 12345 GPS Tag"  # ImageDescription tag
    
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    raw_with_exif = buf.getvalue()
    
    # Check that raw image contains tag
    with Image.open(io.BytesIO(raw_with_exif)) as raw_img:
        assert raw_img.getexif().get(0x010e) == "Farm Worker ID 12345 GPS Tag"
        
    sanitized = strip_exif_metadata(raw_with_exif)
    with Image.open(io.BytesIO(sanitized)) as clean_img:
        clean_exif = clean_img.getexif()
        assert 0x010e not in clean_exif


def test_normalize_image():
    img_bytes = create_test_image(size=(400, 200))
    normalized = normalize_image(img_bytes, target_size=(256, 256))
    with Image.open(io.BytesIO(normalized)) as img:
        assert img.size == (256, 256)
        assert img.mode == "RGB"


def test_flag_identifiable_content():
    # Extreme vertical portrait: width 100, height 300 (ratio 3.0)
    portrait_bytes = create_test_image(size=(100, 300))
    flagged, reasons = flag_identifiable_content(portrait_bytes)
    assert flagged is True
    assert any("aspect ratio" in r.lower() for r in reasons)


def test_process_image_for_ingestion_pipeline():
    img_bytes = create_test_image()
    res = process_image_for_ingestion(img_bytes, "cattle_01.jpg", existing_sha256_hashes=set())
    assert res["success"] is True
    assert "sanitized_image_bytes" in res
    assert "sha256" in res

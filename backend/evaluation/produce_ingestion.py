"""
Produce Image Ingestion, Privacy Sanitization, and Feature Extraction Pipeline.
Provides:
- Format verification and EXIF/GPS scrubbing
- Cryptographic deduplication (SHA-256 and perceptual dHash)
- Computer vision feature extraction (color ripeness, defect area %, blur, illumination, circularity)
- Transparent provenance logging and manifest status (PENDING_REAL_IMAGES if < 10 samples)
"""
import io
import os
import json
import hashlib
from typing import Tuple, List, Optional, Dict, Any, Set
from PIL import Image, ImageOps, ImageFilter
import numpy as np

from backend.grading import produce_constants as pc


ALLOWED_PRODUCE_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
MAX_PRODUCE_IMAGE_SIZE = 15 * 1024 * 1024  # 15MB


def validate_produce_image(image_bytes: bytes, filename: str = "") -> Tuple[bool, str]:
    """Validates raw produce image bytes and format."""
    if not image_bytes:
        return False, "Produce image payload is empty."
    if len(image_bytes) > MAX_PRODUCE_IMAGE_SIZE:
        return False, f"Image exceeds maximum allowable size ({MAX_PRODUCE_IMAGE_SIZE} bytes)."

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            fmt = img.format.upper() if img.format else ""
            if fmt not in ALLOWED_PRODUCE_FORMATS and fmt != "MPO":
                return False, f"Unsupported format: '{fmt}'. Allowed: JPEG, PNG, WEBP."
            img.verify()
        return True, "Valid produce image format."
    except Exception as e:
        return False, f"Corrupted or invalid image data: {str(e)}"


def compute_image_hash(image_bytes: bytes) -> str:
    """Computes exact SHA-256 hash of bytes."""
    return hashlib.sha256(image_bytes).hexdigest()


def compute_perceptual_hash(image_bytes: bytes, hash_size: int = 8) -> str:
    """Computes Difference Hash (dHash) for visual duplicate detection."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        img_gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        arr = np.array(img_gray)
        # Compare adjacent columns
        diff = arr[:, 1:] > arr[:, :-1]
        
        # Flatten boolean array to hex string
        flat = diff.flatten()
        decimal_val = 0
        hex_str = []
        for index, val in enumerate(flat):
            if val:
                decimal_val += 2 ** (index % 4)
            if (index % 4) == 3:
                hex_str.append(hex(decimal_val)[2:])
                decimal_val = 0
        if len(flat) % 4 != 0:
            hex_str.append(hex(decimal_val)[2:])
        return "".join(hex_str)


def hamming_distance(h1: str, h2: str) -> int:
    """Calculates Hamming distance between two hex hashes."""
    if len(h1) != len(h2):
        return max(len(h1), len(h2)) * 4
    return bin(int(h1, 16) ^ int(h2, 16)).count("1")


def strip_exif_metadata(image_bytes: bytes) -> bytes:
    """Strips all EXIF, GPS, device, and camera metadata tags."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=95, optimize=True)
        return out.getvalue()


def normalize_produce_image(image_bytes: bytes, target_size: Tuple[int, int] = (512, 512)) -> bytes:
    """Normalizes image to standard square dimensions with clean white padding."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        bg = Image.new("RGB", target_size, (255, 255, 255))
        offset = ((target_size[0] - img.size[0]) // 2, (target_size[1] - img.size[1]) // 2)
        bg.paste(img, offset)
        out = io.BytesIO()
        bg.save(out, format="JPEG", quality=95, optimize=True)
        return out.getvalue()


def calculate_focus_laplacian(image_gray_arr: np.ndarray) -> float:
    """Computes focus sharpness via Laplacian 3x3 kernel variance."""
    if image_gray_arr.shape[0] < 3 or image_gray_arr.shape[1] < 3:
        return 0.0
    # Discrete Laplacian kernel
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=float)
    # Fast 2D convolution for kernel
    sub = image_gray_arr.astype(float)
    lap = (
        sub[1:-1, :-2] + sub[1:-1, 2:] + sub[:-2, 1:-1] + sub[2:, 1:-1] - 4.0 * sub[1:-1, 1:-1]
    )
    return float(np.var(lap))


def extract_produce_features(image_bytes: bytes) -> Dict[str, Any]:
    """
    Extracts measurable computer vision attributes from produce photograph:
    - Focus blur variance (Laplacian)
    - Mean illumination (lux proxy)
    - Surface defect area %
    - Ripeness stage (USDA 6-stage)
    - Color uniformity %
    - Circularity and aspect ratio
    - Surface occlusion %
    - Critical defect indications
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img_rgb = img.convert("RGB")
        w, h = img_rgb.size
        aspect_ratio = round(float(w) / float(h), 2)
        
        arr_rgb = np.array(img_rgb)
        arr_gray = np.array(img_rgb.convert("L"))

        # 1. Optical Quality Metrics
        laplacian_var = calculate_focus_laplacian(arr_gray)
        illumination_mean = float(np.mean(arr_gray))

        # 2. Fruit Segmentation Heuristic
        # Non-white background detection (assuming neutral or light background)
        r = arr_rgb[:, :, 0].astype(float)
        g = arr_rgb[:, :, 1].astype(float)
        b = arr_rgb[:, :, 2].astype(float)
        brightness = (r + g + b) / 3.0

        # Fruit mask: pixels that are not close to white (>245 in all channels) and not pure black
        fruit_mask = (brightness < 240) & (brightness > 20)
        fruit_pixel_count = int(np.sum(fruit_mask))
        total_pixels = w * h

        if fruit_pixel_count < 100:
            # Insufficient fruit segmentation
            return {
                "laplacian_var": round(laplacian_var, 1),
                "illumination_mean": round(illumination_mean, 1),
                "surface_occlusion_pct": 90.0,
                "surface_defect_pct": 0.0,
                "ripeness_stage": pc.RIPENESS_GREEN,
                "color_uniformity_pct": 50.0,
                "shape_circularity": 0.5,
                "aspect_ratio": aspect_ratio,
                "bruising_severity": pc.BRUISE_NONE,
                "critical_defects": [],
                "quality_passed": False,
                "notes": "Insufficient visible fruit area detected in frame."
            }

        # 3. Ripeness Chromaticity Estimation
        r_fruit = r[fruit_mask]
        g_fruit = g[fruit_mask]
        b_fruit = b[fruit_mask]
        total_rgb = r_fruit + g_fruit + b_fruit + 1e-6
        r_ratio = float(np.mean(r_fruit / total_rgb))
        g_ratio = float(np.mean(g_fruit / total_rgb))

        if r_ratio >= 0.52:
            ripeness_stage = pc.RIPENESS_RED
        elif r_ratio >= 0.46:
            ripeness_stage = pc.RIPENESS_LIGHT_RED
        elif r_ratio >= 0.40:
            ripeness_stage = pc.RIPENESS_PINK
        elif r_ratio >= 0.35 and g_ratio < 0.42:
            ripeness_stage = pc.RIPENESS_TURNING
        elif r_ratio >= 0.32:
            ripeness_stage = pc.RIPENESS_BREAKER
        else:
            ripeness_stage = pc.RIPENESS_GREEN

        # 4. Color Uniformity % (inverse of chromatic variance)
        r_var = float(np.var(r_fruit / total_rgb))
        color_uniformity_pct = round(max(40.0, min(99.0, 100.0 - (r_var * 2500.0))), 1)

        # 5. Surface Defect Area % Estimation
        # Dark spots, blemishes, or necrotic areas on the fruit body
        fruit_brightness = brightness[fruit_mask]
        mean_fb = np.mean(fruit_brightness)
        # Blemish pixels are notably darker than surrounding fruit body or have high local variance
        dark_blemish_mask = fruit_brightness < (mean_fb * 0.65)
        defect_pixels = int(np.sum(dark_blemish_mask))
        defect_pct = round(float(defect_pixels) / float(fruit_pixel_count) * 100.0, 1)

        # 6. Bruising Severity Estimation
        # Diffuse softening patch (pixels between 65% and 80% of mean brightness)
        bruise_pixels = int(np.sum((fruit_brightness >= (mean_fb * 0.65)) & (fruit_brightness < (mean_fb * 0.80))))
        bruise_ratio = bruise_pixels / float(fruit_pixel_count)
        if bruise_ratio < 0.03:
            bruising_severity = pc.BRUISE_NONE
        elif bruise_ratio < 0.10:
            bruising_severity = pc.BRUISE_MINOR
        elif bruise_ratio < 0.20:
            bruising_severity = pc.BRUISE_MODERATE
        else:
            bruising_severity = pc.BRUISE_SEVERE

        # 7. Circularity & Symmetry
        # Bounding box of segmented fruit
        rows = np.any(fruit_mask, axis=1)
        cols = np.any(fruit_mask, axis=0)
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]
        box_w = max(1, xmax - xmin)
        box_h = max(1, ymax - ymin)
        box_aspect = round(float(box_w) / float(box_h), 2)
        
        # Approximate circularity comparing fruit area to enclosing ellipse
        ellipse_area = np.pi * (box_w / 2.0) * (box_h / 2.0)
        circularity = round(min(1.0, max(0.4, float(fruit_pixel_count) / max(1.0, ellipse_area))), 2)

        # 8. Occlusion Estimation
        # Fraction of bounding box area that is void/interrupted
        box_area = box_w * box_h
        occlusion_pct = round(max(0.0, min(80.0, (1.0 - (float(fruit_pixel_count) / box_area)) * 100.0 * 0.4)), 1)

        # 9. Critical Defects Detection
        critical_defects: List[str] = []
        # Check for deep dark cluster in bottom quadrant (Blossom End Rot)
        bottom_third_y = ymin + int(box_h * 0.70)
        bottom_mask = fruit_mask[bottom_third_y:ymax, xmin:xmax]
        if bottom_mask.size > 50:
            b_bright = brightness[bottom_third_y:ymax, xmin:xmax][bottom_mask]
            if len(b_bright) > 0 and np.mean(b_bright) < (mean_fb * 0.45):
                critical_defects.append(pc.CRITICAL_BLOSSOM_END_ROT)

        quality_passed = bool(
            float(laplacian_var) >= pc.MIN_FOCUS_LAPLACIAN and
            pc.MIN_ILLUMINATION_LUX <= float(illumination_mean) <= pc.MAX_ILLUMINATION_LUX and
            float(occlusion_pct) <= pc.MAX_OCCLUSION_PCT
        )

        return {
            "laplacian_var": round(float(laplacian_var), 1),
            "illumination_mean": round(float(illumination_mean), 1),
            "surface_occlusion_pct": round(float(occlusion_pct), 1),
            "surface_defect_pct": round(float(defect_pct), 1),
            "ripeness_stage": str(ripeness_stage),
            "color_uniformity_pct": round(float(color_uniformity_pct), 1),
            "shape_circularity": round(float(circularity), 2),
            "aspect_ratio": round(float(box_aspect), 2),
            "bruising_severity": str(bruising_severity),
            "critical_defects": list(critical_defects),
            "quality_passed": quality_passed,
        }


def process_produce_image(
    raw_bytes: bytes,
    filename: str,
    existing_sha256_set: Optional[Set[str]] = None,
    existing_phash_map: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Ingests, sanitizes, and extracts features for a produce image."""
    existing_sha256_set = existing_sha256_set or set()
    existing_phash_map = existing_phash_map or {}

    valid, err = validate_produce_image(raw_bytes, filename)
    if not valid:
        return {"success": False, "error": err}

    sha256 = compute_image_hash(raw_bytes)
    if sha256 in existing_sha256_set:
        return {"success": False, "error": f"Exact duplicate produce image detected ({sha256[:12]}...)", "is_duplicate": True}

    phash = compute_perceptual_hash(raw_bytes)
    for sample_id, ex_phash in existing_phash_map.items():
        if hamming_distance(phash, ex_phash) <= 4:
            return {"success": False, "error": f"Perceptual duplicate detected of sample {sample_id}", "is_duplicate": True}

    sanitized = strip_exif_metadata(raw_bytes)
    normalized = normalize_produce_image(sanitized)
    features = extract_produce_features(normalized)

    return {
        "success": True,
        "sha256": sha256,
        "phash": phash,
        "sanitized_bytes": normalized,
        "features": features,
        "filename": filename
    }


def get_produce_dataset_status(dataset_root: str = "dataset/produce") -> Dict[str, Any]:
    """
    Returns the real-world dataset status.
    Strict non-fabrication: if count < 10, marks status as PENDING_REAL_IMAGES.
    """
    raw_dir = os.path.join(dataset_root, "raw")
    processed_dir = os.path.join(dataset_root, "processed")
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    raw_files = [f for f in os.listdir(raw_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    proc_files = [f for f in os.listdir(processed_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
    
    total_count = len(proc_files)
    status_label = "READY" if total_count >= 10 else "PENDING_REAL_IMAGES"

    return {
        "status": status_label,
        "processed_samples_count": total_count,
        "raw_samples_count": len(raw_files),
        "target_range": "60-100 genuine produce images",
        "transparency_note": (
            "No synthetic random noise is injected. Real produce images must be ethically photographed "
            "or ingested via the upload pipeline with provenance records."
        )
    }

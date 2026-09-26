"""
Dataset Ingestion & Privacy Sanitization Pipeline for ELHGS.
Provides:
- Format verification (JPEG, PNG, WebP)
- Duplicate detection (SHA-256 and perceptual dHash)
- Complete EXIF/GPS metadata stripping
- Image normalization (RGB, standard resolution)
- Heuristic flagging of potentially identifiable human content
"""
import io
import hashlib
from typing import Tuple, List, Optional, Dict, Any, Set
from PIL import Image, ImageOps


ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}
MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024  # 15MB


def validate_image_format(image_bytes: bytes, filename: str = "") -> Tuple[bool, str]:
    """
    Validates that the provided image is a valid, uncorrupted image in an allowed format.
    """
    if not image_bytes:
        return False, "Image payload is empty."

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        return False, f"Image exceeds maximum allowable size ({MAX_IMAGE_SIZE_BYTES} bytes)."

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img_format = img.format.upper() if img.format else ""
            if img_format not in ALLOWED_FORMATS and img_format != "MPO":
                return False, f"Unsupported image format: '{img_format}'. Allowed: JPEG, PNG, WEBP."
            # Verify image integrity
            img.verify()
        return True, "Valid image format."
    except Exception as e:
        return False, f"Corrupted or invalid image data: {str(e)}"


def compute_image_hash(image_bytes: bytes) -> str:
    """Computes exact SHA-256 hash of image bytes."""
    return hashlib.sha256(image_bytes).hexdigest()


def compute_perceptual_hash(image_bytes: bytes, hash_size: int = 8) -> str:
    """
    Computes a Difference Hash (dHash) for visual duplicate detection.
    Resizes image to (hash_size + 1, hash_size), converts to grayscale,
    and compares adjacent pixels.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img_gray = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = list(img_gray.getdata())
        
        diff = []
        for row in range(hash_size):
            row_start = row * (hash_size + 1)
            for col in range(hash_size):
                diff.append(pixels[row_start + col] > pixels[row_start + col + 1])
                
        # Convert boolean list to hexadecimal string
        decimal_val = 0
        hex_str = []
        for index, value in enumerate(diff):
            if value:
                decimal_val += 2 ** (index % 4)
            if (index % 4) == 3:
                hex_str.append(hex(decimal_val)[2:])
                decimal_val = 0
        if len(diff) % 4 != 0:
            hex_str.append(hex(decimal_val)[2:])
            
        return "".join(hex_str)


def hamming_distance(hash1: str, hash2: str) -> int:
    """Calculates Hamming distance between two hex perceptual hashes."""
    if len(hash1) != len(hash2):
        return max(len(hash1), len(hash2)) * 4
    val1 = int(hash1, 16)
    val2 = int(hash2, 16)
    return bin(val1 ^ val2).count("1")


def detect_duplicate_images(
    new_image_bytes: bytes, 
    existing_sha256_hashes: Set[str],
    existing_phash_map: Optional[Dict[str, str]] = None,
    distance_threshold: int = 5
) -> Tuple[bool, Optional[str]]:
    """
    Checks if an image is an exact or perceptual near-duplicate of previously ingested images.
    Returns (is_duplicate, reason_or_duplicate_id).
    """
    new_sha = compute_image_hash(new_image_bytes)
    if new_sha in existing_sha256_hashes:
        return True, f"Exact duplicate detected (SHA-256 match: {new_sha[:12]}...)"

    if existing_phash_map:
        new_phash = compute_perceptual_hash(new_image_bytes)
        for existing_id, ex_phash in existing_phash_map.items():
            dist = hamming_distance(new_phash, ex_phash)
            if dist <= distance_threshold:
                return True, f"Near-duplicate detected (Hamming distance {dist} to sample {existing_id})"

    return False, None


def strip_exif_metadata(image_bytes: bytes) -> bytes:
    """
    Strips all EXIF, GPS, device, and camera metadata tags.
    Re-encodes the pure raster data into sanitized JPEG format without metadata chunks.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        # Transpose according to EXIF orientation before stripping tags, so image stays upright
        img = ImageOps.exif_transpose(img)
        
        # Convert RGBA/P to RGB for clean standardized output
        if img.mode != "RGB":
            img = img.convert("RGB")

        # Save to buffer without passing existing EXIF info
        clean_buffer = io.BytesIO()
        img.save(clean_buffer, format="JPEG", quality=95, optimize=True)
        return clean_buffer.getvalue()


def normalize_image(image_bytes: bytes, target_size: Tuple[int, int] = (512, 512)) -> bytes:
    """
    Normalizes image:
    1. Strips metadata.
    2. Resizes and pads to standard square dimensions maintaining aspect ratio.
    3. Guarantees 3-channel RGB.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = ImageOps.exif_transpose(img)
        if img.mode != "RGB":
            img = img.convert("RGB")
            
        # Fit inside target_size keeping aspect ratio
        img.thumbnail(target_size, Image.Resampling.LANCZOS)
        
        # Create square background and paste thumbnail in center
        background = Image.new("RGB", target_size, (255, 255, 255))
        offset = ((target_size[0] - img.size[0]) // 2, (target_size[1] - img.size[1]) // 2)
        background.paste(img, offset)
        
        output_buffer = io.BytesIO()
        background.save(output_buffer, format="JPEG", quality=95, optimize=True)
        return output_buffer.getvalue()


def flag_identifiable_content(image_bytes: bytes) -> Tuple[bool, List[str]]:
    """
    Heuristically screens image for potential human presence or PII requiring manual review:
    1. Extreme vertical aspect ratio typical of human portraits.
    2. Skin-tone pixel density clustering in the upper quadrant.
    Returns (flagged_for_review, list_of_reasons).
    """
    flags = []
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            width, height = img.size
            
            # Aspect ratio check: Portrait ratios > 1.8 often denote vertical person selfies
            if height / width > 1.8:
                flags.append("Extreme portrait aspect ratio detected; review for human subject.")

            # Small image resolution check
            if width < 200 or height < 200:
                flags.append("Image resolution is below 200x200 minimum threshold.")

            # Heuristic skin-tone check in top quadrant
            img_rgb = img.convert("RGB")
            top_quadrant = img_rgb.crop((0, 0, width, height // 3)).resize((50, 50))
            pixels = list(top_quadrant.getdata())
            
            skin_like_pixels = 0
            for r, g, b in pixels:
                # Standard YCbCr / RGB skin tone heuristic: R > G > B and (R - G) > 15
                if r > 95 and g > 40 and b > 20 and (max(r, g, b) - min(r, g, b) > 15) and abs(r - g) > 15 and r > g and r > b:
                    skin_like_pixels += 1
                    
            if skin_like_pixels > (len(pixels) * 0.45):
                flags.append("High skin-tone density in upper quadrant; manual review recommended for human presence.")

    except Exception as e:
        flags.append(f"Inspection error during heuristic check: {str(e)}")

    return len(flags) > 0, flags


def process_image_for_ingestion(
    raw_image_bytes: bytes,
    filename: str,
    existing_sha256_hashes: Set[str],
    existing_phash_map: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Full orchestrator for a single image ingestion:
    - Validates format
    - Checks duplicates
    - Strips EXIF
    - Normalizes image
    - Evaluates human PII flags
    """
    is_valid, msg = validate_image_format(raw_image_bytes, filename)
    if not is_valid:
        return {"success": False, "error": msg}

    is_duplicate, dup_reason = detect_duplicate_images(
        raw_image_bytes, 
        existing_sha256_hashes=existing_sha256_hashes,
        existing_phash_map=existing_phash_map
    )
    if is_duplicate:
        return {"success": False, "error": dup_reason, "is_duplicate": True}

    sanitized_bytes = strip_exif_metadata(raw_image_bytes)
    normalized_bytes = normalize_image(sanitized_bytes)
    
    flagged, reasons = flag_identifiable_content(normalized_bytes)
    sha256_hash = compute_image_hash(normalized_bytes)
    phash = compute_perceptual_hash(normalized_bytes)

    return {
        "success": True,
        "sanitized_image_bytes": normalized_bytes,
        "sha256": sha256_hash,
        "phash": phash,
        "flagged_for_manual_review": flagged,
        "flag_reasons": reasons,
        "original_filename": filename
    }

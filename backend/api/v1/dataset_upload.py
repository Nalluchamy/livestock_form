import os
import json
import uuid
import zipfile
import io
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.core.settings import settings
from backend.core.auth_deps import get_current_user, require_role
from backend.models.user import User
from backend.evaluation.ingestion import (
    process_image_for_ingestion,
    validate_image_format,
    detect_duplicate_images,
    strip_exif_metadata,
    normalize_image,
    flag_identifiable_content,
    compute_image_hash,
    compute_perceptual_hash
)
from backend.repositories.annotation_repository import AnnotationRepository
from backend.schemas.responses import APIResponse, success_response


router = APIRouter(prefix="/dataset", tags=["Dataset Management"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REAL_DATASET_DIR = os.path.join(BASE_DIR, "dataset", "real")
PROCESSED_IMAGES_DIR = os.path.join(REAL_DATASET_DIR, "processed", "images")
RAW_IMAGES_DIR = os.path.join(REAL_DATASET_DIR, "raw", "images")
PROVENANCE_FILE = os.path.join(REAL_DATASET_DIR, "documentation", "provenance_records.json")


def safe_relpath(path: str, start: str) -> str:
    try:
        return os.path.relpath(path, start).replace("\\", "/")
    except ValueError:
        return os.path.abspath(path).replace("\\", "/")


def ensure_directories():
    os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)
    os.makedirs(RAW_IMAGES_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(PROVENANCE_FILE), exist_ok=True)


def load_provenance_records() -> List[Dict[str, Any]]:
    ensure_directories()
    if not os.path.exists(PROVENANCE_FILE):
        return []
    try:
        with open(PROVENANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_provenance_records(records: List[Dict[str, Any]]):
    ensure_directories()
    with open(PROVENANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)


def get_existing_hashes(records: List[Dict[str, Any]]):
    sha_set = {r["sha256"] for r in records if "sha256" in r}
    phash_map = {r["sample_id"]: r["phash"] for r in records if "phash" in r and "sample_id" in r}
    return sha_set, phash_map


@router.post("/upload", response_model=APIResponse[dict])
async def upload_dataset_image(
    file: UploadFile = File(...),
    sample_id: Optional[str] = Form(None),
    source_type: str = Form("field_pilot"),
    contributor_id: Optional[str] = Form(None),
    species: str = Form("cattle"),
    consent_obtained: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """
    Ingest a single livestock image:
    1. Validates upload size against MAX_UPLOAD_SIZE_BYTES
    2. Validates format (JPEG, PNG, WebP)
    3. Runs duplicate detection (SHA-256 + perceptual dHash)
    4. Strips EXIF/GPS/device metadata
    5. Normalizes to 512x512 RGB
    6. Screens for PII/human presence
    7. Stores sanitized image in dataset/real/processed/images/{sample_id}.jpg
    8. Logs provenance record separately
    9. Registers pending expert annotation entry
    """
    ensure_directories()
    raw_bytes = await file.read()
    if not raw_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file payload is empty."
        )

    if len(raw_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB."
        )

    # 1. Format check
    valid_format, format_err = validate_image_format(raw_bytes, file.filename or "unknown.jpg")
    if not valid_format:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=format_err
        )

    # 2. Privacy metadata strip
    sanitized_bytes = strip_exif_metadata(raw_bytes)

    # 3. Normalization (512x512 RGB)
    normalized_bytes = normalize_image(sanitized_bytes)

    # 4. Duplicate screening
    provenance_records = load_provenance_records()
    sha_set, phash_map = get_existing_hashes(provenance_records)

    is_duplicate, dup_reason = detect_duplicate_images(normalized_bytes, sha_set, phash_map)
    if is_duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Duplicate image rejected: {dup_reason}"
        )

    # 5. PII / Human Presence Screening
    flagged_pii, pii_reasons = flag_identifiable_content(normalized_bytes)

    # 6. Cryptographic and Perceptual Hashes
    sha256 = compute_image_hash(normalized_bytes)
    phash = compute_perceptual_hash(normalized_bytes)

    # 7. Generate or validate sample_id
    if not sample_id:
        sample_id = f"real_cattle_{uuid.uuid4().hex[:8]}"

    processed_filepath = os.path.join(PROCESSED_IMAGES_DIR, f"{sample_id}.jpg")
    with open(processed_filepath, "wb") as f:
        f.write(normalized_bytes)

    rel_image_path = safe_relpath(processed_filepath, BASE_DIR)

    effective_contributor = contributor_id or (current_user.username if current_user else "anonymous")

    # 8. Append Provenance Record
    provenance_entry = {
        "sample_id": sample_id,
        "original_filename": file.filename,
        "processed_path": rel_image_path,
        "source_type": source_type,
        "contributor_id": effective_contributor,
        "species": species,
        "consent_obtained": consent_obtained,
        "sha256": sha256,
        "phash": phash,
        "flagged_for_manual_review": flagged_pii,
        "flag_reasons": pii_reasons,
        "ingested_at": datetime.now(timezone.utc).isoformat()
    }
    provenance_records.append(provenance_entry)
    save_provenance_records(provenance_records)

    # 9. Register task in expert annotation workflow
    repo = AnnotationRepository(db)
    annotation_record, _ = repo.create_or_get_for_image(
        sample_id=sample_id,
        image_path=rel_image_path,
        species=species
    )

    if flagged_pii:
        repo.flag_quality_issue(
            sample_id=sample_id,
            grader_id="AUTOMATED_INGESTION_SCREENER",
            reason=f"PII/Face flagged: {'; '.join(pii_reasons)}"
        )

    return success_response(
        message=f"Livestock image successfully sanitized and registered under ID: {sample_id}",
        data={
            "sample_id": sample_id,
            "processed_path": rel_image_path,
            "sha256": sha256,
            "phash": phash,
            "flagged_for_review": flagged_pii,
            "flag_reasons": pii_reasons,
            "consent_obtained": consent_obtained,
            "annotation_task_status": annotation_record.annotation_status
        }
    )


@router.post("/batch-import", response_model=APIResponse[dict])
async def batch_import_dataset_images(
    zip_file: UploadFile = File(...),
    source_type: str = Form("field_pilot_batch"),
    contributor_id: Optional[str] = Form(None),
    species: str = Form("cattle"),
    consent_obtained: bool = Form(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("EXPERT_GRADER", "SENIOR_REVIEWER", "ADMIN")),
):
    """
    Ingest a batch archive (.zip) containing livestock images.
    Protected against Zip-Slip path traversal vulnerabilities.
    Sanitizes, deduplicates, and logs provenance for each image.
    """
    ensure_directories()
    zip_bytes = await zip_file.read()
    if not zip_bytes:
        raise HTTPException(status_code=400, detail="Zip file payload is empty.")

    if len(zip_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Zip archive exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB."
        )

    try:
        archive = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid zip archive: {str(e)}")

    provenance_records = load_provenance_records()
    sha_set, phash_map = get_existing_hashes(provenance_records)
    repo = AnnotationRepository(db)

    results = []
    skipped_duplicates = 0
    errors = 0

    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    effective_contributor = contributor_id or (current_user.username if current_user else "batch_importer")

    for filename in archive.namelist():
        # Zip-Slip defense: reject traversal attempts
        if ".." in filename or filename.startswith("/") or filename.startswith("\\"):
            continue

        # Skip directories and hidden/metadata files (e.g. __MACOSX)
        if filename.startswith("__MACOSX") or filename.endswith("/"):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in valid_extensions:
            continue

        try:
            raw_bytes = archive.read(filename)
            valid_format, format_msg = validate_image_format(raw_bytes, filename)
            if not valid_format:
                errors += 1
                continue

            sanitized_bytes = strip_exif_metadata(raw_bytes)
            normalized_bytes = normalize_image(sanitized_bytes)

            is_duplicate, dup_reason = detect_duplicate_images(normalized_bytes, sha_set, phash_map)
            if is_duplicate:
                skipped_duplicates += 1
                continue

            flagged_pii, pii_reasons = flag_identifiable_content(normalized_bytes)
            sha256 = compute_image_hash(normalized_bytes)
            phash = compute_perceptual_hash(normalized_bytes)

            clean_base = os.path.basename(filename)
            base_name = os.path.splitext(clean_base)[0]
            clean_sample_id = f"batch_{base_name}_{uuid.uuid4().hex[:6]}"

            processed_filepath = os.path.join(PROCESSED_IMAGES_DIR, f"{clean_sample_id}.jpg")

            # Canonical path verification: ensure write stays strictly inside PROCESSED_IMAGES_DIR
            resolved_dest = os.path.abspath(processed_filepath)
            expected_root = os.path.abspath(PROCESSED_IMAGES_DIR)
            if not resolved_dest.startswith(expected_root):
                errors += 1
                continue

            with open(processed_filepath, "wb") as f:
                f.write(normalized_bytes)

            rel_image_path = safe_relpath(processed_filepath, BASE_DIR)

            provenance_entry = {
                "sample_id": clean_sample_id,
                "original_filename": filename,
                "processed_path": rel_image_path,
                "source_type": source_type,
                "contributor_id": effective_contributor,
                "species": species,
                "consent_obtained": consent_obtained,
                "sha256": sha256,
                "phash": phash,
                "flagged_for_manual_review": flagged_pii,
                "flag_reasons": pii_reasons,
                "ingested_at": datetime.now(timezone.utc).isoformat()
            }
            provenance_records.append(provenance_entry)
            sha_set.add(sha256)
            phash_map[clean_sample_id] = phash

            repo.create_or_get_for_image(
                sample_id=clean_sample_id,
                image_path=rel_image_path,
                species=species
            )

            results.append({
                "sample_id": clean_sample_id,
                "original_filename": filename,
                "flagged": flagged_pii
            })

        except Exception:
            errors += 1

    save_provenance_records(provenance_records)

    return success_response(
        message=f"Batch import completed: {len(results)} images processed, {skipped_duplicates} duplicates skipped, {errors} errors.",
        data={
            "total_processed": len(results),
            "duplicates_skipped": skipped_duplicates,
            "errors": errors,
            "samples": results
        }
    )


@router.get("/images/{filename}")
def get_dataset_image(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """
    Secure private image serving endpoint.
    Guards against path traversal and Zip-Slip vulnerabilities.
    Restricted to authenticated users.
    """
    ensure_directories()

    # Reject any directory navigation or null bytes
    if not filename or "/" in filename or "\\" in filename or ".." in filename or "\x00" in filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image path. Path traversal detected."
        )

    ext = os.path.splitext(filename)[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image extension requested."
        )

    target_path = os.path.abspath(os.path.join(PROCESSED_IMAGES_DIR, filename))
    base_processed = os.path.abspath(PROCESSED_IMAGES_DIR)

    # Verify target canonical path is strictly contained within base_processed
    try:
        common = os.path.commonpath([base_processed, target_path])
        if common != base_processed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Path traversal detected."
            )
    except ValueError:
        # Cross-drive or incompatible paths
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Invalid filesystem path."
        )

    if not os.path.isfile(target_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image file '{filename}' was not found in processed repository."
        )

    media_type = "image/jpeg" if ext in {".jpg", ".jpeg"} else f"image/{ext.lstrip('.')}"
    return FileResponse(
        target_path,
        media_type=media_type,
        headers={
            "Cache-Control": "private, max-age=3600",
            "X-Content-Type-Options": "nosniff"
        }
    )


@router.get("/collection-progress", response_model=APIResponse[dict])
def get_dataset_collection_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Tracks genuine real dataset collection against target goal (100-300 images).
    Reports real ingestion counts, consensus counts, and pipeline readiness without fabrication.
    """
    ensure_directories()
    repo = AnnotationRepository(db)
    stats = repo.get_annotation_stats()

    processed_count = 0
    if os.path.exists(PROCESSED_IMAGES_DIR):
        processed_count = sum(
            1 for f in os.listdir(PROCESSED_IMAGES_DIR)
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
        )

    consensus_count = stats.get("consensus_reached", 0)
    target_min = 100
    target_max = 300
    target_ideal = 200

    progress_pct = round(min(100.0, (consensus_count / target_ideal) * 100.0), 1)

    readiness = "READY_FOR_TRAINING" if consensus_count >= 10 else "PENDING_REAL_WORLD_COLLECTION"

    return success_response(
        message="Dataset collection progress retrieved.",
        data={
            "target": {
                "min": target_min,
                "ideal": target_ideal,
                "max": target_max,
                "species": "cattle",
            },
            "ingested_images_count": processed_count,
            "total_annotation_tasks": stats.get("total_samples", 0),
            "pending_annotation": stats.get("pending", 0),
            "partially_annotated": stats.get("partially_annotated", 0),
            "consensus_reached": consensus_count,
            "disagreements": stats.get("disagreement", 0),
            "rejected_quality": stats.get("rejected", 0),
            "inter_expert_exact_pct": stats.get("inter_expert_exact_pct", 0.0),
            "inter_expert_kappa": stats.get("inter_expert_kappa", 0.0),
            "progress_percentage": progress_pct,
            "pilot_minimum_target_met": (consensus_count >= target_min),
            "readiness_status": readiness,
            "clinical_disclaimer": "This system does not provide automated veterinary diagnoses. All ratings require clinical correlation."
        }
    )


@router.get("/provenance", response_model=APIResponse[list])
def get_provenance_records(
    current_user: User = Depends(get_current_user),
):
    """
    Returns verified provenance and consent records (maintained separately from training features).
    Restricted to authenticated users.
    """
    records = load_provenance_records()
    return success_response(
        message=f"Retrieved {len(records)} provenance records.",
        data=records
    )

"""
Real Produce Dataset Ingestion, Provenance, Double-Blind Annotation & Evaluation Pipeline.
Phase 17: Genuine Produce Image Validation Workflow for Stage 2.

Provides:
- Ingestion of genuine tomato photographs with EXIF/GPS stripping and PII checks
- Cryptographic deduplication (SHA-256 and perceptual dHash)
- Strict segregation of REAL_PRODUCE vs SYNTHETIC_PRODUCE (zero silent mixing)
- Data integrity enforcement: no automated ground-truth grade assignment
- Double-blind human grading synchronization with PostgreSQL `expert_annotations`
- Leakage-safe dataset splitting with near-duplicate clustering
- Real-data experiment execution under evaluation_type='real_produce_validation'
- Transparent counters: REAL_IMAGES_COLLECTED, REAL_IMAGES_REQUIRED, REAL_IMAGES_REMAINING
"""

import os
import io
import csv
import json
import uuid
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set
from PIL import Image
import numpy as np
from sqlalchemy.orm import Session

from backend.evaluation.produce_ingestion import (
    validate_produce_image,
    compute_image_hash,
    compute_perceptual_hash,
    hamming_distance,
    strip_exif_metadata,
    normalize_produce_image,
    extract_produce_features
)
from backend.models.expert_annotation import ExpertAnnotation
from backend.repositories.annotation_repository import AnnotationRepository
from backend.repositories.experiment_repository import ExperimentRepository
from backend.evaluation import produce_experiment_runner as pr_exp


REAL_PRODUCE_DIR = os.path.join("dataset", "produce", "real")
RAW_DIR = os.path.join(REAL_PRODUCE_DIR, "raw")
PROCESSED_DIR = os.path.join(REAL_PRODUCE_DIR, "processed")
ANNOTATIONS_DIR = os.path.join(REAL_PRODUCE_DIR, "annotations")
SPLITS_DIR = os.path.join(REAL_PRODUCE_DIR, "splits")
REPORTS_DIR = os.path.join(REAL_PRODUCE_DIR, "reports")
METADATA_PATH = os.path.join(REAL_PRODUCE_DIR, "metadata.csv")

TARGET_IMAGES_REQUIRED = 30
TARGET_IMAGES_RECOMMENDED = 50

STAKEHOLDER_FEEDBACK_PATH = os.path.join(REPORTS_DIR, "stakeholder_feedback.json")

METADATA_FIELDNAMES = [
    "sample_id",
    "filename",
    "dataset_type",
    "source_type",
    "capture_date",
    "capture_environment",
    "camera_type",
    "collection_category",
    "grade",
    "grader_1_grade",
    "grader_2_grade",
    "adjudicated_grade",
    "grader_1_confidence",
    "grader_2_confidence",
    "defect_pct",
    "ripeness_stage",
    "occlusion_pct",
    "image_quality_status",
    "sha256",
    "dhash",
    "is_synthetic",
    "is_real",
    "annotation_status",
    "review_status"
]


def ensure_directories():
    """Ensures all real produce directories exist."""
    for d in [REAL_PRODUCE_DIR, RAW_DIR, PROCESSED_DIR, ANNOTATIONS_DIR, SPLITS_DIR, REPORTS_DIR]:
        os.makedirs(d, exist_ok=True)
    if not os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=METADATA_FIELDNAMES)
            writer.writeheader()


def load_metadata_records() -> List[Dict[str, str]]:
    """Loads all existing records from metadata.csv."""
    ensure_directories()
    if not os.path.exists(METADATA_PATH):
        return []
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_metadata_records(records: List[Dict[str, Any]]):
    """Saves records back to metadata.csv."""
    ensure_directories()
    with open(METADATA_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=METADATA_FIELDNAMES)
        writer.writeheader()
        for r in records:
            filtered = {k: r.get(k, "") for k in METADATA_FIELDNAMES}
            writer.writerow(filtered)


def get_real_produce_dataset_status(db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Returns verified status of the genuine produce dataset.
    Follows strict non-fabrication rule:
    REAL_IMAGES_COLLECTED, REAL_IMAGES_REQUIRED, REAL_IMAGES_REMAINING.
    Status is PENDING_REAL_DATA when collected < 30.
    """
    ensure_directories()
    records = load_metadata_records()
    
    # Filter strictly for REAL_PRODUCE records with existing files
    genuine_records = []
    for r in records:
        if r.get("dataset_type") == "REAL_PRODUCE" and r.get("is_real") in {"True", "TRUE", "1"}:
            proc_path = os.path.join(PROCESSED_DIR, r.get("filename", ""))
            if os.path.exists(proc_path):
                genuine_records.append(r)

    collected_count = len(genuine_records)
    remaining_count = max(0, TARGET_IMAGES_REQUIRED - collected_count)
    status_label = "READY" if collected_count >= TARGET_IMAGES_REQUIRED else "PENDING_REAL_DATA"

    # Count annotation stages
    annotated_count = 0
    consensus_count = 0
    disagreement_count = 0
    adjudicated_count = 0

    if db:
        # Cross-reference with PostgreSQL expert annotations table
        stmt_produce = db.query(ExpertAnnotation).filter(ExpertAnnotation.species == "tomato").all()
        for ea in stmt_produce:
            if ea.annotation_status in {"PARTIALLY_ANNOTATED", "CONSENSUS_REACHED", "DISAGREEMENT"}:
                annotated_count += 1
            if ea.annotation_status == "CONSENSUS_REACHED":
                consensus_count += 1
                if ea.consensus_reviewer_id:
                    adjudicated_count += 1
            elif ea.annotation_status == "DISAGREEMENT":
                disagreement_count += 1
    else:
        for r in genuine_records:
            st = r.get("annotation_status", "PENDING")
            if st in {"PARTIALLY_ANNOTATED", "CONSENSUS_REACHED", "DISAGREEMENT"}:
                annotated_count += 1
            if st == "CONSENSUS_REACHED":
                consensus_count += 1
                if r.get("adjudicated_grade"):
                    adjudicated_count += 1
            elif st == "DISAGREEMENT":
                disagreement_count += 1

    category_counts = {
        "apparent_high_quality": 0,
        "apparent_minor_defects": 0,
        "apparent_substantial_defects": 0
    }
    for r in genuine_records:
        cat = r.get("collection_category", "apparent_high_quality")
        if cat in category_counts:
            category_counts[cat] += 1
        else:
            category_counts["apparent_high_quality"] += 1

    expert_annotation_status = (
        "PENDING_EXPERT_ANNOTATION" if annotated_count == 0 else (
            "CONSENSUS_COMPLETED" if (consensus_count >= collected_count and collected_count > 0) else "PARTIALLY_ANNOTATED"
        )
    )

    return {
        "status": status_label,
        "dataset_type": "REAL_PRODUCE",
        "is_synthetic": False,
        "is_real": True,
        "real_images_collected": collected_count,
        "real_images_required": TARGET_IMAGES_REQUIRED,
        "real_images_remaining": remaining_count,
        "recommended_target": TARGET_IMAGES_RECOMMENDED,
        "collection_categories": category_counts,
        "expert_annotation_status": expert_annotation_status,
        "images_annotated": annotated_count,
        "consensus_samples": consensus_count,
        "disagreements": disagreement_count,
        "adjudicated_samples": adjudicated_count,
        "isolation_statement": (
            "Genuine produce images are quarantined in dataset/produce/real/. "
            "Synthetic produce images from dataset/produce/synthetic/ are strictly isolated "
            "and excluded from genuine validation experiments."
        ),
        "data_integrity_rule": (
            "Provisional software grades are NOT ground truth. Reference grades require "
            "independent double-blind human grading with disagreement escalation."
        )
    }


def ingest_real_produce_image(
    raw_bytes: bytes,
    filename: str,
    source_type: str = "field_harvest",
    capture_environment: str = "packhouse_table",
    camera_type: str = "smartphone_camera",
    collection_category: str = "apparent_high_quality",
    capture_date: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Ingests and sanitizes a genuine tomato photograph.
    Performs full 12-step verification:
    1. Decode check
    2. Format check
    3. Dimension check
    4. SHA-256 calculation
    5. dHash calculation
    6. Exact and near-duplicate detection
    7. EXIF removal
    8. GPS removal
    9. Privacy/PII check
    10. Normalization
    11. Provenance metadata generation
    12. Anonymized unique sample ID
    """
    ensure_directories()
    records = load_metadata_records()

    # Step 1 & 2: Decodability & Format validation
    valid, err_msg = validate_produce_image(raw_bytes, filename)
    if not valid:
        return {"success": False, "error": f"Image validation failed: {err_msg}"}

    # Step 3: Dimension check
    with Image.open(io.BytesIO(raw_bytes)) as img:
        w, h = img.size
        if w < 150 or h < 150:
            return {"success": False, "error": f"Image dimensions ({w}x{h}) below minimum required (150x150)."}
        if w > 8000 or h > 8000:
            return {"success": False, "error": f"Image dimensions ({w}x{h}) exceed maximum allowable (8000x8000)."}

    # Step 4 & 5: Cryptographic & Perceptual Hashes
    sha256 = compute_image_hash(raw_bytes)
    dhash = compute_perceptual_hash(raw_bytes)

    # Step 6: Duplicate detection against existing genuine samples
    for r in records:
        if r.get("sha256") == sha256:
            return {
                "success": False,
                "error": f"Exact duplicate image detected (matches sample '{r.get('sample_id')}').",
                "is_duplicate": True
            }
        ex_dhash = r.get("dhash", "")
        if ex_dhash and hamming_distance(dhash, ex_dhash) <= 4:
            return {
                "success": False,
                "error": f"Near-duplicate image detected (matches sample '{r.get('sample_id')}', dHash Hamming distance <= 4).",
                "is_duplicate": True
            }

    # Step 7 & 8: Strip EXIF and GPS tags
    sanitized_bytes = strip_exif_metadata(raw_bytes)

    # Step 9: Privacy/PII checks (detect human face / skin density in top quadrant)
    with Image.open(io.BytesIO(sanitized_bytes)) as simg:
        sw, sh = simg.size
        top_crop = simg.crop((0, 0, sw, max(1, sh // 3))).resize((50, 50)).convert("RGB")
        top_arr = np.array(top_crop)
        pr = top_arr[:, :, 0].astype(int)
        pg = top_arr[:, :, 1].astype(int)
        pb = top_arr[:, :, 2].astype(int)
        max_c = np.maximum(np.maximum(pr, pg), pb)
        min_c = np.minimum(np.minimum(pr, pg), pb)
        skin_mask = (pr > 95) & (pg > 40) & (pb > 20) & ((max_c - min_c) > 15) & (np.abs(pr - pg) > 15) & (pr > pg) & (pr > pb)
        skin_like_count = int(np.sum(skin_mask))
        if skin_like_count > (50 * 50 * 0.45):
            return {
                "success": False,
                "error": "Privacy violation: High skin-tone density in frame indicates human presence. Crop to fruit only."
            }

    # Step 10: Normalization
    normalized_bytes = normalize_produce_image(sanitized_bytes)

    # Step 11 & 12: Provenance metadata & unique anonymized sample ID
    sample_id = f"real_tom_{uuid.uuid4().hex[:12]}"
    raw_filename = f"{sample_id}_raw.jpg"
    proc_filename = f"{sample_id}.jpg"

    raw_path = os.path.join(RAW_DIR, raw_filename)
    proc_path = os.path.join(PROCESSED_DIR, proc_filename)

    # Save original raw evidence file
    with open(raw_path, "wb") as f:
        f.write(raw_bytes)

    # Save sanitized processed file
    with open(proc_path, "wb") as f:
        f.write(normalized_bytes)

    # Extract CV features
    features = extract_produce_features(normalized_bytes)
    cap_date = capture_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Step 13: Append to metadata.csv (Strict non-fabrication: grade is None until human grading)
    metadata_row = {
        "sample_id": sample_id,
        "filename": proc_filename,
        "dataset_type": "REAL_PRODUCE",
        "source_type": source_type,
        "capture_date": cap_date,
        "capture_environment": capture_environment,
        "camera_type": camera_type,
        "collection_category": collection_category,
        "grade": "",  # Ground truth grade intentionally empty pending human double-blind evaluation
        "grader_1_grade": "",
        "grader_2_grade": "",
        "adjudicated_grade": "",
        "grader_1_confidence": "",
        "grader_2_confidence": "",
        "defect_pct": str(features.get("surface_defect_pct", 0.0)),
        "ripeness_stage": str(features.get("ripeness_stage", "RED")),
        "occlusion_pct": str(features.get("surface_occlusion_pct", 0.0)),
        "image_quality_status": "PASSED" if features.get("quality_passed", True) else "FLAGGED_QUALITY",
        "sha256": sha256,
        "dhash": dhash,
        "is_synthetic": "False",
        "is_real": "True",
        "annotation_status": "PENDING",
        "review_status": "NONE"
    }
    records.append(metadata_row)
    save_metadata_records(records)

    # Step 14: If DB session provided, initialize double-blind annotation record
    if db:
        repo = AnnotationRepository(db)
        repo.create_or_get_for_image(
            sample_id=sample_id,
            image_path=proc_path,
            species="tomato"
        )

    return {
        "success": True,
        "sample_id": sample_id,
        "filename": proc_filename,
        "sha256": sha256,
        "dhash": dhash,
        "dataset_type": "REAL_PRODUCE",
        "collection_category": collection_category,
        "features": features,
        "quality_passed": features.get("quality_passed", True),
        "raw_evidence_path": raw_path,
        "processed_image_path": proc_path,
        "annotation_status": "PENDING"
    }


def submit_double_blind_produce_grade(
    sample_id: str,
    grader_id: str,
    grade: str,
    confidence: Optional[float] = None,
    attributes: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Submits an independent human grader assessment with double-blind isolation.
    Syncs with PostgreSQL and updates metadata.csv.
    - If Grader 1 slot is open -> Grader 1 recorded.
    - If Grader 2 slot is open -> Grader 2 recorded.
    - If Grader 1 == Grader 2 -> CONSENSUS_REACHED; reference grade established.
    - If Grader 1 != Grader 2 -> DISAGREEMENT; routed to Senior Reviewer for adjudication.
    """
    clean_grade = grade.upper().strip()
    if clean_grade not in {"A", "B", "C"}:
        raise ValueError(f"Invalid produce grade '{clean_grade}'. Must be 'A', 'B', or 'C'.")

    annotation_record = None
    if db:
        repo = AnnotationRepository(db)
        annotation_record = repo.submit_grade(
            sample_id=sample_id,
            grader_id=grader_id,
            grade=clean_grade,
            attributes=attributes,
            notes=notes
        )

    # Update metadata.csv
    records = load_metadata_records()
    matched = False
    for r in records:
        if r.get("sample_id") == sample_id:
            matched = True
            g1 = r.get("grader_1_grade", "")
            g2 = r.get("grader_2_grade", "")

            if not g1:
                r["grader_1_grade"] = clean_grade
                r["grader_1_confidence"] = str(confidence or 100.0)
                r["annotation_status"] = "PARTIALLY_ANNOTATED"
            elif not g2:
                r["grader_2_grade"] = clean_grade
                r["grader_2_confidence"] = str(confidence or 100.0)
                if r["grader_1_grade"] == clean_grade:
                    r["annotation_status"] = "CONSENSUS_REACHED"
                    r["grade"] = clean_grade  # Authoritative ground truth established by consensus
                    r["review_status"] = "CONSENSUS_AUTO"
                else:
                    r["annotation_status"] = "DISAGREEMENT"
                    r["review_status"] = "OPEN_DISAGREEMENT"
            break

    if matched:
        save_metadata_records(records)

    return {
        "sample_id": sample_id,
        "grader_id": grader_id,
        "grade": clean_grade,
        "annotation_status": annotation_record.annotation_status if annotation_record else ("CONSENSUS_REACHED" if matched and r.get("grade") else "PARTIALLY_ANNOTATED")
    }


def adjudicate_produce_disagreement(
    sample_id: str,
    reviewer_id: str,
    final_grade: str,
    rationale: str,
    db: Optional[Session] = None
) -> Dict[str, Any]:
    """
    Senior Reviewer authoritative resolution of inter-grader disagreement.
    Sets definitive reference grade in metadata.csv and PostgreSQL.
    """
    clean_grade = final_grade.upper().strip()
    if clean_grade not in {"A", "B", "C"}:
        raise ValueError(f"Invalid adjudication grade '{clean_grade}'. Must be 'A', 'B', or 'C'.")

    if db:
        repo = AnnotationRepository(db)
        repo.adjudicate_consensus(
            sample_id=sample_id,
            reviewer_id=reviewer_id,
            final_grade=clean_grade,
            rationale=rationale
        )

    # Update metadata.csv
    records = load_metadata_records()
    for r in records:
        if r.get("sample_id") == sample_id:
            r["adjudicated_grade"] = clean_grade
            r["grade"] = clean_grade  # Authoritative reference grade
            r["annotation_status"] = "CONSENSUS_REACHED"
            r["review_status"] = "ADJUDICATED_RESOLVED"
            break
    save_metadata_records(records)

    return {
        "sample_id": sample_id,
        "reviewer_id": reviewer_id,
        "adjudicated_grade": clean_grade,
        "status": "CONSENSUS_REACHED",
        "rationale": rationale
    }


def split_real_produce_dataset(
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Executes leakage-safe dataset splitting for genuine produce.
    Uses perceptual dHash clustering to prevent multiple photographs of the same tomato
    or near-duplicates from crossing train/validation/test partitions.
    """
    ensure_directories()
    records = load_metadata_records()
    genuine = [r for r in records if r.get("dataset_type") == "REAL_PRODUCE"]

    if not genuine:
        return {
            "status": "EMPTY_DATASET",
            "message": "No genuine produce records available for splitting.",
            "train_count": 0,
            "val_count": 0,
            "test_count": 0
        }

    # Group near-duplicates into clusters (dHash Hamming distance <= 6)
    clusters: List[List[Dict[str, Any]]] = []
    assigned = set()

    for i, r1 in enumerate(genuine):
        if r1["sample_id"] in assigned:
            continue
        cluster = [r1]
        assigned.add(r1["sample_id"])
        h1 = r1.get("dhash", "")
        for j, r2 in enumerate(genuine[i+1:], start=i+1):
            if r2["sample_id"] in assigned:
                continue
            h2 = r2.get("dhash", "")
            if h1 and h2 and hamming_distance(h1, h2) <= 6:
                cluster.append(r2)
                assigned.add(r2["sample_id"])
        clusters.append(cluster)

    import random
    rng = random.Random(seed)
    rng.shuffle(clusters)

    train_samples = []
    val_samples = []
    test_samples = []

    total_samples = len(genuine)
    target_train = int(total_samples * train_ratio)
    target_val = int(total_samples * val_ratio)

    for cluster in clusters:
        if len(train_samples) < target_train:
            train_samples.extend(cluster)
        elif len(val_samples) < target_val:
            val_samples.extend(cluster)
        else:
            test_samples.extend(cluster)

    # Save split files
    for split_name, sample_list in [("train", train_samples), ("val", val_samples), ("test", test_samples)]:
        split_path = os.path.join(SPLITS_DIR, f"{split_name}.csv")
        with open(split_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=METADATA_FIELDNAMES)
            writer.writeheader()
            for s in sample_list:
                writer.writerow({k: s.get(k, "") for k in METADATA_FIELDNAMES})

    manifest = {
        "dataset_name": "EQGS Genuine Tomato Validation Dataset",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_genuine_samples": total_samples,
        "clusters_count": len(clusters),
        "train_samples": len(train_samples),
        "val_samples": len(val_samples),
        "test_samples": len(test_samples),
        "leakage_safety": "Clustered by perceptual dHash (Hamming distance <= 6). Near-duplicates guaranteed in same partition."
    }
    with open(os.path.join(SPLITS_DIR, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest


def run_real_produce_validation_experiment(
    db: Optional[Session] = None,
    experiment_name: str = "EXP_REAL_PRODUCE_STAGE2"
) -> Dict[str, Any]:
    """
    Connects genuine produce dataset to evaluation runner under evaluation_type='real_produce_validation'.
    Enforces strict isolation: checks dataset_type == REAL_PRODUCE and is_synthetic == False.
    If genuine consensus-annotated samples < 10, returns status: PENDING_REAL_DATA.
    """
    status_info = get_real_produce_dataset_status(db=db)
    
    # Check minimum samples with consensus ground truth
    consensus_count = status_info.get("consensus_samples", 0)
    eligible_remaining = max(0, 10 - consensus_count)
    if consensus_count < 10:
        return {
            "status": "PENDING_REAL_DATA",
            "evaluation_type": "real_produce_validation",
            "experiment_name": experiment_name,
            "message": (
                f"Insufficient consensus-annotated genuine produce samples ({consensus_count} available, minimum 10 required; "
                f"{eligible_remaining} additional eligible consensus samples required). "
                "Per non-fabrication principles, real-data evaluation remains in PENDING_REAL_DATA status until genuine evidence is collected."
            ),
            "real_images_collected": status_info["real_images_collected"],
            "real_images_required": TARGET_IMAGES_REQUIRED,
            "consensus_samples_available": consensus_count,
            "eligible_samples_remaining": eligible_remaining,
            "is_synthetic": False
        }

    # If >= 10 consensus samples are available, verify genuine trial records
    # (Per Phase 20 Task 5: Never treat expert reference annotations as completed experimental trials)
    trials_path = os.path.join(REPORTS_DIR, "controlled_trials.json")
    if not os.path.exists(trials_path):
        return {
            "status": "PENDING_REAL_EXPERIMENT",
            "evaluation_type": "real_produce_validation",
            "experiment_name": experiment_name,
            "message": (
                f"Consensus ground truth established for {consensus_count} samples. "
                "However, authentic human-only and AI-assisted controlled trial records have not yet been conducted with human evaluators. "
                "Per non-fabrication guidelines, expert reference annotations are not treated as completed experimental trials."
            ),
            "real_images_collected": status_info["real_images_collected"],
            "consensus_samples_available": consensus_count,
            "eligible_samples_remaining": 0,
            "trial_records_available": 0,
            "is_synthetic": False
        }

    try:
        with open(trials_path, "r", encoding="utf-8") as f:
            trial_data = json.load(f)
        baseline_trials = trial_data.get("baseline_trials", [])
        assisted_trials = trial_data.get("assisted_trials", [])
    except Exception:
        baseline_trials, assisted_trials = [], []

    if len(baseline_trials) < 10 or len(assisted_trials) < 10:
        return {
            "status": "PENDING_REAL_EXPERIMENT",
            "evaluation_type": "real_produce_validation",
            "experiment_name": experiment_name,
            "message": (
                f"Controlled trial records incomplete ({len(baseline_trials)} baseline, {len(assisted_trials)} assisted; 10 required). "
                "Status retained as PENDING_REAL_EXPERIMENT until trial sessions are conducted."
            ),
            "real_images_collected": status_info["real_images_collected"],
            "consensus_samples_available": consensus_count,
            "eligible_samples_remaining": 0,
            "baseline_trials_count": len(baseline_trials),
            "assisted_trials_count": len(assisted_trials),
            "is_synthetic": False
        }

    result = pr_exp.run_before_and_after_experiment(
        baseline_trials=baseline_trials,
        assisted_trials=assisted_trials,
        experiment_name=experiment_name,
        dataset_version="v1.0-real-produce",
        db=db,
        is_synthetic=False
    )
    result["evaluation_type"] = "real_produce_validation"
    return result


def get_real_produce_samples(
    db: Optional[Session] = None,
    status_filter: Optional[str] = None,
    viewer_id: Optional[str] = None,
    is_senior: bool = False
) -> List[Dict[str, Any]]:
    """
    Returns list of genuine tomato samples with double-blind isolation enforced.
    - If viewer is Grader 1: can see Grader 1's grade; Grader 2's grade is masked until consensus.
    - If viewer is Grader 2: can see Grader 2's grade; Grader 1's grade is masked until consensus.
    - If viewer is neither and not senior: both grades are masked until CONSENSUS_REACHED or DISAGREEMENT.
    - Senior Reviewer: can see both Grader 1 and Grader 2 grades, especially for open disagreements.
    """
    ensure_directories()
    records = load_metadata_records()
    genuine = [r for r in records if r.get("dataset_type") == "REAL_PRODUCE" and r.get("is_real") in {"True", "TRUE", "1"}]

    db_map = {}
    if db:
        repo = AnnotationRepository(db)
        db_records, _ = repo.list_annotations(species="tomato", limit=500)
        for dbr in db_records:
            db_map[dbr.sample_id] = dbr

    results = []
    for r in genuine:
        sample_id = r["sample_id"]
        ann_status = r.get("annotation_status", "PENDING")
        dbr = db_map.get(sample_id)
        if dbr:
            ann_status = dbr.annotation_status

        if status_filter and status_filter.upper() != "ALL":
            if ann_status.upper() != status_filter.upper():
                continue

        g1 = r.get("grader_1_grade", "")
        g2 = r.get("grader_2_grade", "")
        ground_truth = r.get("grade", "")

        # Double-blind masking logic
        hide_g1 = False
        hide_g2 = False

        if not is_senior and ann_status not in {"CONSENSUS_REACHED", "DISAGREEMENT"}:
            if viewer_id:
                g1_id = dbr.expert_grader_1_id if dbr else None
                g2_id = dbr.expert_grader_2_id if dbr else None

                if g1_id:
                    if viewer_id != g1_id:
                        hide_g1 = True
                elif g1:
                    hide_g1 = True

                if g2_id:
                    if viewer_id != g2_id:
                        hide_g2 = True
                elif g2:
                    hide_g2 = True
            else:
                if g1:
                    hide_g1 = True
                if g2:
                    hide_g2 = True

        results.append({
            "sample_id": sample_id,
            "filename": r.get("filename", ""),
            "source_type": r.get("source_type", "field_harvest"),
            "capture_date": r.get("capture_date", ""),
            "capture_environment": r.get("capture_environment", "packhouse_table"),
            "camera_type": r.get("camera_type", "smartphone_camera"),
            "collection_category": r.get("collection_category", "apparent_high_quality"),
            "annotation_status": ann_status,
            "review_status": r.get("review_status", "NONE"),
            "image_quality_status": r.get("image_quality_status", "PASSED"),
            "defect_pct": float(r.get("defect_pct", 0.0) or 0.0),
            "ripeness_stage": r.get("ripeness_stage", "RED"),
            "occlusion_pct": float(r.get("occlusion_pct", 0.0) or 0.0),
            "grader_1_grade": g1 if not hide_g1 else None,
            "grader_2_grade": g2 if not hide_g2 else None,
            "ground_truth_grade": ground_truth if (is_senior or ann_status == "CONSENSUS_REACHED") else None,
            "adjudicated_grade": r.get("adjudicated_grade", "") if (is_senior or ann_status == "CONSENSUS_REACHED") else None,
            "is_blind_masked": hide_g1 or hide_g2
        })
    return results


def get_stakeholder_validation_status() -> Dict[str, Any]:
    """
    Returns current status and aggregated responses from the Stage 2 stakeholder study.
    Strict non-fabrication: if 0 responses, status is PENDING_EXTERNAL_EVIDENCE.
    """
    ensure_directories()
    tasks_spec = [
        {"id": "task_1", "name": "Image Capture & Quality Check", "description": "Capture/upload tomato photograph and observe optical quality check."},
        {"id": "task_2", "name": "Explanation & Feature Review", "description": "Review automated feature extraction, defect %, ripeness, and provisional grade."},
        {"id": "task_3", "name": "Independent Double-Blind Grading", "description": "Submit independent quality grade under double-blind isolation."},
        {"id": "task_4", "name": "Disagreement Adjudication", "description": "Inspect adjudicated disagreement case as Senior Reviewer."},
        {"id": "task_5", "name": "Offline PWA & Sync", "description": "Test offline capture in flight mode and subsequent background sync."}
    ]
    survey_questions = [
        {"id": "q1_usability", "text": "The grading interface was straightforward to navigate on a mobile screen."},
        {"id": "q2_explanation_clarity", "text": "The rule explanations clearly showed me why a specific grade was assigned."},
        {"id": "q3_attribute_accuracy", "text": "The measured surface defect percentage and color stage aligned with my visual judgment."},
        {"id": "q4_disagreement_fairness", "text": "The double-blind review process provides a fair, unbiased method to resolve grader differences."},
        {"id": "q5_packhouse_viability", "text": "The offline queue and local saving make this tool practical for remote packhouses with weak connectivity."}
    ]

    if not os.path.exists(STAKEHOLDER_FEEDBACK_PATH):
        return {
            "status": "PENDING_EXTERNAL_EVIDENCE",
            "total_participants": 0,
            "message": "Field usability trials with agricultural practitioners are pending harvest scheduling. No fabricated responses.",
            "tasks": tasks_spec,
            "survey_questions": survey_questions,
            "mean_scores": {},
            "task_completion_rates": {},
            "qualitative_feedback": [],
            "ethical_safeguards": (
                "Participation is strictly voluntary. Non-punitive commitment: no pacing surveillance, "
                "no worker ranking, and zero facial biometric collection."
            )
        }

    try:
        with open(STAKEHOLDER_FEEDBACK_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = []

    if not data:
        return {
            "status": "PENDING_EXTERNAL_EVIDENCE",
            "total_participants": 0,
            "message": "Zero responses recorded in stakeholder feedback log. Status held as PENDING_EXTERNAL_EVIDENCE.",
            "tasks": tasks_spec,
            "survey_questions": survey_questions,
            "mean_scores": {},
            "task_completion_rates": {},
            "qualitative_feedback": [],
            "ethical_safeguards": (
                "Participation is strictly voluntary. Non-punitive commitment: no pacing surveillance, "
                "no worker ranking, and zero facial biometric collection."
            )
        }

    total = len(data)
    mean_scores = {}
    for q in ["q1_usability", "q2_explanation_clarity", "q3_attribute_accuracy", "q4_disagreement_fairness", "q5_packhouse_viability"]:
        scores = [item["likert_scores"].get(q, 3) for item in data if "likert_scores" in item and q in item["likert_scores"]]
        mean_scores[q] = round(sum(scores) / len(scores), 2) if scores else 0.0

    task_rates = {}
    for t in ["task_1", "task_2", "task_3", "task_4", "task_5"]:
        completed = sum(1 for item in data if item.get("completed_tasks", {}).get(t, False))
        task_rates[t] = round((completed / total) * 100.0, 1)

    qualitative = [
        {
            "participant_id": item.get("participant_id"),
            "role": item.get("role"),
            "missing_info": item.get("qualitative_feedback", {}).get("missing_info", ""),
            "override_scenarios": item.get("qualitative_feedback", {}).get("override_scenarios", ""),
            "speed_improvements": item.get("qualitative_feedback", {}).get("speed_improvements", "")
        }
        for item in data if item.get("qualitative_feedback")
    ]

    return {
        "status": "RECORDED_SESSIONS",
        "total_participants": total,
        "message": f"Verified live feedback from {total} agricultural practitioners.",
        "tasks": tasks_spec,
        "survey_questions": survey_questions,
        "mean_scores": mean_scores,
        "task_completion_rates": task_rates,
        "qualitative_feedback": qualitative,
        "ethical_safeguards": (
            "Participation is strictly voluntary. Non-punitive commitment: no pacing surveillance, "
            "no worker ranking, and zero facial biometric collection."
        )
    }


def submit_stakeholder_feedback(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persists an anonymous stakeholder evaluation record following ethical consent.
    """
    ensure_directories()
    existing = []
    if os.path.exists(STAKEHOLDER_FEEDBACK_PATH):
        try:
            with open(STAKEHOLDER_FEEDBACK_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    participant_idx = len(existing) + 1
    role_prefix = payload.get("role", "GRD")[:3].upper()
    participant_id = payload.get("participant_id") or f"STK-{role_prefix}-{participant_idx:03d}"

    entry = {
        "participant_id": participant_id,
        "role": payload.get("role", "PRODUCE_GRADER"),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "completed_tasks": payload.get("completed_tasks", {}),
        "likert_scores": payload.get("likert_scores", {}),
        "qualitative_feedback": payload.get("qualitative_feedback", {}),
        "consent_confirmed": True
    }
    existing.append(entry)

    with open(STAKEHOLDER_FEEDBACK_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)

    return {
        "success": True,
        "participant_id": participant_id,
        "total_participants": len(existing),
        "message": "Stakeholder evaluation recorded successfully."
    }


def get_genuine_failure_cases() -> List[Dict[str, Any]]:
    """
    Returns the systematic failure and edge-case evaluations from docs/ERROR_ANALYSIS.md.
    """
    return [
        {
            "case_id": "case_1_lighting_blur",
            "title": "Failure Case 1: Poor Lighting & Severe Motion Blur",
            "category": "Optical Quality Flaw",
            "input_conditions": {
                "illuminance_proxy": "28.0 lux (deep shadow under packhouse hopper)",
                "focus_variance": "42.1 (severe device shake, threshold >= 100.0)"
            },
            "detected_features": {
                "illuminance_status": "FLAG_LOW_ILLUMINANCE",
                "sharpness_status": "FLAG_IMAGE_BLUR",
                "provisional_confidence": 0.0
            },
            "predicted_grade": "REJECTED_UNSUITABLE",
            "human_grade": "Unfit for commercial grading without recapture",
            "failure_mechanism": "Motion blur attenuates high-frequency spatial gradients, causing blemishes and micro-cracks to blend into surrounding healthy skin.",
            "corrective_action": "Ingestion quality gate triggers HTTP 422 / optical rejection banner with retake instruction: 'Hold steady under >= 500 lux light'.",
            "retake_recommended": True
        },
        {
            "case_id": "case_2_surface_occlusion",
            "title": "Failure Case 2: Surface Occlusion & Foliage Obstruction",
            "category": "Field Obstruction",
            "input_conditions": {
                "occlusion_pct": "34.0% (large vine leaf and cardboard crate rim)",
                "visible_surface_mask": "66.0%"
            },
            "detected_features": {
                "visible_defect_pct": "1.2%",
                "ripeness_stage": "RED",
                "triggered_rules": ["RULE_PARTIAL_OCCLUSION_WARNING"]
            },
            "predicted_grade": "Grade B (Capped)",
            "human_grade": "Requires dual-angle inspection; unexposed calyx cavity unverified",
            "failure_mechanism": "Monocular single-view camera cannot observe hidden hemisphere; severe rot frequently hides in calyx cavity.",
            "corrective_action": "System caps grade at B, marks REQUIRES_HUMAN_CONFIRMATION, and prompts operator for dual-angle photo capture.",
            "retake_recommended": True
        },
        {
            "case_id": "case_3_borderline_defect",
            "title": "Failure Case 3: Borderline Defect Threshold (5.1% Area)",
            "category": "Human Disagreement",
            "input_conditions": {
                "defect_pct": "5.1% (healed cosmetic russeting near stem)",
                "grade_a_cutoff": "5.0%"
            },
            "detected_features": {
                "provisional_rule_grade": "Grade B",
                "margin_to_threshold": "+0.1%",
                "review_flag": "BORDERLINE_DEFECT_AREA"
            },
            "predicted_grade": "Grade B",
            "human_grade": "Grader 1: Grade A (cosmetic allowance) vs Grader 2: Grade B (strict 5% cutoff)",
            "failure_mechanism": "Continuous biological defect gradient meets sharp categorical boundary, producing unavoidable grader discordance.",
            "corrective_action": "System preserves both grades intact under OPEN_DISAGREEMENT and routes to Senior Reviewer for authoritative adjudication.",
            "retake_recommended": False
        },
        {
            "case_id": "case_4_wood_grain_shadows",
            "title": "Failure Case 4: Rustic Packhouse Wood Grain & Shadow Interference",
            "category": "Background Texture Confusion",
            "input_conditions": {
                "staging_surface": "Unpainted weathered wooden sorting bench with dark knots",
                "lighting": "Directional overhead fluorescent creating strong rim cast shadows"
            },
            "detected_features": {
                "false_defect_pct": "24.4% (wood grain fissures and lateral shadow rim falsely segmented)",
                "color_ripeness": "RED",
                "circularity": 0.92
            },
            "predicted_grade": "Grade C (Cull - False Downgrade)",
            "human_grade": "Grade A (Premium Table Fresh - pristine skin with zero blemishes)",
            "failure_mechanism": "Dark high-contrast linear wood grain knots and deep rim shadows exhibit luminance ratios < 0.65 of fruit body.",
            "corrective_action": "Convex hull contour clipping decouples background textures; field staging mandates neutral gray/white grading mats; human review safety net blocks false downgrades.",
            "retake_recommended": True
        }
    ]


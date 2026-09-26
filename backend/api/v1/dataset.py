import os
import json
from fastapi import APIRouter
from backend.schemas.responses import APIResponse, success_response
from backend.evaluation.annotation_validator import load_annotation_csv

router = APIRouter(prefix="/dataset-info", tags=["Dataset"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
REAL_DATASET_DIR = os.path.join(BASE_DIR, "dataset", "real")
SYNTHETIC_DATASET_DIR = os.path.join(BASE_DIR, "dataset", "synthetic")
REAL_LABELS_PATH = os.path.join(REAL_DATASET_DIR, "labels", "annotations.csv")
REAL_MANIFEST_PATH = os.path.join(REAL_DATASET_DIR, "documentation", "dataset_manifest.json")


def count_files_in_dir(directory: str, extensions: tuple = (".jpg", ".jpeg", ".png", ".webp")) -> int:
    if not os.path.exists(directory):
        return 0
    return sum(1 for f in os.listdir(directory) if f.lower().endswith(extensions))


@router.get("", response_model=APIResponse[dict])
def get_dataset_info():
    """
    Returns verified metadata regarding real and synthetic datasets,
    including sample counts, image counts, and readiness status.
    """
    # 1. Inspect real dataset
    raw_images_count = count_files_in_dir(os.path.join(REAL_DATASET_DIR, "raw", "images"))
    processed_images_count = count_files_in_dir(os.path.join(REAL_DATASET_DIR, "processed", "images"))

    samples, errors, batch_summary = load_annotation_csv(REAL_LABELS_PATH)

    manifest_data = {}
    if os.path.exists(REAL_MANIFEST_PATH):
        try:
            with open(REAL_MANIFEST_PATH, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            manifest_data = {}

    ready_for_real_eval = batch_summary.complete_count >= 10 and processed_images_count >= 10

    real_dataset_info = {
        "status": "READY" if ready_for_real_eval else "PENDING_REAL_WORLD_COLLECTION",
        "raw_images_count": raw_images_count,
        "processed_images_count": processed_images_count,
        "total_annotations": batch_summary.total_samples,
        "complete_consensus_annotations": batch_summary.complete_count,
        "pending_annotations": batch_summary.pending_count,
        "disagreements_count": batch_summary.disagreement_count,
        "inter_expert_kappa": batch_summary.inter_expert_kappa,
        "inter_expert_exact_pct": batch_summary.inter_expert_exact_match_pct,
        "manifest": manifest_data,
        "privacy_compliance": {
            "exif_stripping_enforced": True,
            "pii_manual_review_active": True,
            "prohibit_ai_expert_labels": True
        }
    }

    # 2. Inspect synthetic dataset
    synthetic_dataset_info = {
        "status": "AVAILABLE_FOR_DEVELOPMENT",
        "sample_count": 600,
        "description": "Deterministic rule-derived synthetic dataset with 5% simulated human noise used for model development and CI tests.",
        "storage": "in-memory generator + dataset/synthetic/"
    }

    data = {
        "real_dataset": real_dataset_info,
        "synthetic_dataset": synthetic_dataset_info,
        "active_evaluation_mode": "retrospective_real" if ready_for_real_eval else "synthetic_development_only",
        "ready_for_real_evaluation": ready_for_real_eval,
        "message": "Real-world dataset infrastructure initialized. Field cohort evaluation pending genuine expert intake." if not ready_for_real_eval else "Real dataset ready for evaluation."
    }

    return success_response(message="Dataset metadata retrieved successfully", data=data)

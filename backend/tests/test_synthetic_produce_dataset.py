"""
Tests for Synthetic Produce Dataset (Stage 2 / Phase 16).
Verifies:
- Directory structure and manifest schema compliance.
- Image integrity, decoding, and uniqueness (no duplicate SHA-256 hashes).
- Optical quality gate rejection on underexposed & blurred synthetic samples.
- Strict isolation of synthetic data from genuine production splits.
- Provenance metadata and watermarking.
- REST API endpoints for synthetic dataset status and benchmark execution.
"""
import os
import json
import csv
import hashlib
from PIL import Image
import pytest

from backend.evaluation import synthetic_produce_pipeline as syn_pipe
from backend.repositories.experiment_repository import ExperimentRepository


SYNTHETIC_DIR = os.path.join("dataset", "produce", "synthetic")
MANIFEST_PATH = os.path.join(SYNTHETIC_DIR, "generation_manifest.json")
METADATA_PATH = os.path.join(SYNTHETIC_DIR, "metadata.csv")
QUALITY_REPORT_PATH = os.path.join(SYNTHETIC_DIR, "quality_report.json")


def test_synthetic_directory_and_manifest_structure():
    """Verifies directory layout, categories, and manifest structure."""
    assert os.path.exists(SYNTHETIC_DIR), "Synthetic root directory must exist."
    for cat in ["grade_a", "grade_b", "grade_c", "edge_cases"]:
        cat_dir = os.path.join(SYNTHETIC_DIR, cat)
        assert os.path.exists(cat_dir), f"Subdirectory '{cat}' must exist."

    assert os.path.exists(MANIFEST_PATH), "generation_manifest.json must exist."
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert "EQGS" in manifest["dataset_name"]
    assert manifest["target_total_samples"] >= 300
    assert manifest["verified_images_count"] >= 6
    assert "categories" in manifest
    assert "isolation_statement" in manifest
    assert "reproducible_prompts_count" in manifest
    assert manifest["reproducible_prompts_count"] >= 300


def test_synthetic_metadata_csv_structure():
    """Verifies metadata.csv contains proper headers, watermarks, and cryptographic hashes."""
    assert os.path.exists(METADATA_PATH), "metadata.csv must exist."
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) >= 300
    required_cols = {"sample_id", "filename", "category", "grade", "status", "intended_defect_pct", "sha256", "is_synthetic"}
    assert required_cols.issubset(set(reader.fieldnames or []))

    verified_rows = [r for r in rows if r.get("file_present") == "TRUE"]
    assert len(verified_rows) >= 6

    for row in verified_rows:
        assert row["is_synthetic"] in {"TRUE", "True", "1"}
        assert len(row["sha256"]) == 64


def test_physical_synthetic_images_integrity_and_hashes():
    """Validates physical image files: decodability, minimum size, and absence of duplicate hashes."""
    hashes = set()
    found_images = 0

    for cat in ["grade_a", "grade_b", "grade_c", "edge_cases"]:
        cat_dir = os.path.join(SYNTHETIC_DIR, cat)
        for fname in os.listdir(cat_dir):
            if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                fpath = os.path.join(cat_dir, fname)
                found_images += 1

                # Check decodability
                with Image.open(fpath) as img:
                    width, height = img.size
                    assert width > 100
                    assert height > 100
                    assert img.mode in {"RGB", "RGBA"}

                # Check file size (> 20KB)
                assert os.path.getsize(fpath) > 20000

                # Check uniqueness (no duplicate SHA-256)
                with open(fpath, "rb") as f:
                    content = f.read()
                    h = hashlib.sha256(content).hexdigest()
                    assert h not in hashes, f"Duplicate image hash detected: {fname}"
                    hashes.add(h)

    assert found_images >= 6, f"Expected at least 6 physical images, found {found_images}"


def test_optical_quality_gate_on_edge_case_blur():
    """
    Tests that syn_edge_001_blur.jpg is properly caught and rejected by the optical quality gate
    due to low illuminance and camera motion blur.
    """
    result = syn_pipe.evaluate_synthetic_dataset_sample("syn_edge_001_blur", category="edge_cases")
    assert result is not None, "Failed to load syn_edge_001_blur sample."
    assert result["is_synthetic"] is True
    assert result["synthetic_provenance"] == "AI_GENERATED_DEVELOPMENT_SAMPLE"

    # Must be rejected or flagged by the optical quality gate
    assert result["image_quality_passed"] is False or result["provisional_grade"] == "REJECTED_IMAGE"
    assert result["confidence"] == 0.0 or any("BLUR" in r or "ILLUMINANCE" in r for r in result["triggered_rules"])


def test_surface_occlusion_edge_case():
    """Tests evaluation of syn_edge_002_occlusion.jpg."""
    result = syn_pipe.evaluate_synthetic_dataset_sample("syn_edge_002_occlusion", category="edge_cases")
    assert result is not None, "Failed to load syn_edge_002_occlusion sample."
    assert result["is_synthetic"] is True
    # Evaluator extracts features: either occlusion flagged or defect area from foliage forces downgrade
    assert result["provisional_grade"] in {"B", "C"}
    assert any("OCCLUSION" in r or "DOWNGRADE" in r for r in result["triggered_rules"])


def test_strict_isolation_guarantee():
    """
    Ensures that synthetic images are strictly quarantined and never placed in genuine
    production directories (dataset/produce/processed or dataset/real).
    """
    processed_dir = os.path.join("dataset", "produce", "processed")
    if os.path.exists(processed_dir):
        for fname in os.listdir(processed_dir):
            assert not fname.startswith("syn_"), f"Synthetic image {fname} found in genuine processed dir!"

    real_dir = os.path.join("dataset", "real")
    if os.path.exists(real_dir):
        for root, _, files in os.walk(real_dir):
            for fname in files:
                assert not fname.startswith("syn_"), f"Synthetic image {fname} found in real dataset dir!"


def test_synthetic_summary_and_benchmark(db_session):
    """Tests summary extraction and benchmark execution in PostgreSQL."""
    summary = syn_pipe.get_synthetic_dataset_summary()
    assert summary["status"] in {"PARTIAL_PENDING_API_QUOTA", "COMPLETE"}
    assert summary["verified_images_count"] >= 6
    assert summary["target_total_samples"] >= 300
    assert "isolation_guarantee" in summary

    # Run benchmark experiment
    res = syn_pipe.run_synthetic_benchmark_experiment(db=db_session, experiment_name="TEST_SYNTHETIC_BENCHMARK")
    assert res["is_synthetic"] is True
    assert res["evaluation_type"] == "synthetic_produce_development"
    assert res["verified_samples_evaluated"] >= 6

    # Verify persisted in PostgreSQL
    repo = ExperimentRepository(db_session)
    experiments, count = repo.get_experiments(evaluation_type="synthetic_produce_development")
    assert count >= 1
    stored = experiments[0]
    assert stored is not None
    assert stored.experiment_name == "TEST_SYNTHETIC_BENCHMARK"
    assert stored.evaluation_type == "synthetic_produce_development"
    assert stored.performance_metrics.get("is_synthetic") is True


def test_synthetic_api_endpoints(client, db_session):
    """Verifies GET /api/v1/produce/synthetic-status and POST /api/v1/produce/synthetic-benchmark."""
    # Status endpoint
    resp = client.get("/api/v1/produce/synthetic-status")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["verified_images_count"] >= 6
    assert data["target_total_samples"] >= 300
    assert "qc_summary" in data

    # Benchmark endpoint
    payload = {"experiment_name": "API_TEST_SYN_BENCHMARK"}
    resp = client.post("/api/v1/produce/synthetic-benchmark", json=payload)
    assert resp.status_code == 200
    b_data = resp.json()["data"]
    assert b_data["is_synthetic"] is True
    assert b_data["evaluation_type"] == "synthetic_produce_development"


def test_quality_report_json_consistency():
    """Verifies consistency of quality_report.json."""
    assert os.path.exists(QUALITY_REPORT_PATH), "quality_report.json must exist."
    with open(QUALITY_REPORT_PATH, "r", encoding="utf-8") as f:
        qc = json.load(f)

    assert qc["total_images_verified_on_disk"] >= 6
    assert qc["duplicates_detected"] == 0
    assert qc["qc_pass_count"] + qc["qc_review_flagged_count"] + qc["qc_fail_count"] == qc["total_images_verified_on_disk"]

import os
import tempfile
from backend.evaluation.dataset_versioning import (
    validate_sample_record,
    compile_dataset_manifest,
    export_splits_to_csv,
    generate_dataset_quality_report
)
from backend.evaluation.dataset_splitter import split_dataset_group_aware


def test_validate_sample_record():
    valid_sample = {
        "sample_id": "COW-001",
        "final_consensus_grade": "A",
        "body_condition": 3.0
    }
    is_valid, issues = validate_sample_record(valid_sample)
    assert is_valid is True
    assert len(issues) == 0

    # Invalid BCS out of bounds
    invalid_sample_bcs = {
        "sample_id": "COW-002",
        "final_consensus_grade": "B",
        "body_condition": 6.5
    }
    is_valid, issues = validate_sample_record(invalid_sample_bcs)
    assert is_valid is False
    assert any("out of bounds" in i for i in issues)

    # Invalid grade
    invalid_sample_grade = {
        "sample_id": "COW-003",
        "final_consensus_grade": "Z",
        "body_condition": 3.0
    }
    is_valid, issues = validate_sample_record(invalid_sample_grade)
    assert is_valid is False
    assert any("Invalid consensus grade" in i for i in issues)


def test_compile_dataset_manifest_and_report():
    samples = [
        {"sample_id": "S1", "expert_grade_1": "A", "expert_grade_2": "A", "final_consensus_grade": "A", "annotation_status": "CONSENSUS_REACHED"},
        {"sample_id": "S2", "expert_grade_1": "B", "expert_grade_2": "B", "final_consensus_grade": "B", "annotation_status": "CONSENSUS_REACHED"},
        {"sample_id": "S3", "expert_grade_1": "B", "expert_grade_2": "C", "annotation_status": "DISAGREEMENT"},
        {"sample_id": "S4", "quality_flagged": True, "annotation_status": "REJECTED"},
    ]

    manifest = compile_dataset_manifest(samples, version_tag="v1.0.0-test")
    assert manifest["dataset_version"] == "v1.0.0-test"
    assert manifest["sample_metrics"]["verified_consensus_samples"] == 2
    assert manifest["sample_metrics"]["disagreement_samples"] == 1
    assert manifest["sample_metrics"]["rejected_samples"] == 1
    assert manifest["status"] == "PENDING_REAL_WORLD_COLLECTION"  # < 10 samples

    # Test report generation
    report = generate_dataset_quality_report(manifest)
    assert "Real Livestock Dataset Quality & Verification Report" in report
    assert "MANDATORY CLINICAL DISCLAIMER" in report
    assert "Strict Non-Inference" in report or "Non-Inference Boundary" in report


def test_export_splits_to_csv_no_leakage():
    # 12 samples across 4 distinct animal groups
    samples = []
    for group_idx in range(1, 5):
        for angle in ["L", "R", "F"]:
            samples.append({
                "sample_id": f"COW_{group_idx}_{angle}",
                "group_id": f"ANIMAL_{group_idx}",
                "species": "cattle",
                "body_condition": 3.0,
                "coat_quality": "Smooth",
                "eye_condition": "Clear",
                "wound_presence": "None",
                "mobility": "Normal",
                "appetite": "Good",
                "final_consensus_grade": "A",
                "image_path": f"images/COW_{group_idx}_{angle}.jpg"
            })

    split_res = split_dataset_group_aware(samples, target_ratios=(0.5, 0.25, 0.25))

    with tempfile.TemporaryDirectory() as tmpdir:
        exported = export_splits_to_csv(split_res, splits_dir=tmpdir)
        assert os.path.exists(exported["train"])
        assert os.path.exists(exported["val"])
        assert os.path.exists(exported["test"])

        # Check group isolation across train and test
        train_groups = {s["group_id"] for s in split_res["train"]}
        test_groups = {s["group_id"] for s in split_res["test"]}
        overlap = train_groups.intersection(test_groups)
        assert len(overlap) == 0, f"Cross-split animal group leakage detected: {overlap}"

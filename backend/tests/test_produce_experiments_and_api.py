"""
Tests for Produce Experiments Runner and API Endpoints.
Verifies dispute rate calculations, before-and-after persistence in PostgreSQL,
experiment summary dashboard generation, and REST API contract compliance.
"""
import io
import pytest
from PIL import Image, ImageDraw
from backend.evaluation import produce_experiment_runner as pr_exp
from backend.models.disagreement_review import DisagreementReview


def create_test_jpeg_bytes() -> bytes:
    img = Image.new("RGB", (150, 150), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse([15, 15, 135, 135], fill=(225, 35, 25))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_calculate_dispute_rate():
    g1 = ["A", "B", "A", "C"]
    g2 = ["A", "C", "A", "C"]  # 1 dispute out of 4 (index 1: B vs C)
    rate, disputes, total = pr_exp.calculate_dispute_rate(g1, g2)
    assert disputes == 1
    assert total == 4
    assert rate == 25.0

    # Relative reduction
    reduction = pr_exp.calculate_relative_dispute_reduction(dr_baseline=50.0, dr_assisted=20.0)
    assert reduction == 60.0


def test_run_before_and_after_experiment_persistence(db_session):
    baseline_trials = [
        {"sample_id": "s1", "grader_1_grade": "A", "grader_2_grade": "B", "reference_grade": "A", "duration_sec": 30.0},
        {"sample_id": "s2", "grader_1_grade": "B", "grader_2_grade": "B", "reference_grade": "B", "duration_sec": 28.0},
        {"sample_id": "s3", "grader_1_grade": "C", "grader_2_grade": "B", "reference_grade": "C", "duration_sec": 26.0},
    ]
    assisted_trials = [
        {"sample_id": "s1", "grader_1_grade": "A", "grader_2_grade": "A", "reference_grade": "A", "duration_sec": 18.0},
        {"sample_id": "s2", "grader_1_grade": "B", "grader_2_grade": "B", "reference_grade": "B", "duration_sec": 16.0},
        {"sample_id": "s3", "grader_1_grade": "C", "grader_2_grade": "C", "reference_grade": "C", "duration_sec": 15.0},
    ]

    res = pr_exp.run_before_and_after_experiment(
        baseline_trials=baseline_trials,
        assisted_trials=assisted_trials,
        experiment_name="TEST_EXP_001",
        dataset_version="v1.0-test",
        db=db_session
    )

    assert res["status"] == "completed"
    assert res["comparison"]["dispute_rate_baseline_pct"] > 50.0  # 2 of 3 disputed = 66.67%
    assert res["comparison"]["dispute_rate_assisted_pct"] == 0.0   # 0 disputed = 0%
    assert res["comparison"]["relative_dispute_reduction_pct"] == 100.0
    assert res["comparison"]["duration_reduction_pct"] > 0

    # Verify query
    dash = pr_exp.get_produce_experiment_dashboard_data(db_session)
    assert dash["status"] == "COMPLETED_MEASUREMENT"
    assert dash["measured_results"]["relative_dispute_reduction_pct"] == 100.0


def test_api_grade_produce_endpoint(client):
    payload = {
        "surface_defect_pct": 2.5,
        "ripeness_stage": "RED",
        "color_uniformity_pct": 88.0,
        "bruising_severity": "NONE",
        "shape_circularity": 0.85,
        "aspect_ratio": 1.0,
        "critical_defects": []
    }
    resp = client.post("/api/v1/produce/grade", json=payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["provisional_grade"] == "A"
    assert data["image_quality_passed"] is True
    assert "RULE_GRADE_A_PREMIUM" in data["triggered_rules"]


def test_api_grade_disagreement_and_persistence(client, db_session):
    # Grader submits human grade A, but system grades C due to 20% defect
    payload = {
        "surface_defect_pct": 20.0,
        "ripeness_stage": "RED",
        "human_grade": "A",
        "create_persistent_review": True
    }
    resp = client.post("/api/v1/produce/grade", json=payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["provisional_grade"] == "C"
    assert data["disagreement_detected"] is True
    assert data["persistent_review_id"] is not None

    # Verify persistent record in DB
    rev = db_session.query(DisagreementReview).first()
    assert rev is not None
    assert rev.original_human_grade == "A"
    assert rev.original_system_grade == "C"


def test_api_upload_and_grade_produce(client):
    img_bytes = create_test_jpeg_bytes()
    files = {"file": ("test_tomato.jpg", img_bytes, "image/jpeg")}
    data = {"human_grade": "A"}

    resp = client.post("/api/v1/produce/upload-and-grade", files=files, data=data)
    assert resp.status_code == 200
    res_data = resp.json()["data"]
    assert res_data["provisional_grade"] in {"A", "B", "C"}
    assert "extracted_features" in res_data


def test_api_produce_metadata_endpoints(client):
    # Dataset status
    resp = client.get("/api/v1/produce/dataset-status")
    assert resp.status_code == 200
    assert "status" in resp.json()["data"]

    # Edge cases
    resp = client.get("/api/v1/produce/edge-cases")
    assert resp.status_code == 200
    cases = resp.json()["data"]["edge_cases"]
    assert len(cases) == 3
    assert any("POOR_LIGHTING" in c["case_id"] for c in cases)
    assert any("OCCLUSION" in c["case_id"] for c in cases)
    assert any("BORDERLINE" in c["case_id"] for c in cases)

    # Experiment summary
    resp = client.get("/api/v1/produce/experiments/summary")
    assert resp.status_code == 200
    exp_summary = resp.json()["data"]
    assert exp_summary["status"] in {"PENDING_EXPERIMENT", "COMPLETED_MEASUREMENT"}

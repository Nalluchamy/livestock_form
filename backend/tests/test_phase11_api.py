import pytest
from fastapi.testclient import TestClient


def test_api_create_and_list_reviews(client: TestClient):
    # 1. Create a disagreement review
    payload = {
        "original_human_grade": "B",
        "original_system_grade": "C",
        "reviewer_rationale": "Body condition score is borderline 2.0"
    }
    create_res = client.post("/api/v1/reviews", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()["data"]
    assert created_data["original_human_grade"] == "B"
    assert created_data["original_system_grade"] == "C"
    assert created_data["status"] == "PENDING"
    review_id = created_data["id"]

    # 2. List reviews
    list_res = client.get("/api/v1/reviews")
    assert list_res.status_code == 200
    res_json = list_res.json()["data"]
    assert res_json["total"] >= 1
    assert any(r["id"] == review_id for r in res_json["reviews"])
    assert res_json["stats"]["pending_count"] >= 1

    # 3. Resolve review
    resolve_payload = {
        "reviewer_id": "SR-VET-42",
        "reviewer_action": "UPHELD_HUMAN",
        "reviewer_final_decision": "B",
        "reviewer_rationale": "Gait and muscle definition confirm Grade B."
    }
    resolve_res = client.post(f"/api/v1/reviews/{review_id}/resolve", json=resolve_payload)
    assert resolve_res.status_code == 200
    resolved_data = resolve_res.json()["data"]
    assert resolved_data["status"] == "RESOLVED"
    assert resolved_data["reviewer_final_decision"] == "B"
    assert resolved_data["original_human_grade"] == "B"  # Immutable!
    assert resolved_data["original_system_grade"] == "C"  # Immutable!


def test_api_dataset_info(client: TestClient):
    res = client.get("/api/v1/dataset-info")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "real_dataset" in data
    assert "synthetic_dataset" in data
    assert data["real_dataset"]["privacy_compliance"]["exif_stripping_enforced"] is True
    assert data["real_dataset"]["privacy_compliance"]["prohibit_ai_expert_labels"] is True


def test_api_experiments(client: TestClient):
    # 1. Trigger evaluation run
    trigger_payload = {
        "experiment_name": "api_test_eval_run",
        "dataset_version": "real-v1.0",
        "evaluation_type": "retrospective_real"
    }
    run_res = client.post("/api/v1/experiments/run", json=trigger_payload)
    assert run_res.status_code == 202
    run_data = run_res.json()["data"]
    assert "status" in run_data

    # 2. List experiments
    list_res = client.get("/api/v1/experiments")
    assert list_res.status_code == 200
    assert "experiments" in list_res.json()["data"]


def test_api_metrics_includes_persistent_review_stats(client: TestClient):
    # Create a pending review
    client.post("/api/v1/reviews", json={
        "original_human_grade": "A",
        "original_system_grade": "B",
    })

    res = client.get("/api/v1/metrics")
    assert res.status_code == 200
    data = res.json()["data"]
    assert "pending_reviews" in data
    assert data["pending_reviews"] >= 1
    assert "grade_distribution" in data

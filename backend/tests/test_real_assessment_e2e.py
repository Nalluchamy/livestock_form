import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.core.settings import settings
from backend.ml.train_real import train_and_evaluate_real_models
from backend.models.expert_annotation import ExpertAnnotation


def test_real_grading_api_e2e_with_escalation_and_disclaimer(client: TestClient):
    settings.DEMO_MODE = True
    
    # Grading payload with critical wound
    payload = {
        "human_grade": "D",
        "attributes": {
            "body_condition": 3.0,
            "coat_quality": "Rough",
            "eye_condition": "Clear",
            "wound_presence": "Severe",
            "mobility": "Normal",
            "appetite": "Good"
        }
    }

    res = client.post("/api/v1/grade", json=payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["grade"] == "D"
    assert data["urgent_escalation"] is True
    assert "reasons" in data
    assert "escalation_reasons" in data
    assert "clinical_disclaimer" in data
    assert "veterinary medical diagnosis" in data["clinical_disclaimer"]

    # Restore
    settings.DEMO_MODE = False


def test_real_training_runner_pending_when_few_samples():
    res = train_and_evaluate_real_models(experiment_name="test_pending_check")
    assert res["status"] == "PENDING_REAL_DATA"
    assert res["trained"] is False
    assert "deferred" in res["message"]


def test_real_training_runner_executes_with_consensus_cohort(db_session: Session):
    # Insert 12 mock consensus annotations into db_session
    for i in range(12):
        annotation = ExpertAnnotation(
            sample_id=f"COW-TEST-LOT-{i}",
            image_path=f"images/cow_{i}.jpg",
            species="cattle",
            body_condition=3.0 if i % 2 == 0 else 2.2,
            coat_quality="Smooth" if i % 2 == 0 else "Slightly rough",
            eye_condition="Clear",
            wound_presence="None",
            mobility="Normal",
            appetite="Good",
            expert_grader_1_id="EXP-1",
            expert_grade_1="A" if i % 2 == 0 else "B",
            expert_grader_2_id="EXP-2",
            expert_grade_2="A" if i % 2 == 0 else "B",
            final_consensus_grade="A" if i % 2 == 0 else "B",
            annotation_status="CONSENSUS_REACHED"
        )
        db_session.add(annotation)
    db_session.commit()

    # Note: train_and_evaluate_real_models internally opens a SessionLocal.
    # To test execution with DataFrames, we can pass mock data or test the logic
    from backend.ml.train_real import train_and_evaluate_real_models
    import unittest.mock as mock

    mock_train_df = [
        {"sample_id": f"COW-{j}", "group_id": f"GRP-{j}", "body_condition": 3.0 if j % 2 == 0 else 2.2, "coat_quality": "Smooth" if j % 2 == 0 else "Rough", "eye_condition": "Clear", "wound_presence": "None", "mobility": "Normal", "appetite": "Good", "final_consensus_grade": "A" if j % 2 == 0 else "B"}
        for j in range(10)
    ]
    mock_test_df = [
        {"sample_id": f"COW-{j}", "group_id": f"GRP-{j}", "body_condition": 3.0 if j % 2 == 0 else 2.2, "coat_quality": "Smooth" if j % 2 == 0 else "Rough", "eye_condition": "Clear", "wound_presence": "None", "mobility": "Normal", "appetite": "Good", "final_consensus_grade": "A" if j % 2 == 0 else "B"}
        for j in range(10, 14)
    ]

    import pandas as pd
    with mock.patch("backend.ml.train_real.load_consensus_data_from_db_or_csv", return_value=(pd.DataFrame(mock_train_df), pd.DataFrame(mock_test_df))):
        eval_res = train_and_evaluate_real_models(experiment_name="test_cohort_run")
        assert eval_res["status"] == "COMPLETED"
        assert eval_res["trained"] is True
        assert "decision_tree" in eval_res["metrics"]
        assert "logistic_regression" in eval_res["metrics"]

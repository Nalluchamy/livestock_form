import os
import tempfile
import csv
import pytest

from backend.evaluation.real_dataset_runner import (
    run_real_evaluation, 
    evaluate_model_predictions
)


def test_real_evaluation_pending_when_file_absent(db_session):
    non_existent = "dataset/real/labels/non_existent_annotations.csv"
    res = run_real_evaluation(labels_csv_path=non_existent, db_session=db_session)
    assert res["status"] == "PENDING_REAL_DATA"
    assert "pending" in res["message"].lower()
    assert res["evaluation_type"] == "retrospective_real"
    assert "Not yet measured" in res["actual_human_assisted_dispute_reduction"]


def test_real_evaluation_pending_when_insufficient_samples(db_session):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, newline="") as tmp:
        writer = csv.writer(tmp)
        writer.writerow(["sample_id", "body_condition", "coat_quality", "eye_condition", "wound_presence", "mobility", "appetite", "expert_grade_1", "expert_grade_2", "final_consensus_grade", "annotation_status"])
        # Only 2 rows
        writer.writerow(["S1", "3.0", "Smooth", "Clear", "None", "Normal", "Good", "A", "A", "A", "CONSENSUS_REACHED"])
        writer.writerow(["S2", "2.0", "Rough", "Clear", "Minor", "Normal", "Fair", "B", "B", "B", "CONSENSUS_REACHED"])
        tmp_path = tmp.name

    try:
        res = run_real_evaluation(labels_csv_path=tmp_path, db_session=db_session)
        assert res["status"] == "PENDING_REAL_DATA"
        assert "insufficient" in res["message"].lower()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_evaluate_model_predictions():
    y_true = ["A", "B", "C", "D", "A", "B", "C", "D"]
    y_pred = ["A", "B", "C", "C", "A", "B", "C", "D"]  # 7 / 8 match
    confidences = [90.0, 85.0, 80.0, 60.0, 95.0, 88.0, 82.0, 91.0]

    metrics = evaluate_model_predictions(y_true, y_pred, confidences)
    assert metrics["accuracy"] == 87.5
    assert metrics["adjacent_agreement_pct"] == 100.0
    assert metrics["confidence_stats"]["mean"] > 80.0
    assert "A" in metrics["confusion_matrix"]

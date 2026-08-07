"""
Unit and API schema tests for backend/evaluation/agreement_metrics.py
"""
import os
import pytest
from fastapi.testclient import TestClient
from backend.main import create_app
from backend.evaluation.agreement_metrics import (
    cohen_kappa,
    exact_match_percentage,
    adjacent_match_percentage,
    evaluate_validation_dataset
)

app = create_app()
client = TestClient(app)

def test_cohen_kappa_perfect_agreement():
    y1 = ["A", "B", "C", "D"]
    y2 = ["A", "B", "C", "D"]
    kappa = cohen_kappa(y1, y2)
    assert kappa == 1.0

def test_exact_and_adjacent_match():
    y1 = ["A", "B", "C", "D"]
    y2 = ["A", "B", "D", "D"]
    assert exact_match_percentage(y1, y2) == 75.0
    assert adjacent_match_percentage(y1, y2) == 100.0

def test_evaluate_validation_dataset():
    metrics = evaluate_validation_dataset()
    assert "human_baseline" in metrics
    assert "rule_engine_vs_consensus" in metrics
    assert "decision_tree_ml_vs_consensus" in metrics
    assert metrics["dataset_info"]["total_samples"] == 32
    assert metrics["human_baseline"]["cohen_kappa"] > 0.0

def test_agreement_metrics_csv_misalignment_raises_error(tmp_path):
    # Create temp directory with misaligned CSV files
    attr_file = tmp_path / "attributes.csv"
    g1_file = tmp_path / "grader_1.csv"
    g2_file = tmp_path / "grader_2.csv"

    attr_file.write_text("sample_id,body_condition,coat_quality,eye_condition,wound_presence,mobility,appetite\nVAL-001,3.0,Smooth,Clear,None,Normal,Good\nVAL-002,3.0,Smooth,Clear,None,Normal,Good")
    g1_file.write_text("sample_id,human_grade\nVAL-001,A") # Missing VAL-002
    g2_file.write_text("sample_id,human_grade\nVAL-001,A\nVAL-002,A")

    with pytest.raises(ValueError, match="CSV Alignment Mismatch!"):
        evaluate_validation_dataset(data_dir=str(tmp_path))

def test_agreement_metrics_api_schema_and_range():
    response = client.get("/api/v1/metrics/agreement")
    assert response.status_code == 200
    
    body = response.json()
    assert body["status"] == "success"
    assert "data" in body
    
    data = body["data"]
    assert "dataset_info" in data
    assert "human_baseline" in data
    assert "rule_engine_vs_consensus" in data
    assert "decision_tree_ml_vs_consensus" in data
    
    for metric_key in ["human_baseline", "rule_engine_vs_consensus", "decision_tree_ml_vs_consensus"]:
        metric_set = data[metric_key]
        assert -1.0 <= metric_set["cohen_kappa"] <= 1.0
        assert 0.0 <= metric_set["exact_match_pct"] <= 100.0
        assert 0.0 <= metric_set["adjacent_match_pct"] <= 100.0

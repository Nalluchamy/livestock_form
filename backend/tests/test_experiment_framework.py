import os
import pytest
from backend.evaluation import experiment_runner, error_analyzer, report_generator


def test_experiment_runner():
    results = experiment_runner.run_experiment_trial(sample_count=50, seed=42)
    assert results["sample_count"] == 50
    assert "baseline" in results
    assert "assisted" in results
    assert results["assisted"]["agreement_rate"] > results["baseline"]["agreement_rate"]


def test_error_analyzer():
    attrs = {"body_condition": 2.0}
    category = error_analyzer.classify_error(attrs, rule_grade="B", target_grade="C")
    assert category == "Borderline BCS Case"


def test_report_generator():
    report_generator.build_all_reports()
    reports_dir = report_generator.REPORTS_DIR
    
    assert os.path.exists(os.path.join(reports_dir, "experiment_report.md"))
    assert os.path.exists(os.path.join(reports_dir, "comparison_report.md"))
    assert os.path.exists(os.path.join(reports_dir, "metrics_report.md"))
    assert os.path.exists(os.path.join(reports_dir, "stakeholder_validation.md"))
    assert os.path.exists(os.path.join(reports_dir, "limitations_report.md"))

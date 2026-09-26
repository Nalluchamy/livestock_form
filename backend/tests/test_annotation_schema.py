import pytest
from backend.schemas.annotation import ExpertAnnotationSample
from backend.evaluation.annotation_validator import (
    validate_single_record,
    compute_cohen_kappa,
    compute_exact_agreement,
    compute_adjacent_agreement
)


def test_valid_annotation_sample():
    data = {
        "sample_id": "REAL-001",
        "image_path": "images/real_001.jpg",
        "body_condition": 3.0,
        "coat_quality": "Smooth",
        "eye_condition": "Clear",
        "wound_presence": "None",
        "mobility": "Normal",
        "appetite": "Good",
        "weight_if_available": 480.5,
        "expert_grade_1": "A",
        "expert_grade_2": "A",
        "final_consensus_grade": "A",
        "annotation_status": "CONSENSUS_REACHED"
    }
    sample, errors = validate_single_record(data)
    assert errors == []
    assert sample is not None
    assert sample.body_condition == 3.0
    assert sample.expert_grade_1 == "A"


def test_incomplete_annotation_missing_weight():
    data = {
        "sample_id": "REAL-002",
        "body_condition": 2.5,
        "coat_quality": "Slightly rough",
        "eye_condition": "Clear",
        "wound_presence": "None",
        "mobility": "Normal",
        "appetite": "Fair",
        "weight_if_available": None,  # optional
        "expert_grade_1": "B",
        "expert_grade_2": None,  # pending second review
    }
    sample, errors = validate_single_record(data)
    assert errors == []
    assert sample is not None
    assert sample.annotation_status == "PENDING"
    assert sample.weight_if_available is None


def test_disagreement_preservation():
    data = {
        "sample_id": "REAL-003",
        "body_condition": 2.2,
        "coat_quality": "Rough",
        "eye_condition": "Clear",
        "wound_presence": "Minor",
        "mobility": "Normal",
        "appetite": "Fair",
        "expert_grade_1": "B",
        "expert_grade_2": "C",  # Disagreement!
        "final_consensus_grade": None,
    }
    sample, errors = validate_single_record(data)
    assert errors == []
    assert sample is not None
    # Must preserve disagreement status without forcing consensus
    assert sample.annotation_status == "DISAGREEMENT"
    assert sample.final_consensus_grade is None


def test_invalid_attribute_value_rejected():
    data = {
        "sample_id": "REAL-004",
        "body_condition": 3.0,
        "coat_quality": "SuperSilky",  # Invalid!
        "eye_condition": "Clear",
        "wound_presence": "None",
        "mobility": "Normal",
        "appetite": "Good",
    }
    sample, errors = validate_single_record(data)
    assert sample is None
    assert any("coat_quality" in e for e in errors)


def test_agreement_calculations():
    # Exact match trial
    r1 = ["A", "B", "C", "D"]
    r2 = ["A", "B", "C", "D"]
    assert compute_exact_agreement(r1, r2) == 100.0
    assert compute_adjacent_agreement(r1, r2) == 100.0
    assert compute_cohen_kappa(r1, r2) == 1.0

    # Adjacent match trial (A vs B, B vs C, etc.)
    r3 = ["A", "B", "C", "C"]
    r4 = ["B", "C", "D", "C"]
    assert compute_exact_agreement(r3, r4) == 25.0  # only index 3 matches
    assert compute_adjacent_agreement(r3, r4) == 100.0  # all are within 1 grade

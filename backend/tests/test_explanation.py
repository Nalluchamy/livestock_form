import pytest
from backend.grading import constants
from backend.services.explanation import generate_explanation


def test_generate_explanation_critical():
    final_grade = constants.GRADE_D
    sub_grades = {
        "attr1": constants.GRADE_A,
        "attr2": constants.GRADE_D
    }
    reasons = {
        "attr1": "Good thing",
        "attr2": "Bad thing"
    }
    
    explanation = generate_explanation(final_grade, sub_grades, reasons)
    
    assert len(explanation) == 1
    assert "Critical Failure" in explanation[0]
    assert "Bad thing" in explanation[0]
    assert "Good thing" not in explanation[0]


def test_generate_explanation_normal():
    final_grade = constants.GRADE_B
    sub_grades = {
        "attr1": constants.GRADE_A,
        "attr2": constants.GRADE_C
    }
    reasons = {
        "attr1": "Good thing",
        "attr2": "Warning thing"
    }
    
    explanation = generate_explanation(final_grade, sub_grades, reasons)
    
    assert len(explanation) == 2
    assert any("Passed (A): Good thing" in e for e in explanation)
    assert any("Warning (C): Warning thing" in e for e in explanation)

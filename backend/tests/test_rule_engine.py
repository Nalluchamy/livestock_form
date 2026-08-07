import pytest
from backend.grading import constants, rules
from backend.services.rule_engine import evaluate_grading_rules


def test_evaluate_healthy_animal():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good",
    }
    final_grade, sub_grades, reasons = evaluate_grading_rules(attrs)
    
    assert final_grade == constants.GRADE_A
    assert sub_grades[constants.ATTR_BODY_CONDITION] == constants.GRADE_A
    assert len(reasons) == 6


def test_evaluate_critical_animal():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_WOUND_PRESENCE: "Severe", # Trigger Critical Failure
    }
    final_grade, sub_grades, reasons = evaluate_grading_rules(attrs)
    
    assert final_grade == constants.GRADE_D
    assert sub_grades[constants.ATTR_WOUND_PRESENCE] == constants.GRADE_D


def test_evaluate_borderline_animal():
    # Two C grades should trigger the Warning Threshold -> Max C
    attrs = {
        constants.ATTR_BODY_CONDITION: 1.5, # C
        constants.ATTR_COAT_QUALITY: "Rough", # C
        constants.ATTR_EYE_CONDITION: "Clear", # A
        constants.ATTR_WOUND_PRESENCE: "None", # A
    }
    final_grade, sub_grades, reasons = evaluate_grading_rules(attrs)
    
    assert final_grade == constants.GRADE_C

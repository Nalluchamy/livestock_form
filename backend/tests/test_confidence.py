import pytest
from backend.grading import constants
from backend.services.confidence import calculate_confidence


def test_confidence_perfect():
    sub_grades = {"attr1": constants.GRADE_A, "attr2": constants.GRADE_A}
    conf = calculate_confidence(sub_grades, missing_attributes=[], has_image=True)
    assert conf == 100.0


def test_confidence_missing_attributes():
    sub_grades = {"attr1": constants.GRADE_A}
    conf = calculate_confidence(sub_grades, missing_attributes=["attr2", "attr3"], has_image=True)
    # 100 - (2 * 15) = 70
    assert conf == 70.0


def test_confidence_missing_image():
    sub_grades = {"attr1": constants.GRADE_A}
    conf = calculate_confidence(sub_grades, missing_attributes=[], has_image=False)
    # 100 - 20 = 80
    assert conf == 80.0


def test_confidence_contradiction():
    # A and D in the same grading event
    sub_grades = {"attr1": constants.GRADE_A, "attr2": constants.GRADE_D}
    conf = calculate_confidence(sub_grades, missing_attributes=[], has_image=True)
    # 100 - 20 = 80
    assert conf == 80.0

import pytest
from backend.grading import constants
from backend.services.grading_service import generate_grade, detect_disagreement


def test_generate_grade_success():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good",
    }
    result = generate_grade(attrs, has_image=True)
    
    assert result.grade == constants.GRADE_A
    assert result.confidence == 100.0
    assert not result.missing_attributes
    assert not result.review_required


def test_generate_grade_missing_data():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        # Missing all others
    }
    result = generate_grade(attrs, has_image=True)
    
    # 5 missing attrs = -75 confidence
    assert result.confidence == 25.0
    assert len(result.missing_attributes) == 5
    assert result.review_required is True  # Due to low confidence


def test_generate_grade_all_missing():
    with pytest.raises(ValueError, match="Cannot grade"):
        generate_grade({}, has_image=True)


def test_detect_disagreement():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good",
    }
    result = generate_grade(attrs, has_image=True)
    
    # Human grades B, System graded A
    disagreement = detect_disagreement("B", result)
    
    assert disagreement is not None
    assert disagreement.human_grade == "B"
    assert disagreement.system_grade == "A"
    assert disagreement.review_required is True


def test_no_disagreement():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good",
    }
    result = generate_grade(attrs, has_image=True)
    
    # Both grade A
    disagreement = detect_disagreement("A", result)
    assert disagreement is None

from backend.grading import constants
from backend.services.grading_service import generate_grade, MANDATORY_VETERINARY_DISCLAIMER


def test_clinical_escalation_grade_d_overall():
    attrs = {
        constants.ATTR_BODY_CONDITION: 1.2,  # Severe emaciation triggers Grade D
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good"
    }
    result = generate_grade(attrs, has_image=True)
    assert result.grade == constants.GRADE_D
    assert result.urgent_escalation is True
    assert result.review_required is True
    assert any("Critical (Grade D)" in r or "emaciation" in r for r in result.escalation_reasons)
    assert result.clinical_disclaimer == MANDATORY_VETERINARY_DISCLAIMER


def test_clinical_escalation_severe_wounds():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "Severe",  # Critical wound
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good"
    }
    result = generate_grade(attrs, has_image=True)
    assert result.grade == constants.GRADE_D
    assert result.urgent_escalation is True
    assert any("Severe external wounds" in r for r in result.escalation_reasons)


def test_clinical_escalation_unable_to_stand():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Unable to stand",  # Downer cow
        constants.ATTR_APPETITE: "Good"
    }
    result = generate_grade(attrs, has_image=True)
    assert result.grade == constants.GRADE_D
    assert result.urgent_escalation is True
    assert any("Unable to stand" in r or "downer" in r for r in result.escalation_reasons)


def test_clinical_escalation_severe_eye_infection():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Severe infection",  # Pinkeye / corneal perforation
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good"
    }
    result = generate_grade(attrs, has_image=True)
    assert result.grade == constants.GRADE_D
    assert result.urgent_escalation is True
    assert any("ocular infection" in r for r in result.escalation_reasons)


def test_healthy_animal_no_urgent_escalation():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good"
    }
    result = generate_grade(attrs, has_image=True)
    assert result.grade == constants.GRADE_A
    assert result.urgent_escalation is False
    assert len(result.escalation_reasons) == 0
    assert result.clinical_disclaimer == MANDATORY_VETERINARY_DISCLAIMER

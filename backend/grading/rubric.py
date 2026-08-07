"""
Rubric mappings that map raw measured values to their component grades.
"""
from typing import Dict, Any, Tuple
from backend.grading import constants


def map_body_condition(bcs: float) -> Tuple[str, str]:
    """
    Body Condition Score mapping (1-5 scale).
    3 is optimal (A), 2/4 are B, 1.5/4.5 are C, 1 or 5 are D.
    Returns (Grade, Reason).
    """
    if 2.5 <= bcs <= 3.5:
        return constants.GRADE_A, "Optimal body condition"
    elif 2.0 <= bcs < 2.5 or 3.5 < bcs <= 4.0:
        return constants.GRADE_B, "Slightly under/overweight"
    elif 1.5 <= bcs < 2.0 or 4.0 < bcs <= 4.5:
        return constants.GRADE_C, "Poor body condition"
    else:
        return constants.GRADE_D, "Emaciated or dangerously obese"


def map_categorical(value: str, mappings: Dict[str, str], attr_name: str) -> Tuple[str, str]:
    """Maps a categorical value to a grade based on a mapping dictionary."""
    grade = mappings.get(value)
    if not grade:
        raise ValueError(f"Unknown value '{value}' for {attr_name}")
    return grade, f"{attr_name.replace('_', ' ').capitalize()} is {value.lower()}"


COAT_MAPPING = {
    "Smooth": constants.GRADE_A,
    "Slightly rough": constants.GRADE_B,
    "Rough": constants.GRADE_C,
    "Severe lesions": constants.GRADE_D,
}

EYE_MAPPING = {
    "Clear": constants.GRADE_A,
    "Slight discharge": constants.GRADE_B,
    "Cloudy": constants.GRADE_C,
    "Severe infection": constants.GRADE_D,
}

WOUND_MAPPING = {
    "None": constants.GRADE_A,
    "Minor": constants.GRADE_B,
    "Moderate": constants.GRADE_C,
    "Severe": constants.GRADE_D,
}

MOBILITY_MAPPING = {
    "Normal": constants.GRADE_A,
    "Slight limp": constants.GRADE_B,
    "Lame": constants.GRADE_C,
    "Unable to stand": constants.GRADE_D,
}

APPETITE_MAPPING = {
    "Good": constants.GRADE_A,
    "Fair": constants.GRADE_B,
    "Poor": constants.GRADE_C,
    "None": constants.GRADE_D,
}


def evaluate_attribute(attr: str, value: Any) -> Tuple[str, str]:
    """Evaluates a single attribute and returns its sub-grade and reason."""
    if attr == constants.ATTR_BODY_CONDITION:
        return map_body_condition(float(value))
    elif attr == constants.ATTR_COAT_QUALITY:
        return map_categorical(value, COAT_MAPPING, attr)
    elif attr == constants.ATTR_EYE_CONDITION:
        return map_categorical(value, EYE_MAPPING, attr)
    elif attr == constants.ATTR_WOUND_PRESENCE:
        return map_categorical(value, WOUND_MAPPING, attr)
    elif attr == constants.ATTR_MOBILITY:
        return map_categorical(value, MOBILITY_MAPPING, attr)
    elif attr == constants.ATTR_APPETITE:
        return map_categorical(value, APPETITE_MAPPING, attr)
    else:
        raise ValueError(f"Unknown attribute: {attr}")

from typing import Dict, List
from backend.grading import constants


def calculate_confidence(
    sub_grades: Dict[str, str], 
    missing_attributes: List[str], 
    has_image: bool = True
) -> float:
    """
    Calculates the confidence score (0-100) of the grading prediction.
    
    Factors:
    - Base confidence starts at 100.
    - Missing attributes heavily penalize confidence.
    - Contradictory observations (e.g., A mixed with D) penalize confidence.
    - Missing image penalizes confidence by 20.
    """
    confidence = float(constants.CONFIDENCE_MAX)
    
    if not sub_grades:
        return 0.0

    # Penalize for missing data
    confidence -= len(missing_attributes) * constants.PENALTY_MISSING_ATTR

    # Penalize for missing image
    if not has_image:
        confidence -= 20.0

    # Detect contradictions
    grades_present = set(sub_grades.values())
    if constants.GRADE_A in grades_present and constants.GRADE_D in grades_present:
        confidence -= constants.PENALTY_CONTRADICTION
    elif constants.GRADE_B in grades_present and constants.GRADE_D in grades_present:
        confidence -= (constants.PENALTY_CONTRADICTION / 2)

    # Ensure bounds
    if confidence < constants.CONFIDENCE_MIN:
        confidence = constants.CONFIDENCE_MIN
    
    return round(confidence, 1)

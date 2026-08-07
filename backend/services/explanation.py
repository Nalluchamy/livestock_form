from typing import Dict, List
from backend.grading import constants


def generate_explanation(
    final_grade: str, 
    sub_grades: Dict[str, str], 
    reasons: Dict[str, str]
) -> List[str]:
    """
    Translates the fired rules and sub-grades into a human-readable list of reasons.
    """
    explanation_lines = []

    # Check for Critical Failure
    if final_grade == constants.GRADE_D:
        critical_reasons = [
            reason for attr, reason in reasons.items() 
            if sub_grades.get(attr) == constants.GRADE_D
        ]
        explanation_lines.append(f"Critical Failure: {'; '.join(critical_reasons)}")
        return explanation_lines

    # Compile general reasons
    for attr, reason in reasons.items():
        grade = sub_grades.get(attr)
        if grade in [constants.GRADE_C, constants.GRADE_D]:
            explanation_lines.append(f"Warning ({grade}): {reason}")
        else:
            explanation_lines.append(f"Passed ({grade}): {reason}")

    return explanation_lines

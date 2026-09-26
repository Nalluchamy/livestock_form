from typing import Dict, List
from backend.grading import constants


def generate_explanation(
    final_grade: str, 
    sub_grades: Dict[str, str], 
    reasons: Dict[str, str]
) -> List[str]:
    """
    Translates fired rules, component sub-grades, and clinical thresholds into an explainable audit log.

    Precedence Logic:
    - Critical Disqualification (Grade D): When an individual life-safety or disqualifying defect
      is detected (e.g. severe infection or deep rotting lesion), all secondary passing criteria
      are suppressed from the primary summary to ensure the inspector focuses immediately on the clinical hazard.
    - Tiered Explanations (Grades A/B/C): Formats individual criterion outcomes with explicit 'Passed' or
      'Warning' designations, attributing the final grade to specific visual factors.

    Args:
        final_grade: Overarching grade assigned by the rule engine.
        sub_grades: Dictionary mapping attribute keys to individual component grades.
        reasons: Dictionary mapping attribute keys to deterministic diagnostic statements.

    Returns:
        Ordered list of human-readable explanation strings suitable for UI display and audit logging.
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

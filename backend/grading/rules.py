"""
Defines the overarching rules for combining sub-grades into a final grade.
"""
from typing import List, Dict
from backend.grading import constants


def apply_critical_failure_rule(sub_grades: Dict[str, str]) -> bool:
    """If any attribute is Grade D, the overall grade is D."""
    return any(grade == constants.GRADE_D for grade in sub_grades.values())


def apply_warning_threshold_rule(sub_grades: Dict[str, str]) -> bool:
    """If two or more attributes are Grade C, the overall grade cannot exceed C."""
    c_count = sum(1 for grade in sub_grades.values() if grade == constants.GRADE_C)
    return c_count >= 2


def calculate_average_grade(sub_grades: Dict[str, str]) -> str:
    """Calculates the average numeric grade and rounds to the nearest letter."""
    if not sub_grades:
        return constants.GRADE_B  # Default if no data, though shouldn't happen with validators

    total = sum(constants.GRADE_NUMERIC_MAP[g] for g in sub_grades.values())
    avg = total / len(sub_grades)

    if avg <= 1.5:
        return constants.GRADE_A
    elif avg <= 2.5:
        return constants.GRADE_B
    elif avg <= 3.5:
        return constants.GRADE_C
    else:
        return constants.GRADE_D


def determine_final_grade(sub_grades: Dict[str, str]) -> str:
    """
    Applies the rule hierarchy to determine the final system grade.
    1. Critical Failure -> D
    2. Warning Threshold -> Max C (or worse if average dictates)
    3. Average Grade
    """
    if not sub_grades:
        raise ValueError("Cannot determine final grade with no attributes.")

    if apply_critical_failure_rule(sub_grades):
        return constants.GRADE_D

    avg_grade = calculate_average_grade(sub_grades)
    
    if apply_warning_threshold_rule(sub_grades):
        # Must be at least C (numeric 3). If avg_grade is A (1) or B (2), force to C.
        if constants.GRADE_NUMERIC_MAP[avg_grade] < constants.GRADE_NUMERIC_MAP[constants.GRADE_C]:
            return constants.GRADE_C

    return avg_grade

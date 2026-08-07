from typing import Dict, Any, Tuple
from backend.grading import rubric, rules


def evaluate_grading_rules(attributes: Dict[str, Any]) -> Tuple[str, Dict[str, str], Dict[str, str]]:
    """
    Orchestrates the evaluation of attributes through the rubric and rules.
    Returns:
        final_grade (str)
        sub_grades (Dict[attr_name, Grade])
        reasons (Dict[attr_name, plain_text_reason])
    """
    sub_grades = {}
    reasons = {}

    for attr_name, value in attributes.items():
        grade, reason = rubric.evaluate_attribute(attr_name, value)
        sub_grades[attr_name] = grade
        reasons[attr_name] = reason

    final_grade = rules.determine_final_grade(sub_grades)
    
    return final_grade, sub_grades, reasons

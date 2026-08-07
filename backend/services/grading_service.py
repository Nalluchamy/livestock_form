from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.grading import constants
from backend.services import validators, rule_engine, confidence, explanation


class GradingResult(BaseModel):
    grade: str
    confidence: float
    reasons: List[str]
    missing_attributes: List[str]
    review_required: bool


class Disagreement(BaseModel):
    human_grade: str
    system_grade: str
    reason: str
    review_required: bool = True


def generate_grade(
    attributes: Dict[str, Any], 
    has_image: bool = True
) -> GradingResult:
    """
    Main entry point for the Rule Engine grading pipeline.
    Validates input -> Runs rules -> Calculates confidence -> Generates explanations.
    """
    missing_attributes = validators.validate_attributes(attributes)
    
    # If all critical attributes are missing, we cannot grade
    if len(missing_attributes) == len(constants.ALL_ATTRIBUTES):
        raise ValueError("Cannot grade: No attributes provided.")

    final_grade, sub_grades, reasons_dict = rule_engine.evaluate_grading_rules(attributes)
    
    conf_score = confidence.calculate_confidence(sub_grades, missing_attributes, has_image)
    
    exp_lines = explanation.generate_explanation(final_grade, sub_grades, reasons_dict)

    # Determine if review is required inherently (e.g., very low confidence)
    review_req = conf_score < 50.0

    return GradingResult(
        grade=final_grade,
        confidence=conf_score,
        reasons=exp_lines,
        missing_attributes=missing_attributes,
        review_required=review_req
    )


def detect_disagreement(
    human_grade: str, 
    system_result: GradingResult
) -> Optional[Disagreement]:
    """
    Detects if a human grade contradicts the system grade.
    Returns a Disagreement object if they differ, else None.
    NEVER overrides the human grade.
    """
    if human_grade not in constants.ALL_GRADES:
        raise ValueError(f"Invalid human grade: {human_grade}")
        
    if human_grade != system_result.grade:
        return Disagreement(
            human_grade=human_grade,
            system_grade=system_result.grade,
            reason=f"Human graded {human_grade}, but system calculated {system_result.grade} based on rules.",
            review_required=True
        )
    return None

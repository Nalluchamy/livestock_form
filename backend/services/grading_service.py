from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel

from backend.grading import constants
from backend.services import validators, rule_engine, confidence, explanation


MANDATORY_VETERINARY_DISCLAIMER = (
    "Condition grade is an observational decision-support score, not a veterinary medical diagnosis. "
    "Urgent cases require immediate clinical examination by a licensed veterinarian."
)


class GradingResult(BaseModel):
    grade: str
    confidence: float
    reasons: List[str]
    missing_attributes: List[str]
    review_required: bool
    urgent_escalation: bool = False
    escalation_reasons: List[str] = []
    clinical_disclaimer: str = MANDATORY_VETERINARY_DISCLAIMER


class Disagreement(BaseModel):
    human_grade: str
    system_grade: str
    reason: str
    review_required: bool = True


def check_urgent_escalation(
    final_grade: str,
    attributes: Dict[str, Any],
    sub_grades: Dict[str, str]
) -> Tuple[bool, List[str]]:
    """
    Evaluates clinical safety triggers for immediate veterinary escalation:
    1. Overall Grade D
    2. Severe wounds / open lacerations / tissue necrosis
    3. Immobility / 'Unable to stand'
    4. Severe emaciation (BCS < 1.5) or morbid obesity (BCS > 4.5)
    5. Severe eye infection / blindness
    """
    reasons = []

    if final_grade == constants.GRADE_D:
        reasons.append("Overall health evaluated as Critical (Grade D).")

    wound = attributes.get(constants.ATTR_WOUND_PRESENCE)
    if wound == "Severe" or sub_grades.get(constants.ATTR_WOUND_PRESENCE) == "D":
        reasons.append("Severe external wounds or necrotic lesions detected.")

    mobility = attributes.get(constants.ATTR_MOBILITY)
    if mobility == "Unable to stand" or sub_grades.get(constants.ATTR_MOBILITY) == "D":
        reasons.append("Immobility / recumbent 'downer' condition detected.")

    bcs = attributes.get(constants.ATTR_BODY_CONDITION)
    if bcs is not None:
        try:
            bcs_val = float(bcs)
            if bcs_val < 1.5:
                reasons.append(f"Severe emaciation detected (BCS {bcs_val} < 1.5).")
            elif bcs_val > 4.5:
                reasons.append(f"Morbid obesity detected (BCS {bcs_val} > 4.5).")
        except (ValueError, TypeError):
            pass

    eye = attributes.get(constants.ATTR_EYE_CONDITION)
    if eye == "Severe infection" or sub_grades.get(constants.ATTR_EYE_CONDITION) == "D":
        reasons.append("Severe ocular infection or corneal perforation detected.")

    urgent = len(reasons) > 0
    return urgent, reasons


def generate_grade(
    attributes: Dict[str, Any], 
    has_image: bool = True
) -> GradingResult:
    """
    Main entry point for the Rule Engine grading pipeline.
    Validates input -> Runs rules -> Calculates confidence -> Evaluates urgent escalation -> Generates explanations.
    """
    missing_attributes = validators.validate_attributes(attributes)
    
    # If all critical attributes are missing, we cannot grade
    if len(missing_attributes) == len(constants.ALL_ATTRIBUTES):
        raise ValueError("Cannot grade: No attributes provided.")

    final_grade, sub_grades, reasons_dict = rule_engine.evaluate_grading_rules(attributes)
    
    conf_score = confidence.calculate_confidence(sub_grades, missing_attributes, has_image)
    
    exp_lines = explanation.generate_explanation(final_grade, sub_grades, reasons_dict)

    # Evaluate clinical escalation safety rules
    urgent, esc_reasons = check_urgent_escalation(final_grade, attributes, sub_grades)

    # Determine if review is required (low confidence or urgent escalation)
    review_req = (conf_score < 50.0) or urgent

    return GradingResult(
        grade=final_grade,
        confidence=conf_score,
        reasons=exp_lines,
        missing_attributes=missing_attributes,
        review_required=review_req,
        urgent_escalation=urgent,
        escalation_reasons=esc_reasons,
        clinical_disclaimer=MANDATORY_VETERINARY_DISCLAIMER
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

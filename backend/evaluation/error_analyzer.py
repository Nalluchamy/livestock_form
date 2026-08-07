"""
Error Taxonomy Analyzer.
Classifies prediction discrepancies into 5 categories.
"""
from typing import Dict, Any, List


def classify_error(attributes: Dict[str, Any], rule_grade: str, target_grade: str) -> str:
    """
    Classifies a prediction discrepancy into a standardized taxonomy category.
    """
    if rule_grade == target_grade:
        return "No Error"

    bcs = float(attributes.get("body_condition", 3.0))

    # 1. Borderline Case (e.g. BCS near threshold boundary)
    if bcs in [2.0, 2.5, 3.5, 4.0]:
        return "Borderline BCS Case"

    # 2. Missing Attributes
    required_keys = ["body_condition", "coat_quality", "eye_condition", "wound_presence", "mobility", "appetite"]
    if any(k not in attributes for k in required_keys):
        return "Missing Attributes"

    # 3. Rule Threshold Conflict
    if attributes.get("wound_presence") == "Moderate" and attributes.get("mobility") == "Slight limp":
        return "Rule Threshold Conflict"

    # 4. Expert Disagreement / Subjective Noise
    return "Expert Disagreement"


def analyze_errors(dataset_records: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Aggregates error counts across a dataset.
    """
    counts = {
        "Borderline BCS Case": 0,
        "Missing Attributes": 0,
        "Rule Threshold Conflict": 0,
        "Expert Disagreement": 0,
        "Poor Image Quality": 0,
    }

    for record in dataset_records:
        category = classify_error(
            record["attributes"],
            record["rule_grade"],
            record["target_grade"]
        )
        if category in counts:
            counts[category] += 1

    return counts

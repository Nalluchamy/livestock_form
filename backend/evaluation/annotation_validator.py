"""
Expert Annotation Validator & Inter-Annotator Agreement Calculator.
Enforces:
1. Double-blind annotation rules.
2. Disagreement preservation without automated artificial forced consensus.
3. Statistical metrics: Cohen's Kappa, Exact Match %, Adjacent Match %.
4. Graceful handling of missing or incomplete attributes.
"""
import os
import csv
import math
from typing import List, Dict, Any, Tuple, Optional
from pydantic import ValidationError

from backend.schemas.annotation import ExpertAnnotationSample, AnnotationBatchSummary
from backend.grading import constants


GRADE_TO_INT = {
    constants.GRADE_A: 1,
    constants.GRADE_B: 2,
    constants.GRADE_C: 3,
    constants.GRADE_D: 4,
}

INT_TO_GRADE = {v: k for k, v in GRADE_TO_INT.items()}


def compute_cohen_kappa(y1: List[str], y2: List[str], categories: Optional[List[str]] = None) -> float:
    """Computes unweighted Cohen's Kappa between two raters."""
    if len(y1) != len(y2) or len(y1) == 0:
        return 0.0

    if categories is None:
        categories = [constants.GRADE_A, constants.GRADE_B, constants.GRADE_C, constants.GRADE_D]

    n = len(y1)
    k = len(categories)
    cat_to_idx = {c: i for i, c in enumerate(categories)}

    matrix = [[0] * k for _ in range(k)]
    valid_pairs = 0
    for a, b in zip(y1, y2):
        if a in cat_to_idx and b in cat_to_idx:
            matrix[cat_to_idx[a]][cat_to_idx[b]] += 1
            valid_pairs += 1

    if valid_pairs == 0:
        return 0.0

    observed_acc = sum(matrix[i][i] for i in range(k)) / valid_pairs

    sum_row = [sum(matrix[i][j] for j in range(k)) for i in range(k)]
    sum_col = [sum(matrix[i][j] for i in range(k)) for j in range(k)]

    expected_acc = sum(sum_row[i] * sum_col[i] for i in range(k)) / (valid_pairs * valid_pairs)

    if expected_acc == 1.0:
        return 1.0

    kappa = (observed_acc - expected_acc) / (1.0 - expected_acc)
    return round(kappa, 4)


def compute_exact_agreement(y1: List[str], y2: List[str]) -> float:
    """Computes percentage of exact matching grades between two raters."""
    pairs = [(a, b) for a, b in zip(y1, y2) if a and b]
    if not pairs:
        return 0.0
    matches = sum(1 for a, b in pairs if a == b)
    return round((matches / len(pairs)) * 100.0, 2)


def compute_adjacent_agreement(y1: List[str], y2: List[str]) -> float:
    """Computes percentage of adjacent matching grades (e.g. A vs B, B vs C, diff <= 1)."""
    pairs = [(a, b) for a, b in zip(y1, y2) if a in GRADE_TO_INT and b in GRADE_TO_INT]
    if not pairs:
        return 0.0
    matches = sum(1 for a, b in pairs if abs(GRADE_TO_INT[a] - GRADE_TO_INT[b]) <= 1)
    return round((matches / len(pairs)) * 100.0, 2)


def validate_single_record(row: Dict[str, Any]) -> Tuple[Optional[ExpertAnnotationSample], List[str]]:
    """
    Parses a single dictionary into an ExpertAnnotationSample model.
    Returns (sample_object_or_none, errors_list).
    """
    errors = []
    # Handle body_condition conversion if string
    clean_row = dict(row)
    if "body_condition" in clean_row and clean_row["body_condition"]:
        try:
            clean_row["body_condition"] = float(clean_row["body_condition"])
        except ValueError:
            errors.append(f"Invalid body_condition number: '{clean_row['body_condition']}'")
            clean_row["body_condition"] = None
    else:
        clean_row["body_condition"] = None

    if "weight_if_available" in clean_row and clean_row["weight_if_available"]:
        try:
            clean_row["weight_if_available"] = float(clean_row["weight_if_available"])
        except ValueError:
            clean_row["weight_if_available"] = None
    else:
        clean_row["weight_if_available"] = None

    # Blank strings to None
    for field in ["expert_grade_1", "expert_grade_2", "final_consensus_grade", "image_path", 
                  "coat_quality", "eye_condition", "wound_presence", "mobility", "appetite"]:
        if field in clean_row and clean_row[field] == "":
            clean_row[field] = None

    # Determine status if not provided
    g1 = clean_row.get("expert_grade_1")
    g2 = clean_row.get("expert_grade_2")
    final_grade = clean_row.get("final_consensus_grade")
    
    status = clean_row.get("annotation_status", "PENDING")
    if not clean_row.get("annotation_status"):
        if g1 and g2:
            if g1 == g2:
                status = "CONSENSUS_REACHED"
                if not final_grade:
                    clean_row["final_consensus_grade"] = g1
            else:
                if final_grade:
                    status = "CONSENSUS_REACHED"
                else:
                    status = "DISAGREEMENT"
        elif g1 or g2:
            status = "PENDING"
        else:
            status = "INCOMPLETE"
    clean_row["annotation_status"] = status

    try:
        sample = ExpertAnnotationSample(**clean_row)
        return sample, errors
    except ValidationError as e:
        for err in e.errors():
            errors.append(f"Field '{err['loc'][0]}': {err['msg']}")
        return None, errors


def load_annotation_csv(csv_path: str) -> Tuple[List[ExpertAnnotationSample], List[str], AnnotationBatchSummary]:
    """
    Loads and validates a complete expert annotation CSV file.
    Returns (valid_samples, error_messages, summary_metrics).
    """
    if not os.path.exists(csv_path):
        summary = AnnotationBatchSummary(
            total_samples=0,
            complete_count=0,
            pending_count=0,
            disagreement_count=0,
            consensus_count=0,
            rejected_count=0
        )
        return [], [f"File not found: {csv_path}"], summary

    valid_samples: List[ExpertAnnotationSample] = []
    errors: List[str] = []

    with open(csv_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=2):
            sample, row_errors = validate_single_record(row)
            if row_errors:
                for err in row_errors:
                    errors.append(f"Line {line_num} (sample_id={row.get('sample_id', 'unknown')}): {err}")
            if sample:
                valid_samples.append(sample)

    # Compute inter-annotator metrics among samples having both expert_grade_1 and expert_grade_2
    dual_grades = [(s.expert_grade_1, s.expert_grade_2) for s in valid_samples if s.expert_grade_1 and s.expert_grade_2]
    
    g1_list = [p[0] for p in dual_grades]
    g2_list = [p[1] for p in dual_grades]

    kappa = compute_cohen_kappa(g1_list, g2_list) if len(g1_list) >= 5 else None
    exact_pct = compute_exact_agreement(g1_list, g2_list) if g1_list else None
    adj_pct = compute_adjacent_agreement(g1_list, g2_list) if g1_list else None

    complete_count = sum(1 for s in valid_samples if s.final_consensus_grade is not None)
    pending_count = sum(1 for s in valid_samples if s.annotation_status == "PENDING")
    disagreement_count = sum(1 for s in valid_samples if s.annotation_status == "DISAGREEMENT")
    consensus_count = sum(1 for s in valid_samples if s.annotation_status == "CONSENSUS_REACHED")
    rejected_count = sum(1 for s in valid_samples if s.annotation_status == "REJECTED")

    summary = AnnotationBatchSummary(
        total_samples=len(valid_samples),
        complete_count=complete_count,
        pending_count=pending_count,
        disagreement_count=disagreement_count,
        consensus_count=consensus_count,
        rejected_count=rejected_count,
        inter_expert_kappa=kappa,
        inter_expert_exact_match_pct=exact_pct,
        inter_expert_adjacent_match_pct=adj_pct,
    )

    return valid_samples, errors, summary

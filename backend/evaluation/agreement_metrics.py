"""
Agreement Metrics Evaluation Module for ELHGS.
Computes Cohen's Kappa, Exact Match %, and Adjacent-Tier Match %
across independent human graders, Rule Engine baseline, and Decision Tree ML advisory model.
"""
import os
import csv
import math
from typing import List, Dict, Tuple, Any

from backend.grading import rules, rubric, constants
from backend.ml.predict import predict_explainable_grade


def cohen_kappa(y1: List[str], y2: List[str], categories: List[str] = None) -> float:
    """
    Calculates unweighted Cohen's Kappa between two lists of categorical ratings.
    """
    if len(y1) != len(y2) or len(y1) == 0:
        return 0.0

    if categories is None:
        categories = sorted(list(set(y1) | set(y2)))

    n = len(y1)
    cat_to_idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)

    matrix = [[0] * k for _ in range(k)]
    for a, b in zip(y1, y2):
        matrix[cat_to_idx[a]][cat_to_idx[b]] += 1

    observed_acc = sum(matrix[i][i] for i in range(k)) / n

    sum_row = [sum(matrix[i][j] for j in range(k)) for i in range(k)]
    sum_col = [sum(matrix[i][j] for i in range(k)) for j in range(k)]

    expected_acc = sum(sum_row[i] * sum_col[i] for i in range(k)) / (n * n)

    if expected_acc == 1.0:
        return 1.0

    kappa = (observed_acc - expected_acc) / (1.0 - expected_acc)
    return round(kappa, 4)


def exact_match_percentage(y1: List[str], y2: List[str]) -> float:
    """Calculates percentage of exact matching grades."""
    if not y1:
        return 0.0
    matches = sum(1 for a, b in zip(y1, y2) if a == b)
    return round((matches / len(y1)) * 100.0, 2)


def adjacent_match_percentage(y1: List[str], y2: List[str]) -> float:
    """
    Calculates percentage of exact OR adjacent matching grades (e.g. A vs B, B vs C).
    """
    if not y1:
        return 0.0
    grade_map = {constants.GRADE_A: 1, constants.GRADE_B: 2, constants.GRADE_C: 3, constants.GRADE_D: 4}
    
    matches = 0
    for a, b in zip(y1, y2):
        v1 = grade_map.get(a, 0)
        v2 = grade_map.get(b, 0)
        if abs(v1 - v2) <= 1:
            matches += 1
            
    return round((matches / len(y1)) * 100.0, 2)


def compute_consensus(g1: str, g2: str) -> str:
    """Computes consensus grade between 2 human graders."""
    if g1 == g2:
        return g1
    grade_map = {constants.GRADE_A: 1, constants.GRADE_B: 2, constants.GRADE_C: 3, constants.GRADE_D: 4}
    rev_map = {1: constants.GRADE_A, 2: constants.GRADE_B, 3: constants.GRADE_C, 4: constants.GRADE_D}
    avg = math.ceil((grade_map[g1] + grade_map[g2]) / 2.0)
    return rev_map[avg]


def evaluate_validation_dataset(data_dir: str = None) -> Dict[str, Any]:
    """
    Loads validation dataset and evaluates Human vs Rule Engine vs Decision Tree ML.
    """
    if data_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(base_dir, "data", "validation_set")

    attr_path = os.path.join(data_dir, "attributes.csv")
    g1_path = os.path.join(data_dir, "grader_1.csv")
    g2_path = os.path.join(data_dir, "grader_2.csv")

    if not (os.path.exists(attr_path) and os.path.exists(g1_path) and os.path.exists(g2_path)):
        raise FileNotFoundError(f"Validation dataset CSV files not found in {data_dir}")

    # Load Attributes
    samples = []
    with open(attr_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["body_condition"] = float(row["body_condition"])
            samples.append(row)

    # Load Grader 1
    grader_1_map = {}
    with open(g1_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grader_1_map[row["sample_id"]] = row["human_grade"]

    # Load Grader 2
    grader_2_map = {}
    with open(g2_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            grader_2_map[row["sample_id"]] = row["human_grade"]

    # CSV Alignment Sanity Check (Fail Loudly if misaligned)
    attr_ids = set(s["sample_id"] for s in samples)
    g1_ids = set(grader_1_map.keys())
    g2_ids = set(grader_2_map.keys())

    if not (attr_ids == g1_ids == g2_ids) or not (len(samples) == len(grader_1_map) == len(grader_2_map)):
        raise ValueError(
            f"CSV Alignment Mismatch! "
            f"attributes.csv N={len(samples)}, grader_1.csv N={len(grader_1_map)}, grader_2.csv N={len(grader_2_map)}. "
            f"Sample ID discrepancies: attr-g1={attr_ids ^ g1_ids}, attr-g2={attr_ids ^ g2_ids}"
        )


    g1_list = []
    g2_list = []
    consensus_list = []
    rule_engine_list = []
    dt_ml_list = []

    categories = [constants.GRADE_A, constants.GRADE_B, constants.GRADE_C, constants.GRADE_D]

    for sample in samples:
        s_id = sample["sample_id"]
        g1 = grader_1_map[s_id]
        g2 = grader_2_map[s_id]
        cons = compute_consensus(g1, g2)

        g1_list.append(g1)
        g2_list.append(g2)
        consensus_list.append(cons)

        # Rule Engine evaluation
        attr_dict = {
            constants.ATTR_BODY_CONDITION: sample["body_condition"],
            constants.ATTR_COAT_QUALITY: sample["coat_quality"],
            constants.ATTR_EYE_CONDITION: sample["eye_condition"],
            constants.ATTR_WOUND_PRESENCE: sample["wound_presence"],
            constants.ATTR_MOBILITY: sample["mobility"],
            constants.ATTR_APPETITE: sample["appetite"],
        }
        sub_grades = {}
        for k, v in attr_dict.items():
            sub_g, _ = rubric.evaluate_attribute(k, v)
            sub_grades[k] = sub_g
        
        re_grade = rules.determine_final_grade(sub_grades)
        rule_engine_list.append(re_grade)

        # Decision Tree ML evaluation
        dt_pred = predict_explainable_grade(attr_dict, model_name="Decision Tree")
        dt_ml_list.append(dt_pred["grade"])

    # Compute Metrics
    metrics = {
        "dataset_info": {
            "total_samples": len(samples),
            "source": "data/validation_set/",
            "provenance": "[measured, N=32, real validation set]"
        },
        "human_baseline": {
            "cohen_kappa": cohen_kappa(g1_list, g2_list, categories),
            "exact_match_pct": exact_match_percentage(g1_list, g2_list),
            "adjacent_match_pct": adjacent_match_percentage(g1_list, g2_list),
        },
        "rule_engine_vs_consensus": {
            "cohen_kappa": cohen_kappa(rule_engine_list, consensus_list, categories),
            "exact_match_pct": exact_match_percentage(rule_engine_list, consensus_list),
            "adjacent_match_pct": adjacent_match_percentage(rule_engine_list, consensus_list),
        },
        "decision_tree_ml_vs_consensus": {
            "cohen_kappa": cohen_kappa(dt_ml_list, consensus_list, categories),
            "exact_match_pct": exact_match_percentage(dt_ml_list, consensus_list),
            "adjacent_match_pct": adjacent_match_percentage(dt_ml_list, consensus_list),
        },
        "decision_tree_ml_vs_grader_1": {
            "cohen_kappa": cohen_kappa(dt_ml_list, g1_list, categories),
            "exact_match_pct": exact_match_percentage(dt_ml_list, g1_list),
            "adjacent_match_pct": adjacent_match_percentage(dt_ml_list, g1_list),
        },
        "decision_tree_ml_vs_grader_2": {
            "cohen_kappa": cohen_kappa(dt_ml_list, g2_list, categories),
            "exact_match_pct": exact_match_percentage(dt_ml_list, g2_list),
            "adjacent_match_pct": adjacent_match_percentage(dt_ml_list, g2_list),
        }
    }

    return metrics


if __name__ == "__main__":
    res = evaluate_validation_dataset()
    import json
    print(json.dumps(res, indent=2))

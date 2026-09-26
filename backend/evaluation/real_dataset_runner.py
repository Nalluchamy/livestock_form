"""
Real Dataset Evaluation Runner for ELHGS.
Evaluates Rule Engine, Decision Tree, and Logistic Regression models against
genuine expert consensus labels on held-out test splits.

Strictly distinguishes:
- Human-vs-Human baseline agreement
- System-vs-Expert agreement
- Human-vs-System disagreement
- Actual human-assisted dispute reduction (distinguished from simulated trials)

If genuine real data is unavailable, returns explicit 'PENDING_REAL_DATA' status
without fabricating results.
"""
import os
import csv
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, 
    precision_score, 
    recall_score, 
    f1_score, 
    confusion_matrix
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression

from backend.grading import constants, rubric, rules
from backend.ml.feature_engineering import preprocess_dataframe, FEATURE_COLUMNS
from backend.evaluation.annotation_validator import (
    load_annotation_csv, 
    compute_cohen_kappa, 
    compute_exact_agreement, 
    compute_adjacent_agreement
)
from backend.evaluation.dataset_splitter import split_dataset_group_aware
from backend.services.confidence import calculate_confidence
from backend.models.experiment_result import ExperimentResult
from backend.repositories.experiment_repository import ExperimentRepository


DEFAULT_REAL_LABELS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "dataset", "real", "labels", "annotations.csv"
)

CATEGORIES = [constants.GRADE_A, constants.GRADE_B, constants.GRADE_C, constants.GRADE_D]


def evaluate_model_predictions(
    y_true: List[str], 
    y_pred: List[str], 
    confidences: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Computes rigorous classification and agreement metrics.
    """
    if not y_true or not y_pred or len(y_true) != len(y_pred):
        return {
            "accuracy": 0.0,
            "macro_precision": 0.0,
            "macro_recall": 0.0,
            "macro_f1": 0.0,
            "cohen_kappa": 0.0,
            "exact_agreement_pct": 0.0,
            "adjacent_agreement_pct": 0.0,
            "confusion_matrix": {},
            "confidence_stats": {}
        }

    acc = round(accuracy_score(y_true, y_pred) * 100.0, 2)
    prec = round(precision_score(y_true, y_pred, labels=CATEGORIES, average="macro", zero_division=0) * 100.0, 2)
    rec = round(recall_score(y_true, y_pred, labels=CATEGORIES, average="macro", zero_division=0) * 100.0, 2)
    f1 = round(f1_score(y_true, y_pred, labels=CATEGORIES, average="macro", zero_division=0) * 100.0, 2)
    kappa = compute_cohen_kappa(y_pred, y_true, CATEGORIES)
    exact_match = compute_exact_agreement(y_pred, y_true)
    adj_match = compute_adjacent_agreement(y_pred, y_true)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=CATEGORIES).tolist()
    cm_dict = {
        CATEGORIES[i]: {CATEGORIES[j]: cm[i][j] for j in range(len(CATEGORIES))}
        for i in range(len(CATEGORIES))
    }

    # Confidence distribution stats
    conf_stats = {}
    if confidences:
        conf_arr = np.array(confidences)
        conf_stats = {
            "mean": round(float(np.mean(conf_arr)), 2),
            "median": round(float(np.median(conf_arr)), 2),
            "min": round(float(np.min(conf_arr)), 2),
            "max": round(float(np.max(conf_arr)), 2),
            "under_50_pct_count": int(np.sum(conf_arr < 50.0)),
            "under_70_pct_count": int(np.sum(conf_arr < 70.0)),
        }

    return {
        "accuracy": acc,
        "macro_precision": prec,
        "macro_recall": rec,
        "macro_f1": f1,
        "cohen_kappa": kappa,
        "exact_agreement_pct": exact_match,
        "adjacent_agreement_pct": adj_match,
        "confusion_matrix": cm_dict,
        "confidence_stats": conf_stats
    }


def predict_rule_engine_row(row: Dict[str, Any]) -> Tuple[str, float]:
    """Evaluates a single attribute dictionary through the deterministic Rule Engine."""
    attr_dict = {
        constants.ATTR_BODY_CONDITION: row.get("body_condition", 3.0),
        constants.ATTR_COAT_QUALITY: row.get("coat_quality", "Smooth"),
        constants.ATTR_EYE_CONDITION: row.get("eye_condition", "Clear"),
        constants.ATTR_WOUND_PRESENCE: row.get("wound_presence", "None"),
        constants.ATTR_MOBILITY: row.get("mobility", "Normal"),
        constants.ATTR_APPETITE: row.get("appetite", "Good"),
    }
    sub_grades = {}
    missing = []
    for k, v in attr_dict.items():
        if v is None:
            missing.append(k)
            continue
        try:
            sub_g, _ = rubric.evaluate_attribute(k, v)
            sub_grades[k] = sub_g
        except Exception:
            missing.append(k)

    final_grade = rules.determine_final_grade(sub_grades)
    confidence = calculate_confidence(sub_grades, missing, has_image=bool(row.get("image_path")))
    return final_grade, confidence


def run_real_evaluation(
    labels_csv_path: Optional[str] = None,
    experiment_name: str = "retrospective_real_dataset_run",
    db_session=None
) -> Dict[str, Any]:
    """
    Main execution pipeline for evaluating models on genuine real data.
    If genuine real data with expert consensus is not available, returns PENDING_REAL_DATA.
    """
    csv_path = labels_csv_path or DEFAULT_REAL_LABELS_PATH

    # Check if real labels CSV exists and has samples
    if not os.path.exists(csv_path):
        result = {
            "status": "PENDING_REAL_DATA",
            "message": "Real-world evaluation pending genuine expert-labeled dataset. Labels CSV not found.",
            "evaluation_type": "retrospective_real",
            "dataset_info": {"path": csv_path, "total_samples": 0},
            "performance_metrics": {},
            "expert_agreement_metrics": {},
            "actual_human_assisted_dispute_reduction": "Not yet measured (Field trial pending)"
        }
        if db_session:
            repo = ExperimentRepository(db_session)
            exp = ExperimentResult(
                experiment_name=experiment_name,
                dataset_version="real-pending",
                model_version="rule-v1.0+dt-v1.0",
                evaluation_type="retrospective_real",
                status="pending_real_data",
                dataset_sample_count=0,
                test_sample_count=0,
                performance_metrics={},
                expert_agreement_metrics={},
                confidence_distribution={},
                error_category_counts={},
                notes="Real dataset labels not found; pending field collection."
            )
            repo.save_experiment_result(exp)
        return result

    samples, errors, batch_summary = load_annotation_csv(csv_path)

    # Filter samples that have a valid ground truth consensus grade
    consensus_samples = [s.model_dump() for s in samples if s.final_consensus_grade is not None]

    if len(consensus_samples) < 10:
        result = {
            "status": "PENDING_REAL_DATA",
            "message": f"Real-world evaluation pending: Insufficient expert-consensus samples (found {len(consensus_samples)}, minimum required: 10).",
            "evaluation_type": "retrospective_real",
            "dataset_info": {"path": csv_path, "total_samples": len(samples), "consensus_samples": len(consensus_samples)},
            "batch_summary": batch_summary.model_dump(),
            "performance_metrics": {},
            "expert_agreement_metrics": {
                "human_baseline_kappa": batch_summary.inter_expert_kappa,
                "human_baseline_exact_pct": batch_summary.inter_expert_exact_match_pct,
            },
            "actual_human_assisted_dispute_reduction": "Not yet measured (Field trial pending)"
        }
        return result

    # 1. Leakage-safe Group Splitting
    split_res = split_dataset_group_aware(consensus_samples, target_ratios=(0.70, 0.15, 0.15), random_seed=42)
    train_data = split_res["train"]
    test_data = split_res["test"]

    # 2. Fit ML models on train data only
    train_df = pd.DataFrame(train_data)
    test_df = pd.DataFrame(test_data)

    X_train_raw = train_df[["body_condition", "coat_quality", "eye_condition", "wound_presence", "mobility", "appetite"]]
    y_train = train_df["final_consensus_grade"]
    X_train = preprocess_dataframe(X_train_raw)

    X_test_raw = test_df[["body_condition", "coat_quality", "eye_condition", "wound_presence", "mobility", "appetite"]]
    y_test = list(test_df["final_consensus_grade"])
    X_test = preprocess_dataframe(X_test_raw)

    # Train Decision Tree
    dt = DecisionTreeClassifier(max_depth=5, random_state=42)
    dt.fit(X_train, y_train)
    dt_preds = list(dt.predict(X_test))

    # Train Logistic Regression
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    lr_preds = list(lr.predict(X_test))

    # 3. Evaluate Rule Engine on held-out test data
    re_preds = []
    re_confidences = []
    for s in test_data:
        g, c = predict_rule_engine_row(s)
        re_preds.append(g)
        re_confidences.append(c)

    # 4. Compute Metrics on Held-out Test Split
    rule_metrics = evaluate_model_predictions(y_test, re_preds, re_confidences)
    dt_metrics = evaluate_model_predictions(y_test, dt_preds)
    lr_metrics = evaluate_model_predictions(y_test, lr_preds)

    # 5. Inter-Human Baseline on Test Split
    test_g1 = [s.get("expert_grade_1") for s in test_data if s.get("expert_grade_1") and s.get("expert_grade_2")]
    test_g2 = [s.get("expert_grade_2") for s in test_data if s.get("expert_grade_1") and s.get("expert_grade_2")]
    human_baseline = {
        "cohen_kappa": compute_cohen_kappa(test_g1, test_g2) if test_g1 else None,
        "exact_agreement_pct": compute_exact_agreement(test_g1, test_g2) if test_g1 else None,
        "adjacent_agreement_pct": compute_adjacent_agreement(test_g1, test_g2) if test_g1 else None,
    }

    # Error breakdown on Rule Engine
    error_counts = {
        "borderline_bcs": 0,
        "missing_attributes": 0,
        "sub_grade_conflict": 0,
        "total_disagreements": sum(1 for yt, yp in zip(y_test, re_preds) if yt != yp)
    }
    for s, yt, yp in zip(test_data, y_test, re_preds):
        if yt != yp:
            bcs = s.get("body_condition")
            if bcs and (abs(bcs - 2.5) <= 0.2 or abs(bcs - 3.5) <= 0.2):
                error_counts["borderline_bcs"] += 1
            if any(s.get(k) is None for k in ["coat_quality", "eye_condition", "wound_presence"]):
                error_counts["missing_attributes"] += 1

    performance_metrics = {
        "rule_engine": rule_metrics,
        "decision_tree": dt_metrics,
        "logistic_regression": lr_metrics,
    }

    expert_agreement_metrics = {
        "human_baseline_inter_rater": human_baseline,
        "rule_engine_vs_consensus": {
            "cohen_kappa": rule_metrics["cohen_kappa"],
            "exact_agreement_pct": rule_metrics["exact_agreement_pct"],
            "adjacent_agreement_pct": rule_metrics["adjacent_agreement_pct"]
        },
        "decision_tree_vs_consensus": {
            "cohen_kappa": dt_metrics["cohen_kappa"],
            "exact_agreement_pct": dt_metrics["exact_agreement_pct"],
            "adjacent_agreement_pct": dt_metrics["adjacent_agreement_pct"]
        },
        "logistic_regression_vs_consensus": {
            "cohen_kappa": lr_metrics["cohen_kappa"],
            "exact_agreement_pct": lr_metrics["exact_agreement_pct"],
            "adjacent_agreement_pct": lr_metrics["adjacent_agreement_pct"]
        }
    }

    result = {
        "status": "COMPLETED",
        "evaluation_type": "retrospective_real",
        "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_sample_count": len(consensus_samples),
        "test_sample_count": len(test_data),
        "performance_metrics": performance_metrics,
        "expert_agreement_metrics": expert_agreement_metrics,
        "confidence_distribution": rule_metrics["confidence_stats"],
        "error_category_counts": error_counts,
        "split_counts": split_res["counts"],
        "split_limitations": split_res["limitations_warnings"],
        "actual_human_assisted_dispute_reduction": "Requires prospective randomized field cohort study to measure",
        "notes": "Retrospective evaluation strictly on held-out test split with genuine expert annotations."
    }

    # Persist to database if db_session is provided
    if db_session:
        repo = ExperimentRepository(db_session)
        exp = ExperimentResult(
            experiment_name=experiment_name,
            dataset_version="real-v1.0",
            model_version="rule-v1.0+dt-v1.0+lr-v1.0",
            evaluation_type="retrospective_real",
            status="completed",
            dataset_sample_count=len(consensus_samples),
            test_sample_count=len(test_data),
            performance_metrics=performance_metrics,
            expert_agreement_metrics=expert_agreement_metrics,
            confidence_distribution=rule_metrics["confidence_stats"],
            error_category_counts=error_counts,
            notes="Retrospective evaluation on held-out test split."
        )
        repo.save_experiment_result(exp)

    return result


if __name__ == "__main__":
    res = run_real_evaluation()
    print(json.dumps(res, indent=2))

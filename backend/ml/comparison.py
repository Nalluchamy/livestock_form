"""
Three-Way Comparison Module.
Compares Rule Engine vs Decision Tree vs Logistic Regression against ground truth expert labels.
"""
import time
import pandas as pd
from typing import Dict, Any

from backend.ml.dataset_loader import load_dataset
from backend.ml.feature_engineering import preprocess_dataframe
from backend.ml import model_registry, evaluation
from backend.services import grading_service


def run_three_way_comparison() -> Dict[str, Any]:
    """
    Evaluates Rule Engine, Decision Tree, and Logistic Regression on the test dataset.
    """
    print("Running 3-way comparative evaluation...")
    X_raw, y_expert = load_dataset()

    dt_model, _ = model_registry.load_model("Decision Tree")
    lr_model, _ = model_registry.load_model("Logistic Regression")
    X_enc = preprocess_dataframe(X_raw)

    rule_preds = []
    t0 = time.time()
    for _, row in X_raw.iterrows():
        attrs = row.to_dict()
        res = grading_service.generate_grade(attrs, has_image=True)
        rule_preds.append(res.grade)
    rule_time = (time.time() - t0) * 1000.0 / len(X_raw)

    t0 = time.time()
    dt_preds = dt_model.predict(X_enc)
    dt_time = (time.time() - t0) * 1000.0 / len(X_raw)

    t0 = time.time()
    lr_preds = lr_model.predict(X_enc)
    lr_time = (time.time() - t0) * 1000.0 / len(X_raw)

    rule_metrics = evaluation.calculate_metrics(y_expert, rule_preds)
    dt_metrics = evaluation.calculate_metrics(y_expert, dt_preds)
    lr_metrics = evaluation.calculate_metrics(y_expert, lr_preds)

    disagreement_count = sum(1 for r, d in zip(rule_preds, dt_preds) if r != d)

    summary = {
        "dataset_size": len(X_raw),
        "rule_engine": {
            **rule_metrics,
            "avg_prediction_time_ms": round(rule_time, 3)
        },
        "decision_tree": {
            **dt_metrics,
            "avg_prediction_time_ms": round(dt_time, 3)
        },
        "logistic_regression": {
            **lr_metrics,
            "avg_prediction_time_ms": round(lr_time, 3)
        },
        "rule_vs_dt_disagreement_count": disagreement_count,
        "rule_vs_dt_disagreement_rate": round((disagreement_count / len(X_raw)) * 100, 1)
    }

    return summary


if __name__ == "__main__":
    report = run_three_way_comparison()
    print("\n================ Comparative Report ================")
    print(f"Dataset Size: {report['dataset_size']}")
    print(f"Rule Engine Accuracy: {report['rule_engine']['accuracy']}%")
    print(f"Decision Tree Accuracy: {report['decision_tree']['accuracy']}%")
    print(f"Logistic Regression Accuracy: {report['logistic_regression']['accuracy']}%")
    print(f"Disagreement Rate (Rule vs Decision Tree): {report['rule_vs_dt_disagreement_rate']}%")

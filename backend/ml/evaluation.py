"""
Model Evaluation metrics calculator.
Calculates Accuracy, Precision, Recall, F1, Cohen's Kappa, and Confusion Matrix.
"""
from typing import Dict, Any, List
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    cohen_kappa_score,
    confusion_matrix
)

from backend.grading import constants


def calculate_metrics(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    """
    Computes detailed evaluation metrics for multi-class classification.
    """
    labels = sorted(list(constants.ALL_GRADES))

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, average="weighted", zero_division=0)
    rec = recall_score(y_true, y_pred, average="weighted", zero_division=0)
    f1 = f1_score(y_true, y_pred, average="weighted", zero_division=0)
    kappa = cohen_kappa_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=labels)

    return {
        "accuracy": round(float(acc) * 100, 2),
        "precision": round(float(prec) * 100, 2),
        "recall": round(float(rec) * 100, 2),
        "f1_score": round(float(f1) * 100, 2),
        "cohen_kappa": round(float(kappa), 3),
        "confusion_matrix": cm.tolist(),
        "labels": labels
    }

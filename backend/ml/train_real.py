"""
Model Training & Evaluation Pipeline for Real Livestock Consensus Dataset.
Trains structured-attribute Decision Tree and Logistic Regression models
on genuine consensus data with leakage-safe held-out testing.
"""
import os
import json
import time
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timezone
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from backend.ml.feature_engineering import preprocess_dataframe, FEATURE_COLUMNS
from backend.ml import model_registry
from backend.evaluation.dataset_splitter import split_dataset_group_aware
from backend.evaluation.agreement_metrics import cohen_kappa, exact_match_percentage, adjacent_match_percentage
from backend.database.connection import SessionLocal
from backend.models.expert_annotation import ExpertAnnotation
from backend.repositories.experiment_repository import ExperimentRepository


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REAL_DATASET_DIR = os.path.join(BASE_DIR, "dataset", "real")
SPLITS_DIR = os.path.join(REAL_DATASET_DIR, "splits")
TRAIN_SPLIT_CSV = os.path.join(SPLITS_DIR, "train.csv")
TEST_SPLIT_CSV = os.path.join(SPLITS_DIR, "test.csv")


def load_consensus_data_from_db_or_csv() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads training and test consensus samples from splits CSVs or active DB records.
    Returns (train_df, test_df).
    """
    # 1. First preference: check if group-aware splits exist on disk
    if os.path.exists(TRAIN_SPLIT_CSV) and os.path.exists(TEST_SPLIT_CSV):
        try:
            train_df = pd.read_csv(TRAIN_SPLIT_CSV)
            test_df = pd.read_csv(TEST_SPLIT_CSV)
            if len(train_df) > 0 and len(test_df) > 0:
                return train_df, test_df
        except Exception:
            pass

    # 2. Fallback: Query ExpertAnnotation table
    db = SessionLocal()
    try:
        annotations = db.query(ExpertAnnotation).filter(
            ExpertAnnotation.final_consensus_grade.is_not(None),
            ExpertAnnotation.quality_flagged == False
        ).all()

        if not annotations:
            return pd.DataFrame(), pd.DataFrame()

        rows = []
        for a in annotations:
            rows.append({
                "sample_id": a.sample_id,
                "group_id": a.sample_id.split("-")[0] if "-" in a.sample_id else a.sample_id,
                "body_condition": a.body_condition if a.body_condition is not None else 3.0,
                "coat_quality": a.coat_quality or "Smooth",
                "eye_condition": a.eye_condition or "Clear",
                "wound_presence": a.wound_presence or "None",
                "mobility": a.mobility or "Normal",
                "appetite": a.appetite or "Good",
                "final_consensus_grade": a.final_consensus_grade
            })

        all_df = pd.DataFrame(rows)
        if len(all_df) < 10:
            return all_df, pd.DataFrame()

        # Split group-aware
        split_dict = split_dataset_group_aware(rows, target_ratios=(0.7, 0.15, 0.15))
        train_df = pd.DataFrame(split_dict["train"] + split_dict["val"])
        test_df = pd.DataFrame(split_dict["test"])
        return train_df, test_df

    finally:
        db.close()


def train_and_evaluate_real_models(
    experiment_name: str = "real_consensus_model_eval",
    dataset_version: str = "v1.0.0-real"
) -> Dict[str, Any]:
    """
    Trains models on real consensus dataset. If insufficient samples (<10),
    gracefully marks status as PENDING_REAL_DATA without fabricating results.
    """
    train_df, test_df = load_consensus_data_from_db_or_csv()
    total_samples = len(train_df) + len(test_df)

    db = SessionLocal()
    exp_repo = ExperimentRepository(db)

    try:
        if total_samples < 10 or len(test_df) == 0:
            status_info = {
                "status": "PENDING_REAL_DATA",
                "message": f"Real model training deferred. Found {total_samples} consensus samples (< 10 required for statistically valid validation).",
                "total_consensus_samples": total_samples,
                "trained": False,
                "models": {}
            }

            # Record pending experiment in DB
            exp_repo.create_experiment_result(
                experiment_name=experiment_name,
                dataset_version=dataset_version,
                evaluation_type="retrospective_real",
                metrics_summary={
                    "status": "PENDING_REAL_DATA",
                    "sample_count": total_samples,
                    "reason": "Insufficient field consensus samples"
                }
            )
            return status_info

        # Preprocess features
        X_train_raw = train_df[["body_condition", "coat_quality", "eye_condition", "wound_presence", "mobility", "appetite"]]
        y_train = train_df["final_consensus_grade"].astype(str).str.upper()

        X_test_raw = test_df[["body_condition", "coat_quality", "eye_condition", "wound_presence", "mobility", "appetite"]]
        y_test = test_df["final_consensus_grade"].astype(str).str.upper()

        X_train = preprocess_dataframe(X_train_raw)
        X_test = preprocess_dataframe(X_test_raw)

        # 1. Decision Tree Model
        dt = DecisionTreeClassifier(max_depth=4, random_state=42)
        dt.fit(X_train, y_train)
        dt_preds = dt.predict(X_test)
        dt_path = model_registry.save_model(dt, "Decision Tree (Real)", is_real=True)

        dt_acc = float(accuracy_score(y_test, dt_preds))
        dt_f1 = float(f1_score(y_test, dt_preds, average="macro", zero_division=0))
        dt_prec = float(precision_score(y_test, dt_preds, average="macro", zero_division=0))
        dt_rec = float(recall_score(y_test, dt_preds, average="macro", zero_division=0))
        dt_kappa = float(cohen_kappa(list(y_test), list(dt_preds)))
        dt_exact = float(exact_match_percentage(list(y_test), list(dt_preds)))
        dt_adj = float(adjacent_match_percentage(list(y_test), list(dt_preds)))

        # 2. Logistic Regression Model
        lr = LogisticRegression(max_iter=1000, random_state=42)
        lr.fit(X_train, y_train)
        lr_preds = lr.predict(X_test)
        lr_path = model_registry.save_model(lr, "Logistic Regression (Real)", is_real=True)

        lr_acc = float(accuracy_score(y_test, lr_preds))
        lr_f1 = float(f1_score(y_test, lr_preds, average="macro", zero_division=0))
        lr_prec = float(precision_score(y_test, lr_preds, average="macro", zero_division=0))
        lr_rec = float(recall_score(y_test, lr_preds, average="macro", zero_division=0))
        lr_kappa = float(cohen_kappa(list(y_test), list(lr_preds)))
        lr_exact = float(exact_match_percentage(list(y_test), list(lr_preds)))
        lr_adj = float(adjacent_match_percentage(list(y_test), list(lr_preds)))

        metrics_summary = {
            "status": "COMPLETED",
            "dataset_version": dataset_version,
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "decision_tree": {
                "accuracy": round(dt_acc, 4),
                "macro_precision": round(dt_prec, 4),
                "macro_recall": round(dt_rec, 4),
                "macro_f1": round(dt_f1, 4),
                "cohen_kappa": round(dt_kappa, 4),
                "exact_match_pct": round(dt_exact, 2),
                "adjacent_match_pct": round(dt_adj, 2),
                "model_artifact": dt_path
            },
            "logistic_regression": {
                "accuracy": round(lr_acc, 4),
                "macro_precision": round(lr_prec, 4),
                "macro_recall": round(lr_rec, 4),
                "macro_f1": round(lr_f1, 4),
                "cohen_kappa": round(lr_kappa, 4),
                "exact_match_pct": round(lr_exact, 2),
                "adjacent_match_pct": round(lr_adj, 2),
                "model_artifact": lr_path
            }
        }

        exp_repo.create_experiment_result(
            experiment_name=experiment_name,
            dataset_version=dataset_version,
            evaluation_type="retrospective_real",
            metrics_summary=metrics_summary
        )

        return {
            "status": "COMPLETED",
            "message": "Real models trained and evaluated on held-out test consensus split.",
            "trained": True,
            "metrics": metrics_summary
        }

    finally:
        db.close()


if __name__ == "__main__":
    res = train_and_evaluate_real_models()
    print(json.dumps(res, indent=2))

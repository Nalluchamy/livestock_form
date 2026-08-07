"""
Explainable Prediction Engine.
Extracts decision paths, feature importances, and coefficient contributions.
"""
import time
from typing import Dict, Any, List
import numpy as np

from backend.ml import model_registry
from backend.ml.feature_engineering import preprocess_single_input, FEATURE_COLUMNS


def predict_explainable_grade(
    attributes: Dict[str, Any], 
    model_name: str = "Decision Tree"
) -> Dict[str, Any]:
    """
    Executes inference and returns prediction, confidence score, and explainable feature importances.
    """
    start_time = time.time()

    model, meta = model_registry.load_model(model_name)
    feature_vector = preprocess_single_input(attributes)

    # Prediction & Probabilities
    predicted_grade = model.predict(feature_vector)[0]
    probabilities = model.predict_proba(feature_vector)[0]
    confidence = float(np.max(probabilities) * 100.0)

    # Explainability Extraction
    top_features = []
    explanations = []

    if "decision" in model_name.lower():
        # Extract Decision Tree Feature Importances
        importances = model.feature_importances_
        sorted_indices = np.argsort(importances)[::-1]
        
        for idx in sorted_indices:
            feat_name = FEATURE_COLUMNS[idx].replace("_enc", "").replace("_", " ").capitalize()
            imp_val = float(importances[idx])
            if imp_val > 0.05:
                top_features.append(feat_name)
                explanations.append(f"{feat_name} contributed {imp_val * 100:.1f}% to decision tree split.")

    else:
        # Extract Logistic Regression Coefficients for predicted class
        class_idx = list(model.classes_).index(predicted_grade)
        coefs = model.coef_[class_idx]
        sorted_indices = np.argsort(np.abs(coefs))[::-1]

        for idx in sorted_indices:
            feat_name = FEATURE_COLUMNS[idx].replace("_enc", "").replace("_", " ").capitalize()
            coef_val = float(coefs[idx])
            top_features.append(feat_name)
            explanations.append(f"{feat_name} coefficient weight ({coef_val:+.2f}) for Grade {predicted_grade}.")

    exec_time_ms = (time.time() - start_time) * 1000.0

    return {
        "model": meta["model_name"],
        "grade": predicted_grade,
        "confidence": round(confidence, 1),
        "top_features": top_features[:3],
        "explanations": explanations[:3],
        "prediction_time_ms": round(exec_time_ms, 2)
    }

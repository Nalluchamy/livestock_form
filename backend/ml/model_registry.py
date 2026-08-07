"""
Model Registry for managing serialized joblib artifacts and metadata.
"""
import os
import joblib
from datetime import datetime
from typing import Dict, Any, Tuple

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")

DECISION_TREE_PATH = os.path.join(MODELS_DIR, "decision_tree.joblib")
LOGISTIC_REGRESSION_PATH = os.path.join(MODELS_DIR, "logistic_regression.joblib")


def ensure_models_dir():
    """Ensures the directory for storing model artifacts exists."""
    os.makedirs(MODELS_DIR, exist_ok=True)


def save_model(model: Any, model_name: str) -> str:
    """Saves a trained sklearn model to disk using joblib."""
    ensure_models_dir()
    path = DECISION_TREE_PATH if "decision" in model_name.lower() else LOGISTIC_REGRESSION_PATH
    
    artifact = {
        "model": model,
        "model_name": model_name,
        "trained_at": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    joblib.dump(artifact, path)
    return path


def load_model(model_name: str = "Decision Tree") -> Tuple[Any, Dict[str, Any]]:
    """
    Loads a model artifact and metadata from disk.
    """
    path = DECISION_TREE_PATH if "decision" in model_name.lower() else LOGISTIC_REGRESSION_PATH
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model artifact not found at {path}. Run model training first.")
        
    artifact = joblib.load(path)
    return artifact["model"], {
        "model_name": artifact["model_name"],
        "trained_at": artifact["trained_at"],
        "version": artifact["version"]
    }

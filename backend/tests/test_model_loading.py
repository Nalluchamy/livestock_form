import os
import pytest
from backend.ml import model_registry, train


def test_model_training_and_loading():
    # Run training to produce joblib files
    train.train_models()

    dt_model, dt_meta = model_registry.load_model("Decision Tree")
    assert dt_model is not None
    assert dt_meta["model_name"] == "Decision Tree Classifier"

    lr_model, lr_meta = model_registry.load_model("Logistic Regression")
    assert lr_model is not None
    assert lr_meta["model_name"] == "Logistic Regression"

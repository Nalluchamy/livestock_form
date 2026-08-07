"""
Model Training Script for Decision Tree and Logistic Regression classifiers.
"""
import time
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

from backend.ml.dataset_loader import load_dataset
from backend.ml.feature_engineering import preprocess_dataframe
from backend.ml import model_registry


def train_models():
    """
    Trains Decision Tree and Logistic Regression models on synthetic livestock data,
    prints basic metrics, and saves joblib artifacts.
    """
    print("Loading synthetic livestock dataset...")
    X_raw, y = load_dataset()
    X = preprocess_dataframe(X_raw)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 1. Train Decision Tree Classifier
    print("Training Decision Tree Classifier...")
    t0 = time.time()
    dt_model = DecisionTreeClassifier(max_depth=5, random_state=42)
    dt_model.fit(X_train, y_train)
    dt_time = time.time() - t0

    dt_preds = dt_model.predict(X_test)
    dt_acc = accuracy_score(y_test, dt_preds)
    print(f"Decision Tree Trained in {dt_time:.4f}s - Test Accuracy: {dt_acc * 100:.2f}%")

    dt_path = model_registry.save_model(dt_model, "Decision Tree Classifier")
    print(f"Saved Decision Tree model to {dt_path}")

    # 2. Train Logistic Regression Classifier
    print("\nTraining Logistic Regression Classifier...")
    t0 = time.time()
    lr_model = LogisticRegression(max_iter=1000, random_state=42)
    lr_model.fit(X_train, y_train)
    lr_time = time.time() - t0

    lr_preds = lr_model.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_preds)
    print(f"Logistic Regression Trained in {lr_time:.4f}s - Test Accuracy: {lr_acc * 100:.2f}%")

    lr_path = model_registry.save_model(lr_model, "Logistic Regression")
    print(f"Saved Logistic Regression model to {lr_path}")


if __name__ == "__main__":
    train_models()

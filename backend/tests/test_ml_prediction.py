import pytest
from backend.ml import predict, train
from backend.grading import constants


@pytest.fixture(scope="module", autouse=True)
def setup_models():
    train.train_models()


def test_predict_decision_tree():
    attrs = {
        constants.ATTR_BODY_CONDITION: 3.0,
        constants.ATTR_COAT_QUALITY: "Smooth",
        constants.ATTR_EYE_CONDITION: "Clear",
        constants.ATTR_WOUND_PRESENCE: "None",
        constants.ATTR_MOBILITY: "Normal",
        constants.ATTR_APPETITE: "Good",
    }
    res = predict.predict_explainable_grade(attrs, model_name="Decision Tree")

    assert res["model"] == "Decision Tree Classifier"
    assert res["grade"] in constants.ALL_GRADES
    assert 0.0 <= res["confidence"] <= 100.0
    assert isinstance(res["top_features"], list)
    assert isinstance(res["explanations"], list)


def test_predict_logistic_regression():
    attrs = {
        constants.ATTR_BODY_CONDITION: 1.0,
        constants.ATTR_COAT_QUALITY: "Rough",
        constants.ATTR_EYE_CONDITION: "Cloudy",
        constants.ATTR_WOUND_PRESENCE: "Severe",
        constants.ATTR_MOBILITY: "Unable to stand",
        constants.ATTR_APPETITE: "None",
    }
    res = predict.predict_explainable_grade(attrs, model_name="Logistic Regression")

    assert res["model"] == "Logistic Regression"
    assert res["grade"] == constants.GRADE_D
    assert 0.0 <= res["confidence"] <= 100.0
    assert len(res["top_features"]) > 0

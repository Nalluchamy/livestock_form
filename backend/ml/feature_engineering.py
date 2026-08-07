"""
Feature Engineering & Preprocessing for ELHGS ML Pipeline.
Handles ordinal mapping of categorical livestock health observations.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

from backend.grading import constants

# Ordinal encodings mapping physical severity to numbers (0=Healthy -> 3=Severe)
COAT_ENCODING = {"Smooth": 0, "Slightly rough": 1, "Rough": 2, "Severe lesions": 3}
EYE_ENCODING = {"Clear": 0, "Slight discharge": 1, "Cloudy": 2, "Severe infection": 3}
WOUND_ENCODING = {"None": 0, "Minor": 1, "Moderate": 2, "Severe": 3}
MOBILITY_ENCODING = {"Normal": 0, "Slight limp": 1, "Lame": 2, "Unable to stand": 3}
APPETITE_ENCODING = {"Good": 0, "Fair": 1, "Poor": 2, "None": 3}

FEATURE_COLUMNS = [
    "body_condition",
    "coat_quality_enc",
    "eye_condition_enc",
    "wound_presence_enc",
    "mobility_enc",
    "appetite_enc"
]


def preprocess_single_input(attributes: Dict[str, Any]) -> np.ndarray:
    """
    Preprocesses a single attribute dictionary into a 2D numpy array suitable for model inference.
    """
    bcs = float(attributes.get(constants.ATTR_BODY_CONDITION, 3.0))
    coat = COAT_ENCODING.get(attributes.get(constants.ATTR_COAT_QUALITY, "Smooth"), 0)
    eye = EYE_ENCODING.get(attributes.get(constants.ATTR_EYE_CONDITION, "Clear"), 0)
    wound = WOUND_ENCODING.get(attributes.get(constants.ATTR_WOUND_PRESENCE, "None"), 0)
    mobility = MOBILITY_ENCODING.get(attributes.get(constants.ATTR_MOBILITY, "Normal"), 0)
    appetite = APPETITE_ENCODING.get(attributes.get(constants.ATTR_APPETITE, "Good"), 0)

    feature_vector = np.array([[bcs, coat, eye, wound, mobility, appetite]])
    return feature_vector


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Encodes categorical features of a DataFrame into numerical features.
    """
    processed = pd.DataFrame()
    processed["body_condition"] = df["body_condition"].astype(float)
    processed["coat_quality_enc"] = df["coat_quality"].map(COAT_ENCODING).fillna(0)
    processed["eye_condition_enc"] = df["eye_condition"].map(EYE_ENCODING).fillna(0)
    processed["wound_presence_enc"] = df["wound_presence"].map(WOUND_ENCODING).fillna(0)
    processed["mobility_enc"] = df["mobility"].map(MOBILITY_ENCODING).fillna(0)
    processed["appetite_enc"] = df["appetite"].map(APPETITE_ENCODING).fillna(0)
    return processed[FEATURE_COLUMNS]

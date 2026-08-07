"""
Dataset Loader for ELHGS ML Pipeline.
Generates a realistic synthetic livestock health dataset based on measured physical attributes.
"""
import random
import pandas as pd
from typing import Tuple

from backend.grading import constants


def generate_synthetic_dataset(num_samples: int = 600, random_seed: int = 42) -> pd.DataFrame:
    """
    Generates a realistic synthetic dataset for livestock health grading.
    Features: body_condition, coat_quality, eye_condition, wound_presence, mobility, appetite.
    Target: expert_grade (A, B, C, D).
    """
    random.seed(random_seed)
    data = []

    coat_options = list(constants.COAT_VALUES)
    eye_options = list(constants.EYE_VALUES)
    wound_options = list(constants.WOUND_VALUES)
    mobility_options = list(constants.MOBILITY_VALUES)
    appetite_options = list(constants.APPETITE_VALUES)

    for _ in range(num_samples):
        # Generate random attributes with realistic probability distributions
        bcs = round(random.uniform(1.0, 5.0), 1)
        coat = random.choice(coat_options)
        eye = random.choice(eye_options)
        wound = random.choice(wound_options)
        mobility = random.choice(mobility_options)
        appetite = random.choice(appetite_options)

        # Determine target grade based on expert-ground-truth rules with slight noise
        if wound == "Severe" or mobility == "Unable to stand" or bcs < 1.5 or bcs > 4.5:
            target = constants.GRADE_D
        elif wound == "Moderate" or coat == "Rough" or eye == "Cloudy" or mobility == "Lame" or appetite == "Poor" or bcs < 2.0 or bcs > 4.0:
            target = constants.GRADE_C
        elif coat == "Slightly rough" or eye == "Slight discharge" or wound == "Minor" or mobility == "Slight limp" or appetite == "Fair" or bcs < 2.5 or bcs > 3.5:
            target = constants.GRADE_B
        else:
            target = constants.GRADE_A

        # Introduce 5% realistic label noise to simulate human variance
        if random.random() < 0.05:
            noise_grades = [g for g in constants.ALL_GRADES if g != target]
            target = random.choice(noise_grades)

        data.append({
            "body_condition": bcs,
            "coat_quality": coat,
            "eye_condition": eye,
            "wound_presence": wound,
            "mobility": mobility,
            "appetite": appetite,
            "expert_grade": target
        })

    return pd.DataFrame(data)


def load_dataset() -> Tuple[pd.DataFrame, pd.Series]:
    """
    Loads dataset and splits into feature DataFrame X and target Series y.
    """
    df = generate_synthetic_dataset()
    X = df.drop(columns=["expert_grade"])
    y = df["expert_grade"]
    return X, y

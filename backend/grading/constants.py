"""
Constants and definitions for the grading engine.
Avoids magic numbers and hardcoded strings.
"""

# Overall Final Grades
GRADE_A = "A"
GRADE_B = "B"
GRADE_C = "C"
GRADE_D = "D"

ALL_GRADES = {GRADE_A, GRADE_B, GRADE_C, GRADE_D}

# Grade Values for Averaging (lower is better, assuming D=4, A=1)
GRADE_NUMERIC_MAP = {
    GRADE_A: 1,
    GRADE_B: 2,
    GRADE_C: 3,
    GRADE_D: 4,
}

# Attribute Names
ATTR_BODY_CONDITION = "body_condition"
ATTR_COAT_QUALITY = "coat_quality"
ATTR_EYE_CONDITION = "eye_condition"
ATTR_WOUND_PRESENCE = "wound_presence"
ATTR_MOBILITY = "mobility"
ATTR_APPETITE = "appetite"
ATTR_WEIGHT = "weight"

ALL_ATTRIBUTES = {
    ATTR_BODY_CONDITION,
    ATTR_COAT_QUALITY,
    ATTR_EYE_CONDITION,
    ATTR_WOUND_PRESENCE,
    ATTR_MOBILITY,
    ATTR_APPETITE,
}

# Acceptable values for categorical attributes
COAT_VALUES = {"Smooth", "Slightly rough", "Rough", "Severe lesions"}
EYE_VALUES = {"Clear", "Slight discharge", "Cloudy", "Severe infection"}
WOUND_VALUES = {"None", "Minor", "Moderate", "Severe"}
MOBILITY_VALUES = {"Normal", "Slight limp", "Lame", "Unable to stand"}
APPETITE_VALUES = {"Good", "Fair", "Poor", "None"}

# Confidence Score Constants
CONFIDENCE_MAX = 100
CONFIDENCE_MIN = 0

PENALTY_MISSING_ATTR = 15
PENALTY_CONTRADICTION = 20

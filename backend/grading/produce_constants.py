"""
Produce Grading Constants and Configuration.
Defines measurable visual thresholds, classifications, and rule criteria for produce (tomatoes).
Strictly segregated from livestock health domain constants.
"""

# Overall Produce Quality Grades
PRODUCE_GRADE_A = "A"  # Premium / Table Fresh
PRODUCE_GRADE_B = "B"  # Standard Commercial / Processing
PRODUCE_GRADE_C = "C"  # Cull / Reject

ALL_PRODUCE_GRADES = {PRODUCE_GRADE_A, PRODUCE_GRADE_B, PRODUCE_GRADE_C}

# Numeric mappings for agreement and metrics
PRODUCE_GRADE_NUMERIC = {
    PRODUCE_GRADE_A: 1,
    PRODUCE_GRADE_B: 2,
    PRODUCE_GRADE_C: 3,
}

# USDA Ripeness Stages for Tomatoes
RIPENESS_GREEN = "GREEN"
RIPENESS_BREAKER = "BREAKER"
RIPENESS_TURNING = "TURNING"
RIPENESS_PINK = "PINK"
RIPENESS_LIGHT_RED = "LIGHT_RED"
RIPENESS_RED = "RED"

ALL_RIPENESS_STAGES = {
    RIPENESS_GREEN,
    RIPENESS_BREAKER,
    RIPENESS_TURNING,
    RIPENESS_PINK,
    RIPENESS_LIGHT_RED,
    RIPENESS_RED,
}

# Bruising & Mechanical Damage
BRUISE_NONE = "NONE"
BRUISE_MINOR = "MINOR"
BRUISE_MODERATE = "MODERATE"
BRUISE_SEVERE = "SEVERE"

ALL_BRUISE_LEVELS = {
    BRUISE_NONE,
    BRUISE_MINOR,
    BRUISE_MODERATE,
    BRUISE_SEVERE,
}

# Critical Disqualifying Defects
CRITICAL_BLOSSOM_END_ROT = "blossom_end_rot"
CRITICAL_GROWTH_CRACKS = "growth_cracks"
CRITICAL_ACTIVE_ROT = "active_rot"
CRITICAL_PUNCTURE = "deep_puncture"

ALL_CRITICAL_DEFECTS = {
    CRITICAL_BLOSSOM_END_ROT,
    CRITICAL_GROWTH_CRACKS,
    CRITICAL_ACTIVE_ROT,
    CRITICAL_PUNCTURE,
}

# Objective Thresholds
MAX_DEFECT_PCT_GRADE_A = 5.0
MAX_DEFECT_PCT_GRADE_B = 15.0

BORDERLINE_DEFECT_TOLERANCE = 1.0  # Defines [4.0, 6.0] and [14.0, 16.0]

MIN_COLOR_UNIFORMITY_GRADE_A = 85.0
MIN_COLOR_UNIFORMITY_GRADE_B = 70.0

MIN_CIRCULARITY_GRADE_A = 0.78
MIN_CIRCULARITY_GRADE_B = 0.65

ASPECT_RATIO_MIN_A = 0.85
ASPECT_RATIO_MAX_A = 1.18
ASPECT_RATIO_MIN_B = 0.70
ASPECT_RATIO_MAX_B = 1.35

# Image Quality Gates
MIN_FOCUS_LAPLACIAN = 100.0
MIN_ILLUMINATION_LUX = 40.0
MAX_ILLUMINATION_LUX = 245.0
MAX_OCCLUSION_PCT = 30.0
OCCLUSION_REVIEW_THRESHOLD = 20.0

# Regulatory Disclaimer Notice
PROVISIONAL_RUBRIC_DISCLAIMER = (
    "PROVISIONAL_SOFTWARE_DEFAULT: Grading criteria represent engineering demonstration thresholds "
    "pending formal ratification by accredited agricultural produce quality authorities."
)

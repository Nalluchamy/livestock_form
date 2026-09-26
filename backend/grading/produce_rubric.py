"""
Produce Quality Grading Rubric.
Provides deterministic mapping of objective visual attributes (tomatoes)
to component grades and human review triggers.
"""
from typing import Dict, Any, Tuple, List, Optional
from backend.grading import produce_constants as pc


def evaluate_surface_defect(defect_pct: float) -> Tuple[str, str]:
    """
    Evaluates visible surface defect percentage.
    Grade A <= 5.0%, Grade B <= 15.0%, Grade C > 15.0%.
    """
    if defect_pct < 0.0:
        raise ValueError("Surface defect percentage cannot be negative")
    
    if defect_pct <= pc.MAX_DEFECT_PCT_GRADE_A:
        return pc.PRODUCE_GRADE_A, f"Surface defect area is minimal ({defect_pct:.1f}% <= {pc.MAX_DEFECT_PCT_GRADE_A}%)"
    elif defect_pct <= pc.MAX_DEFECT_PCT_GRADE_B:
        return pc.PRODUCE_GRADE_B, f"Surface defect area is moderate ({defect_pct:.1f}% <= {pc.MAX_DEFECT_PCT_GRADE_B}%)"
    else:
        return pc.PRODUCE_GRADE_C, f"Surface defect area exceeds commercial tolerance ({defect_pct:.1f}% > {pc.MAX_DEFECT_PCT_GRADE_B}%)"


def evaluate_ripeness(ripeness_stage: str, uniformity_pct: float) -> Tuple[str, str]:
    """
    Evaluates tomato maturity stage and chromaticity uniformity.
    """
    stage_upper = ripeness_stage.upper().strip()
    if stage_upper not in pc.ALL_RIPENESS_STAGES:
        raise ValueError(f"Unknown ripeness stage '{ripeness_stage}'. Expected one of {pc.ALL_RIPENESS_STAGES}")

    if stage_upper in {pc.RIPENESS_PINK, pc.RIPENESS_LIGHT_RED, pc.RIPENESS_RED} and uniformity_pct >= pc.MIN_COLOR_UNIFORMITY_GRADE_A:
        return pc.PRODUCE_GRADE_A, f"Maturity {stage_upper} with high color uniformity ({uniformity_pct:.1f}%)"
    elif stage_upper in {pc.RIPENESS_BREAKER, pc.RIPENESS_TURNING, pc.RIPENESS_PINK, pc.RIPENESS_LIGHT_RED, pc.RIPENESS_RED} and uniformity_pct >= pc.MIN_COLOR_UNIFORMITY_GRADE_B:
        return pc.PRODUCE_GRADE_B, f"Maturity {stage_upper} with acceptable commercial color uniformity ({uniformity_pct:.1f}%)"
    else:
        return pc.PRODUCE_GRADE_C, f"Immature green or mottled uneven coloring ({stage_upper}, {uniformity_pct:.1f}%)"


def evaluate_bruising(bruise_level: str) -> Tuple[str, str]:
    """
    Evaluates mechanical bruising severity.
    """
    level_upper = bruise_level.upper().strip()
    if level_upper not in pc.ALL_BRUISE_LEVELS:
        raise ValueError(f"Unknown bruise level '{bruise_level}'. Expected one of {pc.ALL_BRUISE_LEVELS}")

    if level_upper == pc.BRUISE_NONE:
        return pc.PRODUCE_GRADE_A, "No visible mechanical bruising"
    elif level_upper in {pc.BRUISE_MINOR, pc.BRUISE_MODERATE}:
        return pc.PRODUCE_GRADE_B, f"Minor to moderate superficial bruising ({level_upper.lower()})"
    else:
        return pc.PRODUCE_GRADE_C, "Severe structural bruising or ruptured epidermis"


def evaluate_geometry(circularity: float, aspect_ratio: float) -> Tuple[str, str]:
    """
    Evaluates symmetry, circularity and aspect ratio.
    """
    if circularity >= pc.MIN_CIRCULARITY_GRADE_A and pc.ASPECT_RATIO_MIN_A <= aspect_ratio <= pc.ASPECT_RATIO_MAX_A:
        return pc.PRODUCE_GRADE_A, f"Symmetrical round fruit shape (circularity {circularity:.2f}, AR {aspect_ratio:.2f})"
    elif circularity >= pc.MIN_CIRCULARITY_GRADE_B and pc.ASPECT_RATIO_MIN_B <= aspect_ratio <= pc.ASPECT_RATIO_MAX_B:
        return pc.PRODUCE_GRADE_B, f"Moderately irregular shape (circularity {circularity:.2f}, AR {aspect_ratio:.2f})"
    else:
        return pc.PRODUCE_GRADE_C, f"Severely misshapen or distorted fruit (circularity {circularity:.2f}, AR {aspect_ratio:.2f})"


def evaluate_critical_defects(defects: List[str]) -> Tuple[bool, List[str]]:
    """
    Checks if any disqualifying critical defects are present.
    Returns (has_critical, triggered_descriptions).
    """
    triggered = []
    for d in defects:
        clean = d.lower().strip()
        if clean in pc.ALL_CRITICAL_DEFECTS:
            triggered.append(f"Critical disqualifying defect present: {clean.replace('_', ' ')}")
    return (len(triggered) > 0, triggered)


def check_image_quality(
    laplacian_var: float,
    illumination_mean: float,
    occlusion_pct: float
) -> Tuple[bool, List[str], List[str]]:
    """
    Validates optical capture suitability.
    Returns (is_acceptable, blocking_errors, warnings).
    """
    errors: List[str] = []
    warnings: List[str] = []

    if laplacian_var < pc.MIN_FOCUS_LAPLACIAN:
        errors.append(f"Image blur detected (Laplacian variance {laplacian_var:.1f} < {pc.MIN_FOCUS_LAPLACIAN})")
    
    if illumination_mean < pc.MIN_ILLUMINATION_LUX:
        errors.append(f"Image severely under-illuminated (mean luminance {illumination_mean:.1f} < {pc.MIN_ILLUMINATION_LUX} lux)")
    elif illumination_mean > pc.MAX_ILLUMINATION_LUX:
        errors.append(f"Image over-exposed (mean luminance {illumination_mean:.1f} > {pc.MAX_ILLUMINATION_LUX})")

    if occlusion_pct > pc.MAX_OCCLUSION_PCT:
        errors.append(f"Fruit surface obstructed beyond allowable limit ({occlusion_pct:.1f}% > {pc.MAX_OCCLUSION_PCT}%)")
    elif occlusion_pct >= pc.OCCLUSION_REVIEW_THRESHOLD:
        warnings.append(f"Partial occlusion observed ({occlusion_pct:.1f}%); visible surface may omit defects")

    is_acceptable = len(errors) == 0
    return is_acceptable, errors, warnings


def check_borderline_escalation(
    defect_pct: float,
    uniformity_pct: float,
    occlusion_pct: float
) -> Tuple[bool, List[str]]:
    """
    Identifies borderline score regions requiring senior human adjudicator review.
    """
    reasons: List[str] = []

    # Borderline Grade A / B boundary (4.0% - 6.0%)
    if abs(defect_pct - pc.MAX_DEFECT_PCT_GRADE_A) <= pc.BORDERLINE_DEFECT_TOLERANCE:
        reasons.append(f"Borderline Grade A/B defect percentage ({defect_pct:.1f}%, within 1% of 5.0% threshold)")

    # Borderline Grade B / C boundary (14.0% - 16.0%)
    if abs(defect_pct - pc.MAX_DEFECT_PCT_GRADE_B) <= pc.BORDERLINE_DEFECT_TOLERANCE:
        reasons.append(f"Borderline Grade B/C defect percentage ({defect_pct:.1f}%, within 1% of 15.0% threshold)")

    # Partial occlusion warning
    if occlusion_pct >= pc.OCCLUSION_REVIEW_THRESHOLD:
        reasons.append(f"Partial fruit occlusion ({occlusion_pct:.1f}% >= {pc.OCCLUSION_REVIEW_THRESHOLD}%) requires visual verification")

    return (len(reasons) > 0, reasons)

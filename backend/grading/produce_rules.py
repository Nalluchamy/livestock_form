"""
Produce Grading Rules Engine.
Defines the overarching deterministic evaluation rules, rule hierarchy,
explainable rationales, and review triggers for produce (tomatoes).
"""
from typing import Dict, Any, List, Optional
from backend.grading import produce_constants as pc
from backend.grading import produce_rubric as pr


def evaluate_produce_sample(
    surface_defect_pct: float,
    ripeness_stage: str,
    color_uniformity_pct: float = 85.0,
    bruising_severity: str = pc.BRUISE_NONE,
    shape_circularity: float = 0.85,
    aspect_ratio: float = 1.0,
    critical_defects: Optional[List[str]] = None,
    laplacian_var: float = 150.0,
    illumination_mean: float = 120.0,
    surface_occlusion_pct: float = 0.0,
    human_grade: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates a produce sample deterministically across the USDA/UNECE rubric hierarchy.

    Evaluation Hierarchy & Priority Order:
    1. Tier 0 - Optical Quality Gate: Validates focus (Laplacian variance >= 100), lighting
       (40 <= lux <= 245), and surface occlusion (<= 30%). Rejects ungradable captures immediately.
    2. Tier 1 - Disqualifying Critical Defects: Checks for blossom end rot lesions, growth cracks,
       active decay, or deep punctures. If present, fruit is assigned Grade C (Cull) immediately.
    3. Tier 2 - Epidermal Defect Area: Evaluates surface defect surface area:
       - <= 5.0% -> Grade A eligible
       - <= 15.0% -> Grade B eligible
       - > 15.0% -> Grade C (Commercial Cull)
    4. Tier 3 - Ripeness & Color Uniformity: Evaluates USDA ripeness stage and color variance.
       Immature green or mottled fruit fails Grade A/B requirements.
    5. Tier 4 - Mechanical Damage & Bruising: Evaluates structural integrity (None -> A, Minor/Mod -> B, Severe -> C).
    6. Tier 5 - Geometric Symmetry: Evaluates circularity and aspect ratio against roundness bounds.
    7. Tier 6 - Borderline Review Triggering: Inspects defect boundaries [4.0%, 6.0%] and [14.0%, 16.0%].
       Flags borderline cases for human oversight while generating counterfactual improvement paths.

    Returns:
        Deterministic explainability payload with provisional grade, reasons, rules, and counterfactuals.
    """
    critical_defects = critical_defects or []
    triggered_rules: List[str] = []
    reasons: List[str] = []
    missing_attributes: List[str] = []
    review_reasons: List[str] = []
    review_required = False

    # 1. Optical Image Quality Gate
    img_ok, img_errors, img_warnings = pr.check_image_quality(
        laplacian_var=laplacian_var,
        illumination_mean=illumination_mean,
        occlusion_pct=surface_occlusion_pct
    )

    if not img_ok:
        triggered_rules.append("RULE_IMAGE_QUALITY_REJECTION")
        return {
            "provisional_grade": "REJECTED_IMAGE",
            "confidence": 0.0,
            "confidence_type": "Deterministic Rule Clearance (Uncalibrated)",
            "image_quality_passed": False,
            "reasons": img_errors,
            "triggered_rules": triggered_rules,
            "review_required": True,
            "review_reasons": ["Image quality unsuitable for automated grading: " + "; ".join(img_errors)],
            "missing_observations": [],
            "provisional_notice": pc.PROVISIONAL_RUBRIC_DISCLAIMER,
            "sub_grades": {},
            "raw_attributes": {
                "laplacian_var": laplacian_var,
                "illumination_mean": illumination_mean,
                "surface_occlusion_pct": surface_occlusion_pct,
            }
        }

    # 2. Critical Defects Gate
    has_crit, crit_msgs = pr.evaluate_critical_defects(critical_defects)
    if has_crit:
        triggered_rules.append("RULE_CRITICAL_DEFECT_DISQUALIFICATION")
        reasons.extend(crit_msgs)
        final_grade = pc.PRODUCE_GRADE_C
        grade_confidence = 98.0
        review_required = True
        review_reasons.append("Critical disqualifying defect identified; requires physical dock verification")
    else:
        # 3. Evaluate Component Criteria
        sub_grades = {}

        g_defect, r_defect = pr.evaluate_surface_defect(surface_defect_pct)
        sub_grades["surface_defect"] = g_defect
        reasons.append(r_defect)

        g_ripeness, r_ripeness = pr.evaluate_ripeness(ripeness_stage, color_uniformity_pct)
        sub_grades["ripeness"] = g_ripeness
        reasons.append(r_ripeness)

        g_bruise, r_bruise = pr.evaluate_bruising(bruising_severity)
        sub_grades["bruising"] = g_bruise
        reasons.append(r_bruise)

        g_geom, r_geom = pr.evaluate_geometry(shape_circularity, aspect_ratio)
        sub_grades["geometry"] = g_geom
        reasons.append(r_geom)

        # 4. Synthesize Final Grade
        numeric_scores = [pc.PRODUCE_GRADE_NUMERIC[g] for g in sub_grades.values()]
        max_score = max(numeric_scores)  # Worst sub-grade

        if max_score == 1:
            final_grade = pc.PRODUCE_GRADE_A
            triggered_rules.append("RULE_GRADE_A_PREMIUM")
            reasons.append("All visual attributes meet Grade A premium commercial thresholds")
            # Confidence based on distance to 5% cutoff
            margin = pc.MAX_DEFECT_PCT_GRADE_A - surface_defect_pct
            grade_confidence = min(99.0, max(75.0, 75.0 + (margin / pc.MAX_DEFECT_PCT_GRADE_A) * 24.0))
        elif max_score == 2:
            final_grade = pc.PRODUCE_GRADE_B
            triggered_rules.append("RULE_GRADE_B_COMMERCIAL")
            reasons.append("Sample meets Grade B standard commercial specifications")
            grade_confidence = 85.0
        else:
            final_grade = pc.PRODUCE_GRADE_C
            triggered_rules.append("RULE_GRADE_C_DOWNGRADE")
            reasons.append("One or more attributes fail commercial specifications, downgraded to Grade C")
            grade_confidence = 90.0

    # 5. Check Borderline & Human Review Triggers
    is_borderline, borderline_msgs = pr.check_borderline_escalation(
        defect_pct=surface_defect_pct,
        uniformity_pct=color_uniformity_pct,
        occlusion_pct=surface_occlusion_pct
    )
    if is_borderline:
        triggered_rules.append("RULE_BORDERLINE_UNCERTAINTY")
        review_required = True
        review_reasons.extend(borderline_msgs)
        grade_confidence = max(55.0, grade_confidence - 20.0)

    if img_warnings:
        review_reasons.extend(img_warnings)

    # 6. Check Human Disagreement if human grade was supplied
    disagreement_detected = False
    disagreement_details = None
    if human_grade:
        h_clean = human_grade.upper().strip()
        if h_clean in pc.ALL_PRODUCE_GRADES:
            if h_clean != final_grade:
                disagreement_detected = True
                review_required = True
                triggered_rules.append("RULE_DISAGREEMENT_TRIGGERED")
                disagreement_details = {
                    "human_grade": h_clean,
                    "system_grade": final_grade,
                    "reason": f"Human grader assigned {h_clean}, but system rule engine derived {final_grade} based on observable attributes."
                }
                review_reasons.append(f"Inter-grader/system discordance: human {h_clean} vs system {final_grade}")

    return {
        "provisional_grade": final_grade,
        "confidence": round(grade_confidence, 1),
        "confidence_type": "Deterministic Rule Clearance (Uncalibrated)",
        "image_quality_passed": True,
        "reasons": reasons,
        "triggered_rules": triggered_rules,
        "review_required": review_required,
        "review_reasons": review_reasons,
        "missing_observations": missing_attributes,
        "disagreement": disagreement_details,
        "disagreement_detected": disagreement_detected,
        "provisional_notice": pc.PROVISIONAL_RUBRIC_DISCLAIMER,
        "sub_grades": sub_grades if not has_crit else {"critical_defect": pc.PRODUCE_GRADE_C},
        "raw_attributes": {
            "surface_defect_pct": surface_defect_pct,
            "ripeness_stage": ripeness_stage,
            "color_uniformity_pct": color_uniformity_pct,
            "bruising_severity": bruising_severity,
            "shape_circularity": shape_circularity,
            "aspect_ratio": aspect_ratio,
            "critical_defects": critical_defects,
            "laplacian_var": laplacian_var,
            "illumination_mean": illumination_mean,
            "surface_occlusion_pct": surface_occlusion_pct,
        }
    }

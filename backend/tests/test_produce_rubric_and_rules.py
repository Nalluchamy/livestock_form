"""
Tests for Produce Quality Grading Rubric and Rules Engine (Tomatoes).
Verifies deterministic grading, threshold boundaries, critical defect disqualifications,
borderline review triggers, and disagreement detection.
"""
import pytest
from backend.grading import produce_constants as pc
from backend.grading import produce_rubric as pr
from backend.grading import produce_rules as pr_rules


def test_evaluate_surface_defect_thresholds():
    # Grade A: <= 5.0%
    grade, reason = pr.evaluate_surface_defect(0.0)
    assert grade == pc.PRODUCE_GRADE_A
    grade, reason = pr.evaluate_surface_defect(5.0)
    assert grade == pc.PRODUCE_GRADE_A

    # Grade B: 5.01% - 15.0%
    grade, reason = pr.evaluate_surface_defect(5.1)
    assert grade == pc.PRODUCE_GRADE_B
    grade, reason = pr.evaluate_surface_defect(15.0)
    assert grade == pc.PRODUCE_GRADE_B

    # Grade C: > 15.0%
    grade, reason = pr.evaluate_surface_defect(15.1)
    assert grade == pc.PRODUCE_GRADE_C
    grade, reason = pr.evaluate_surface_defect(45.0)
    assert grade == pc.PRODUCE_GRADE_C

    # Invalid negative
    with pytest.raises(ValueError):
        pr.evaluate_surface_defect(-1.0)


def test_evaluate_ripeness_stages():
    # Grade A: PINK/LIGHT_RED/RED with uniformity >= 85
    grade, _ = pr.evaluate_ripeness("RED", 90.0)
    assert grade == pc.PRODUCE_GRADE_A
    grade, _ = pr.evaluate_ripeness("LIGHT_RED", 85.0)
    assert grade == pc.PRODUCE_GRADE_A

    # Grade B: BREAKER/TURNING or PINK/RED with uniformity 70-84
    grade, _ = pr.evaluate_ripeness("TURNING", 80.0)
    assert grade == pc.PRODUCE_GRADE_B
    grade, _ = pr.evaluate_ripeness("RED", 75.0)
    assert grade == pc.PRODUCE_GRADE_B

    # Grade C: GREEN or uniformity < 70
    grade, _ = pr.evaluate_ripeness("GREEN", 95.0)
    assert grade == pc.PRODUCE_GRADE_C
    grade, _ = pr.evaluate_ripeness("RED", 60.0)
    assert grade == pc.PRODUCE_GRADE_C

    with pytest.raises(ValueError):
        pr.evaluate_ripeness("OVERRIPE_BANANA", 80.0)


def test_evaluate_bruising_and_geometry():
    # Bruising
    assert pr.evaluate_bruising(pc.BRUISE_NONE)[0] == pc.PRODUCE_GRADE_A
    assert pr.evaluate_bruising(pc.BRUISE_MINOR)[0] == pc.PRODUCE_GRADE_B
    assert pr.evaluate_bruising(pc.BRUISE_MODERATE)[0] == pc.PRODUCE_GRADE_B
    assert pr.evaluate_bruising(pc.BRUISE_SEVERE)[0] == pc.PRODUCE_GRADE_C

    # Geometry
    # Grade A: circ >= 0.78 and 0.85 <= AR <= 1.18
    assert pr.evaluate_geometry(0.85, 1.0)[0] == pc.PRODUCE_GRADE_A
    # Grade B: circ >= 0.65 and 0.70 <= AR <= 1.35
    assert pr.evaluate_geometry(0.70, 1.25)[0] == pc.PRODUCE_GRADE_B
    # Grade C: irregular
    assert pr.evaluate_geometry(0.50, 1.50)[0] == pc.PRODUCE_GRADE_C


def test_evaluate_produce_sample_grade_a():
    result = pr_rules.evaluate_produce_sample(
        surface_defect_pct=2.0,
        ripeness_stage="RED",
        color_uniformity_pct=90.0,
        bruising_severity=pc.BRUISE_NONE,
        shape_circularity=0.88,
        aspect_ratio=1.02,
        laplacian_var=180.0,
        illumination_mean=135.0,
        surface_occlusion_pct=5.0
    )
    assert result["provisional_grade"] == pc.PRODUCE_GRADE_A
    assert result["image_quality_passed"] is True
    assert "RULE_GRADE_A_PREMIUM" in result["triggered_rules"]
    assert result["review_required"] is False
    assert result["confidence"] >= 75.0


def test_evaluate_produce_sample_critical_defect():
    result = pr_rules.evaluate_produce_sample(
        surface_defect_pct=1.0,
        ripeness_stage="RED",
        critical_defects=[pc.CRITICAL_BLOSSOM_END_ROT]
    )
    assert result["provisional_grade"] == pc.PRODUCE_GRADE_C
    assert "RULE_CRITICAL_DEFECT_DISQUALIFICATION" in result["triggered_rules"]
    assert result["review_required"] is True


def test_evaluate_produce_sample_borderline_escalation():
    # 5.1% defect is within 1% of the 5.0% cutoff -> Borderline A/B
    result = pr_rules.evaluate_produce_sample(
        surface_defect_pct=5.1,
        ripeness_stage="RED",
        color_uniformity_pct=88.0
    )
    assert result["provisional_grade"] == pc.PRODUCE_GRADE_B
    assert result["review_required"] is True
    assert "RULE_BORDERLINE_UNCERTAINTY" in result["triggered_rules"]
    assert any("Borderline Grade A/B" in r for r in result["review_reasons"])


def test_evaluate_produce_sample_disagreement_detection():
    # System evaluates B (due to 8% defect), human grader submitted A
    result = pr_rules.evaluate_produce_sample(
        surface_defect_pct=8.0,
        ripeness_stage="RED",
        human_grade="A"
    )
    assert result["provisional_grade"] == pc.PRODUCE_GRADE_B
    assert result["disagreement_detected"] is True
    assert result["review_required"] is True
    assert "RULE_DISAGREEMENT_TRIGGERED" in result["triggered_rules"]
    assert result["disagreement"]["human_grade"] == "A"
    assert result["disagreement"]["system_grade"] == "B"


def test_evaluate_produce_sample_image_quality_rejection():
    # Low Laplacian variance (blur)
    result = pr_rules.evaluate_produce_sample(
        surface_defect_pct=1.0,
        ripeness_stage="RED",
        laplacian_var=35.0  # severely blurred (< 100)
    )
    assert result["provisional_grade"] == "REJECTED_IMAGE"
    assert result["image_quality_passed"] is False
    assert result["confidence"] == 0.0
    assert "RULE_IMAGE_QUALITY_REJECTION" in result["triggered_rules"]

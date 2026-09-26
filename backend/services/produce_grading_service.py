"""
Produce Grading Service.
Orchestrates computer-vision feature extraction, deterministic rule grading,
double-blind comparison, and persistent disagreement review escalation for produce (tomatoes).
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.grading import produce_constants as pc
from backend.grading import produce_rules as pr_rules
from backend.evaluation import produce_ingestion as pr_ingest
from backend.repositories.review_repository import ReviewRepository


class ProduceGradingService:
    def __init__(self, db: Optional[Session] = None):
        self.db = db
        self.review_repo = ReviewRepository(db) if db else None

    def grade_sample(
        self,
        image_bytes: Optional[bytes] = None,
        attributes: Optional[Dict[str, Any]] = None,
        human_grade: Optional[str] = None,
        create_persistent_review_on_disagreement: bool = True
    ) -> Dict[str, Any]:
        """
        Grades a produce sample from either image bytes, manual attributes, or both.
        If both are provided, manual attributes override extracted image features.
        """
        attributes = attributes or {}
        extracted_features: Dict[str, Any] = {}

        if image_bytes:
            extracted_features = pr_ingest.extract_produce_features(image_bytes)

        # Merge extracted features with manual attributes (manual takes precedence)
        merged_attrs = {
            "surface_defect_pct": float(attributes.get("surface_defect_pct", extracted_features.get("surface_defect_pct", 0.0))),
            "ripeness_stage": str(attributes.get("ripeness_stage", extracted_features.get("ripeness_stage", pc.RIPENESS_RED))),
            "color_uniformity_pct": float(attributes.get("color_uniformity_pct", extracted_features.get("color_uniformity_pct", 85.0))),
            "bruising_severity": str(attributes.get("bruising_severity", extracted_features.get("bruising_severity", pc.BRUISE_NONE))),
            "shape_circularity": float(attributes.get("shape_circularity", extracted_features.get("shape_circularity", 0.85))),
            "aspect_ratio": float(attributes.get("aspect_ratio", extracted_features.get("aspect_ratio", 1.0))),
            "critical_defects": list(attributes.get("critical_defects", extracted_features.get("critical_defects", []))),
            "laplacian_var": float(attributes.get("laplacian_var", extracted_features.get("laplacian_var", 150.0))),
            "illumination_mean": float(attributes.get("illumination_mean", extracted_features.get("illumination_mean", 120.0))),
            "surface_occlusion_pct": float(attributes.get("surface_occlusion_pct", extracted_features.get("surface_occlusion_pct", 0.0))),
            "human_grade": human_grade or attributes.get("human_grade"),
        }

        # Deterministic explainable rule evaluation
        result = pr_rules.evaluate_produce_sample(
            surface_defect_pct=merged_attrs["surface_defect_pct"],
            ripeness_stage=merged_attrs["ripeness_stage"],
            color_uniformity_pct=merged_attrs["color_uniformity_pct"],
            bruising_severity=merged_attrs["bruising_severity"],
            shape_circularity=merged_attrs["shape_circularity"],
            aspect_ratio=merged_attrs["aspect_ratio"],
            critical_defects=merged_attrs["critical_defects"],
            laplacian_var=merged_attrs["laplacian_var"],
            illumination_mean=merged_attrs["illumination_mean"],
            surface_occlusion_pct=merged_attrs["surface_occlusion_pct"],
            human_grade=merged_attrs["human_grade"]
        )

        # If disagreement detected and DB available, persist review record
        persistent_review_id = None
        if result.get("disagreement_detected") and self.review_repo and create_persistent_review_on_disagreement:
            try:
                review = self.review_repo.create_review(
                    original_human_grade=merged_attrs["human_grade"],
                    original_system_grade=result["provisional_grade"],
                    reviewer_rationale="Automatic disagreement escalation from produce grading engine."
                )
                persistent_review_id = str(review.id)
            except Exception:
                # Disagreement persistence failure must not crash grading pipeline
                pass

        result["persistent_review_id"] = persistent_review_id
        result["extracted_features"] = extracted_features
        return result

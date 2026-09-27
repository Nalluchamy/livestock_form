"""
Benchmark Evaluation Script for Synthetic Produce Dataset.
Evaluates physical synthetic tomato images through the EQGS pipeline:
- Ingestion and optical quality gate validation
- Feature extraction and deterministic produce grading
- Calculation of classification metrics (Accuracy, Precision, Recall, F1-Score)
- Confusion Matrix computation across Grade A, B, C, and Edge Cases
- Quality Gate rejection rate tracking
- Storage in dataset/produce/synthetic/benchmark_results.json
- Database persistence under evaluation_type='synthetic_produce_development'
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from collections import defaultdict

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.evaluation.produce_ingestion import extract_produce_features
from backend.grading import produce_rules as pr_rules
from backend.database.session import SessionLocal
from backend.repositories.experiment_repository import ExperimentRepository

SYNTHETIC_DIR = os.path.join(BASE_DIR, "dataset", "produce", "synthetic")
BENCHMARK_RESULTS_PATH = os.path.join(SYNTHETIC_DIR, "benchmark_results.json")


def run_synthetic_benchmark(synthetic_root: str = SYNTHETIC_DIR) -> Dict[str, Any]:
    """Runs rigorous benchmarking over verified physical synthetic images."""
    categories = ["grade_a", "grade_b", "grade_c", "edge_cases"]
    
    evaluated_samples = []
    total_physical_images = 0
    optical_rejected = 0
    optical_passed = 0

    # Ground truth vs Predicted tallies
    classes = ["A", "B", "C", "REJECTED_IMAGE"]
    confusion_matrix = {gt: {pred: 0 for pred in classes} for gt in ["A", "B", "C", "EDGE_CASE"]}

    for cat in categories:
        cat_dir = os.path.join(synthetic_root, cat)
        if not os.path.exists(cat_dir):
            continue

        files = sorted([f for f in os.listdir(cat_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        for filename in files:
            total_physical_images += 1
            file_path = os.path.join(cat_dir, filename)
            
            with open(file_path, "rb") as f:
                image_bytes = f.read()

            features = extract_produce_features(image_bytes)
            eval_result = pr_rules.evaluate_produce_sample(
                surface_defect_pct=features["surface_defect_pct"],
                ripeness_stage=features["ripeness_stage"],
                color_uniformity_pct=features["color_uniformity_pct"],
                bruising_severity=features["bruising_severity"],
                shape_circularity=features["shape_circularity"],
                aspect_ratio=features["aspect_ratio"],
                critical_defects=features["critical_defects"],
                laplacian_var=features["laplacian_var"],
                illumination_mean=features["illumination_mean"],
                surface_occlusion_pct=features["surface_occlusion_pct"]
            )

            derived_grade = eval_result["provisional_grade"]
            expected_grade = "A" if cat == "grade_a" else ("B" if cat == "grade_b" else ("C" if cat == "grade_c" else "EDGE_CASE"))

            if derived_grade == "REJECTED_IMAGE":
                optical_rejected += 1
            else:
                optical_passed += 1

            # Update confusion matrix
            pred_key = derived_grade if derived_grade in classes else "C"
            if expected_grade in confusion_matrix and pred_key in confusion_matrix[expected_grade]:
                confusion_matrix[expected_grade][pred_key] += 1

            evaluated_samples.append({
                "sample_id": os.path.splitext(filename)[0],
                "filename": filename,
                "category": cat,
                "expected_grade": expected_grade,
                "derived_grade": derived_grade,
                "confidence": eval_result.get("confidence", 0.0),
                "quality_passed": features.get("quality_passed", True),
                "review_required": eval_result.get("review_required", False),
                "triggered_rules": eval_result.get("triggered_rules", []),
                "extracted_features": {
                    "surface_defect_pct": features.get("surface_defect_pct"),
                    "ripeness_stage": features.get("ripeness_stage"),
                    "laplacian_var": features.get("laplacian_var"),
                    "illumination_mean": features.get("illumination_mean"),
                }
            })

    # Metric computations
    # Pure commercial classes: A, B, C
    commercial_total = 0
    commercial_correct = 0
    per_class_metrics = {}

    for c in ["A", "B", "C"]:
        tp = confusion_matrix[c].get(c, 0)
        fn = sum(v for k, v in confusion_matrix[c].items() if k != c)
        fp = sum(confusion_matrix[other].get(c, 0) for other in ["A", "B", "C", "EDGE_CASE"] if other != c)

        precision = round((tp / (tp + fp)) * 100.0, 1) if (tp + fp) > 0 else 0.0
        recall = round((tp / (tp + fn)) * 100.0, 1) if (tp + fn) > 0 else 0.0
        f1 = round((2 * precision * recall) / (precision + recall), 1) if (precision + recall) > 0 else 0.0

        commercial_total += (tp + fn)
        commercial_correct += tp

        per_class_metrics[f"Grade_{c}"] = {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision_pct": precision,
            "recall_pct": recall,
            "f1_score": f1
        }

    overall_accuracy_pct = round((commercial_correct / commercial_total) * 100.0, 1) if commercial_total > 0 else 0.0
    quality_gate_rejection_rate = round((optical_rejected / total_physical_images) * 100.0, 1) if total_physical_images > 0 else 0.0

    benchmark_summary = {
        "benchmark_name": "EQGS Synthetic Produce Prototype Benchmark",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evaluation_type": "synthetic_produce_development",
        "is_synthetic": True,
        "dataset_version": "v1.0-synthetic",
        "total_images_evaluated": total_physical_images,
        "optical_quality_gate": {
            "passed_count": optical_passed,
            "rejected_count": optical_rejected,
            "rejection_rate_pct": quality_gate_rejection_rate
        },
        "metrics": {
            "commercial_samples_count": commercial_total,
            "commercial_correct_count": commercial_correct,
            "accuracy_pct": overall_accuracy_pct,
            "per_class": per_class_metrics
        },
        "confusion_matrix": confusion_matrix,
        "sample_evaluations": evaluated_samples,
        "non_fabrication_declaration": (
            "Benchmark derived exclusively from physical synthetic images in dataset/produce/synthetic/. "
            "Excludes ungenerated queued prompts and genuine field images. "
            "This prototype has not been validated on genuine field photographs."
        )
    }

    # Save to disk
    with open(BENCHMARK_RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(benchmark_summary, f, indent=2)

    # Persist to database if available
    try:
        db = SessionLocal()
        try:
            repo = ExperimentRepository(db)
            repo.create_experiment_result(
                experiment_name="EXP_SYNTHETIC_BENCHMARK_PRODUCE",
                dataset_version="v1.0-synthetic",
                evaluation_type="synthetic_produce_development",
                metrics_summary=benchmark_summary,
                status="completed_simulation"
            )
            print("Successfully recorded benchmark run in PostgreSQL under evaluation_type='synthetic_produce_development'.")
        finally:
            db.close()
    except Exception as db_err:
        print(f"Notice: PostgreSQL persistence skipped or deferred ({str(db_err)}). JSON results saved.")

    return benchmark_summary


def main():
    print("=" * 60)
    print("EQGS SYNTHETIC PRODUCE BENCHMARK EVALUATION")
    print("=" * 60)
    results = run_synthetic_benchmark()
    print(f"Total Physical Images Evaluated: {results['total_images_evaluated']}")
    print(f"Optical Quality Gate Rejections: {results['optical_quality_gate']['rejected_count']} ({results['optical_quality_gate']['rejection_rate_pct']}%)")
    print(f"Commercial Defect Accuracy:      {results['metrics']['accuracy_pct']}%")
    print("\nConfusion Matrix:")
    for gt, preds in results["confusion_matrix"].items():
        print(f"  GT {gt:<10}: {preds}")
    print(f"\nSaved Benchmark Results to: {BENCHMARK_RESULTS_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()

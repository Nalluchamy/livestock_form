"""
Before-and-After Controlled Experiment Runner for Produce Quality Grading.
Evaluates:
- Baseline (Human-Only) vs Assisted (AI-Assisted Human Grading)
- Inter-grader dispute rates and relative dispute reduction %
- Cohen's Kappa and exact match agreement
- Mean assessment duration
- Transparent persistence to PostgreSQL `experiment_results` table
"""
import statistics
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from backend.evaluation.agreement_metrics import cohen_kappa, exact_match_percentage
from backend.repositories.experiment_repository import ExperimentRepository


# Predefined Benchmarks & Targets
BENCHMARK_TARGETS = {
    "dispute_rate_baseline": 33.3,
    "dispute_rate_target": 15.0,
    "relative_dispute_reduction_target_pct": 50.0,
    "cohen_kappa_baseline": 0.58,
    "cohen_kappa_target": 0.80,
    "expert_agreement_baseline_pct": 74.2,
    "expert_agreement_target_pct": 88.0,
    "mean_duration_baseline_sec": 28.4,
    "mean_duration_target_sec": 18.0,
}


def calculate_dispute_rate(grades_1: List[str], grades_2: List[str]) -> Tuple[float, int, int]:
    """
    Calculates percentage of discordant evaluations between two graders.
    Returns (dispute_rate_pct, dispute_count, total_count).
    """
    if not grades_1 or len(grades_1) != len(grades_2):
        return 0.0, 0, 0
    total = len(grades_1)
    disputes = sum(1 for g1, g2 in zip(grades_1, grades_2) if g1.strip().upper() != g2.strip().upper())
    rate = round((disputes / float(total)) * 100.0, 2)
    return rate, disputes, total


def calculate_relative_dispute_reduction(dr_baseline: float, dr_assisted: float) -> Optional[float]:
    """
    Calculates percentage reduction in dispute rate from baseline.
    Returns None (undefined) if baseline dispute rate is zero to avoid division by zero.
    """
    if dr_baseline <= 0.0:
        return None
    reduction = ((dr_baseline - dr_assisted) / dr_baseline) * 100.0
    return round(reduction, 2)


def calculate_cohort_metrics(
    trials: List[Dict[str, Any]],
    condition_name: str
) -> Dict[str, Any]:
    """Calculates metrics for a single cohort condition (baseline or assisted)."""
    if not trials:
        return {
            "condition": condition_name,
            "sample_count": 0,
            "dispute_rate_pct": 0.0,
            "dispute_count": 0,
            "exact_agreement_pct": 0.0,
            "cohen_kappa": 0.0,
            "expert_agreement_pct": 0.0,
            "mean_duration_sec": 0.0,
            "median_duration_sec": 0.0,
            "escalations_count": 0,
            "reference_evaluations_count": 0,
            "average_confidence": 0.0,
        }

    g1_list = [t["grader_1_grade"] for t in trials]
    g2_list = [t["grader_2_grade"] for t in trials]
    ref_list = [t.get("reference_grade") for t in trials]
    durations = [float(t.get("duration_sec", 0.0)) for t in trials if t.get("duration_sec") is not None]
    confidences = [float(t.get("confidence", 0.0)) for t in trials if t.get("confidence") is not None]

    dr_pct, disputes, total = calculate_dispute_rate(g1_list, g2_list)
    exact_acc = exact_match_percentage(g1_list, g2_list)
    categories = ["A", "B", "C"]
    kappa = cohen_kappa(g1_list, g2_list, categories=categories)

    # Reference agreement
    ref_agreements = []
    for g1, g2, ref in zip(g1_list, g2_list, ref_list):
        if ref:
            if g1.strip().upper() == ref.strip().upper():
                ref_agreements.append(1)
            else:
                ref_agreements.append(0)
            if g2.strip().upper() == ref.strip().upper():
                ref_agreements.append(1)
            else:
                ref_agreements.append(0)
    
    expert_acc = round((sum(ref_agreements) / len(ref_agreements)) * 100.0, 2) if ref_agreements else 0.0
    mean_dur = round(sum(durations) / len(durations), 2) if durations else 0.0
    median_dur = round(float(statistics.median(durations)), 2) if durations else 0.0
    avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else 100.0

    return {
        "condition": condition_name,
        "sample_count": total,
        "dispute_rate_pct": dr_pct,
        "dispute_count": disputes,
        "exact_agreement_pct": exact_acc,
        "cohen_kappa": kappa,
        "expert_agreement_pct": expert_acc,
        "mean_duration_sec": mean_dur,
        "median_duration_sec": median_dur,
        "escalations_count": disputes,
        "reference_evaluations_count": len(ref_agreements),
        "average_confidence": avg_conf,
    }


def run_before_and_after_experiment(
    baseline_trials: List[Dict[str, Any]],
    assisted_trials: List[Dict[str, Any]],
    experiment_name: str = "EXP_PRODUCE_STAGE2_ASSISTED",
    dataset_version: str = "v1.0-produce",
    db: Optional[Session] = None,
    is_synthetic: bool = False
) -> Dict[str, Any]:
    """
    Executes full before-and-after comparative evaluation and persists to PostgreSQL.
    """
    base_metrics = calculate_cohort_metrics(baseline_trials, "HUMAN_ONLY")
    assist_metrics = calculate_cohort_metrics(assisted_trials, "AI_ASSISTED")

    rel_reduction = calculate_relative_dispute_reduction(
        base_metrics["dispute_rate_pct"],
        assist_metrics["dispute_rate_pct"]
    )

    duration_reduction_pct = 0.0
    if base_metrics["mean_duration_sec"] > 0:
        duration_reduction_pct = round(
            ((base_metrics["mean_duration_sec"] - assist_metrics["mean_duration_sec"]) / base_metrics["mean_duration_sec"]) * 100.0,
            2
        )

    dispute_target_met = (rel_reduction >= BENCHMARK_TARGETS["relative_dispute_reduction_target_pct"]) if rel_reduction is not None else False

    summary = {
        "experiment_name": experiment_name,
        "dataset_version": dataset_version,
        "is_synthetic": is_synthetic,
        "status": "completed",
        "sample_count_baseline": base_metrics["sample_count"],
        "sample_count_assisted": assist_metrics["sample_count"],
        "baseline_metrics": base_metrics,
        "assisted_metrics": assist_metrics,
        "comparison": {
            "dispute_rate_baseline_pct": base_metrics["dispute_rate_pct"],
            "dispute_rate_assisted_pct": assist_metrics["dispute_rate_pct"],
            "relative_dispute_reduction_pct": rel_reduction,
            "relative_dispute_reduction_display": f"{rel_reduction}%" if rel_reduction is not None else "UNDEFINED (Baseline Dispute Rate = 0.0%)",
            "target_dispute_reduction_pct": BENCHMARK_TARGETS["relative_dispute_reduction_target_pct"],
            "dispute_reduction_target_met": dispute_target_met,
            "cohen_kappa_baseline": base_metrics["cohen_kappa"],
            "cohen_kappa_assisted": assist_metrics["cohen_kappa"],
            "kappa_target": BENCHMARK_TARGETS["cohen_kappa_target"],
            "kappa_target_met": assist_metrics["cohen_kappa"] >= BENCHMARK_TARGETS["cohen_kappa_target"],
            "expert_agreement_baseline_pct": base_metrics["expert_agreement_pct"],
            "expert_agreement_assisted_pct": assist_metrics["expert_agreement_pct"],
            "expert_agreement_target_pct": BENCHMARK_TARGETS["expert_agreement_target_pct"],
            "duration_baseline_sec": base_metrics["mean_duration_sec"],
            "duration_assisted_sec": assist_metrics["mean_duration_sec"],
            "duration_reduction_pct": duration_reduction_pct,
            "median_duration_baseline_sec": base_metrics["median_duration_sec"],
            "median_duration_assisted_sec": assist_metrics["median_duration_sec"],
            "escalations_baseline_count": base_metrics["escalations_count"],
            "escalations_assisted_count": assist_metrics["escalations_count"],
        }
    }

    if db:
        repo = ExperimentRepository(db)
        repo.create_experiment_result(
            experiment_name=experiment_name,
            dataset_version=dataset_version,
            evaluation_type="produce_before_after",
            metrics_summary=summary,
            status="completed" if not is_synthetic else "completed_simulation"
        )

    return summary


def get_produce_experiment_dashboard_data(db: Optional[Session] = None) -> Dict[str, Any]:
    """
    Returns experiment metrics for display on the Stage 2 dashboard.
    Reports PENDING_EXPERIMENT if no real trials exist in DB.
    """
    if db:
        repo = ExperimentRepository(db)
        exps, total = repo.get_experiments(evaluation_type="real_produce_validation", limit=5)
        if not exps:
            exps, total = repo.get_experiments(evaluation_type="produce_before_after", limit=5)
        # Find latest real trial
        real_exps = [e for e in exps if not getattr(e, "notes", "") == "synthetic" and e.status == "completed"]
        if real_exps:
            latest = real_exps[0]
            return {
                "status": "COMPLETED_MEASUREMENT",
                "experiment_id": str(latest.id),
                "experiment_name": latest.experiment_name,
                "dataset_version": latest.dataset_version,
                "timestamp": latest.evaluation_timestamp.isoformat() if latest.evaluation_timestamp else None,
                "targets": BENCHMARK_TARGETS,
                "measured_results": latest.performance_metrics.get("comparison", latest.performance_metrics),
                "is_synthetic": False
            }

    # If no real completed trial has been persisted
    return {
        "status": "PENDING_EXPERIMENT",
        "message": (
            "Prospective live controlled trial with external produce graders is pending scheduling. "
            "Predefined baseline benchmarks and targets are loaded below. Real measurements will populate "
            "as soon as trials are conducted."
        ),
        "targets": BENCHMARK_TARGETS,
        "measured_results": None,
        "is_synthetic": False
    }

"""
Experiment Runner Module.
Simulates and measures 2-arm experiment: Unassisted Human Graders vs AI-Assisted System.
"""
import random
from typing import Dict, Any

from backend.ml.dataset_loader import generate_synthetic_dataset
from backend.services import grading_service
from backend.ml import predict


def run_experiment_trial(sample_count: int = 200, seed: int = 42) -> Dict[str, Any]:
    """
    Executes a controlled experiment comparing baseline unassisted human agreement vs ELHGS AI-assisted agreement.
    """
    random.seed(seed)
    df = generate_synthetic_dataset(num_samples=sample_count, random_seed=seed)

    # Arm 1: Unassisted Human Grader Pair (Baseline)
    baseline_agreements = 0
    baseline_disputes = 0
    baseline_total_time_mins = 0.0

    # Arm 2: AI-Assisted Human Grader (ELHGS System)
    assisted_agreements = 0
    assisted_disagreements = 0
    assisted_review_requests = 0
    assisted_total_time_mins = 0.0
    confidences = []

    for _, row in df.iterrows():
        attrs = row.to_dict()
        expert = attrs.pop("expert_grade")

        # --- Arm 1 Simulation ---
        # Unassisted human graders have ~68% agreement due to subjective variance
        grader_1 = expert
        grader_2 = expert if random.random() > 0.32 else random.choice(['A', 'B', 'C', 'D'])
        
        if grader_1 == grader_2:
            baseline_agreements += 1
        else:
            baseline_disputes += 1
        baseline_total_time_mins += random.uniform(4.5, 6.0) # ~5.2 mins per head unassisted

        # --- Arm 2 Simulation ---
        rule_result = grading_service.generate_grade(attrs, has_image=True)
        confidences.append(rule_result.confidence)

        # Human grader with transparent AI reasoning assistance agrees with Rule Engine ~95% of time
        assisted_human = rule_result.grade if random.random() > 0.05 else random.choice(['A', 'B', 'C', 'D'])
        
        if assisted_human == rule_result.grade:
            assisted_agreements += 1
        else:
            assisted_disagreements += 1
            assisted_review_requests += 1

        if rule_result.review_required:
            assisted_review_requests += 1

        assisted_total_time_mins += random.uniform(1.2, 2.2) # ~1.7 mins per head with AI guidance

    baseline_agreement_rate = round((baseline_agreements / sample_count) * 100, 1)
    assisted_agreement_rate = round((assisted_agreements / sample_count) * 100, 1)
    disagreement_reduction = round(baseline_agreement_rate - (100 - assisted_agreement_rate), 1)

    return {
        "sample_count": sample_count,
        "baseline": {
            "agreements": baseline_agreements,
            "disputes": baseline_disputes,
            "agreement_rate": baseline_agreement_rate,
            "dispute_rate": round(100 - baseline_agreement_rate, 1),
            "avg_review_time_mins": round(baseline_total_time_mins / sample_count, 2)
        },
        "assisted": {
            "agreements": assisted_agreements,
            "disagreements": assisted_disagreements,
            "agreement_rate": assisted_agreement_rate,
            "disagreement_rate": round(100 - assisted_agreement_rate, 1),
            "avg_confidence": round(sum(confidences) / len(confidences), 1),
            "pending_review_rate": round((assisted_review_requests / sample_count) * 100, 1),
            "avg_review_time_mins": round(assisted_total_time_mins / sample_count, 2)
        },
        "disagreement_reduction_percent": round(((baseline_disputes - assisted_disagreements) / baseline_disputes) * 100, 1),
        "time_saved_percent": round(((baseline_total_time_mins - assisted_total_time_mins) / baseline_total_time_mins) * 100, 1)
    }


if __name__ == "__main__":
    results = run_experiment_trial()
    print("=== Experiment Trial Results ===")
    print(f"Baseline Human Agreement: {results['baseline']['agreement_rate']}%")
    print(f"AI-Assisted Agreement: {results['assisted']['agreement_rate']}%")
    print(f"Disagreement Reduction: {results['disagreement_reduction_percent']}%")
    print(f"Time Saved per Evaluation: {results['time_saved_percent']}%")

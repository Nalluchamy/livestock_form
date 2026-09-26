import pytest
from backend.models.experiment_result import ExperimentResult
from backend.repositories.experiment_repository import ExperimentRepository


def test_save_and_retrieve_experiment(db_session):
    repo = ExperimentRepository(db_session)
    exp = ExperimentResult(
        experiment_name="test_real_eval_01",
        dataset_version="real-v1.0",
        model_version="rule-v1.0+dt-v1.0",
        evaluation_type="retrospective_real",
        status="completed",
        dataset_sample_count=120,
        test_sample_count=18,
        performance_metrics={"rule_engine": {"accuracy": 83.33, "cohen_kappa": 0.72}},
        expert_agreement_metrics={"human_baseline_inter_rater": {"cohen_kappa": 0.85}},
        confidence_distribution={"mean": 92.4},
        error_category_counts={"borderline_bcs": 2}
    )

    saved = repo.save_experiment_result(exp)
    assert saved.id is not None

    fetched = repo.get_experiment_by_id(saved.id)
    assert fetched is not None
    assert fetched.experiment_name == "test_real_eval_01"
    assert fetched.performance_metrics["rule_engine"]["accuracy"] == 83.33
    assert fetched.test_sample_count == 18


def test_get_latest_experiment(db_session):
    repo = ExperimentRepository(db_session)
    from datetime import datetime, timezone, timedelta
    base_time = datetime(2026, 9, 25, 12, 0, 0, tzinfo=timezone.utc)
    exp1 = ExperimentResult(
        experiment_name="run_01",
        dataset_version="v1",
        model_version="v1",
        evaluation_type="synthetic",
        status="completed",
        evaluation_timestamp=base_time,
        dataset_sample_count=50,
        test_sample_count=10,
        performance_metrics={},
        expert_agreement_metrics={},
        confidence_distribution={},
        error_category_counts={}
    )
    exp2 = ExperimentResult(
        experiment_name="run_02",
        dataset_version="v2",
        model_version="v2",
        evaluation_type="retrospective_real",
        status="completed",
        evaluation_timestamp=base_time + timedelta(minutes=5),
        dataset_sample_count=100,
        test_sample_count=15,
        performance_metrics={"accuracy": 90.0},
        expert_agreement_metrics={},
        confidence_distribution={},
        error_category_counts={}
    )
    repo.save_experiment_result(exp1)
    repo.save_experiment_result(exp2)

    latest = repo.get_latest_experiment()
    assert latest is not None
    assert latest.experiment_name == "run_02"

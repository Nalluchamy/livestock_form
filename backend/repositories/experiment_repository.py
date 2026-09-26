import uuid
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from backend.models.experiment_result import ExperimentResult


class ExperimentRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_experiment_result(self, experiment: ExperimentResult) -> ExperimentResult:
        """Persists a new evaluation experiment result."""
        self.db.add(experiment)
        self.db.commit()
        self.db.refresh(experiment)
        return experiment

    def create_experiment_result(
        self,
        experiment_name: str,
        dataset_version: str,
        evaluation_type: str,
        metrics_summary: Dict[str, Any],
        model_version: str = "1.0.0-real",
        status: Optional[str] = None
    ) -> ExperimentResult:
        """Helper to instantiate and persist an ExperimentResult."""
        stat = (status or metrics_summary.get("status", "completed")).lower()
        experiment = ExperimentResult(
            experiment_name=experiment_name,
            dataset_version=dataset_version,
            model_version=model_version,
            evaluation_type=evaluation_type,
            status=stat,
            dataset_sample_count=metrics_summary.get("train_samples", 0) + metrics_summary.get("test_samples", 0),
            test_sample_count=metrics_summary.get("test_samples", 0),
            performance_metrics=metrics_summary,
            expert_agreement_metrics={},
            confidence_distribution={},
            error_category_counts={}
        )
        return self.save_experiment_result(experiment)

    def get_experiment_by_id(self, exp_id: uuid.UUID) -> Optional[ExperimentResult]:
        """Fetches a specific experiment by ID."""
        stmt = select(ExperimentResult).where(ExperimentResult.id == exp_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_experiments(
        self,
        evaluation_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[ExperimentResult], int]:
        """Fetches experiments with optional evaluation_type filter, pagination, and total count."""
        stmt = select(ExperimentResult)
        count_stmt = select(func.count(ExperimentResult.id))

        if evaluation_type:
            stmt = stmt.where(ExperimentResult.evaluation_type == evaluation_type)
            count_stmt = count_stmt.where(ExperimentResult.evaluation_type == evaluation_type)

        stmt = stmt.order_by(
            desc(ExperimentResult.evaluation_timestamp),
            desc(ExperimentResult.created_at)
        ).offset(skip).limit(limit)
        results = list(self.db.execute(stmt).scalars().all())
        total = self.db.execute(count_stmt).scalar_one()

        return results, total

    def get_latest_experiment(self, evaluation_type: Optional[str] = None) -> Optional[ExperimentResult]:
        """Fetches the most recent completed experiment."""
        stmt = select(ExperimentResult)
        if evaluation_type:
            stmt = stmt.where(ExperimentResult.evaluation_type == evaluation_type)
        stmt = stmt.order_by(
            desc(ExperimentResult.evaluation_timestamp),
            desc(ExperimentResult.created_at)
        ).limit(1)
        return self.db.execute(stmt).scalar_one_or_none()

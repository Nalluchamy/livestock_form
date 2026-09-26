import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy import String, DateTime, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from backend.database.base import Base


class ExperimentResult(Base):
    """
    Persistent table for machine learning and rule engine evaluation experiments.
    Stores comprehensive benchmarking runs across synthetic datasets, retrospective real-data
    evaluations, and prospective human-assisted field studies.
    """
    __tablename__ = "experiment_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    experiment_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    dataset_version: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    
    evaluation_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Evaluation typology: 'synthetic', 'retrospective_real', or 'prospective_human_assisted'
    evaluation_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    
    # Status: 'completed', 'pending_real_data', 'failed'
    status: Mapped[str] = mapped_column(String(50), default="completed", index=True, nullable=False)

    # Sample Counts
    dataset_sample_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    test_sample_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Granular Metrics in JSON
    performance_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    expert_agreement_metrics: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    confidence_distribution: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error_category_counts: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def __repr__(self) -> str:
        return f"<ExperimentResult(id={self.id}, name={self.experiment_name}, type={self.evaluation_type}, status={self.status})>"

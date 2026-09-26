"""persistent reviews and experiments

Revision ID: 0002_persistent_reviews_and_experiments
Revises: 0001_initial_schema
Create Date: 2026-09-24 20:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0002_persistent_reviews_and_experiments'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create disagreement_reviews
    op.create_table(
        'disagreement_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('grading_event_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('fact_grading_events.id', ondelete='SET NULL'), nullable=True),
        sa.Column('original_human_grade', sa.String(length=50), nullable=False),
        sa.Column('original_system_grade', sa.String(length=50), nullable=False),
        sa.Column('expert_grade', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('reviewer_id', sa.String(length=255), nullable=True),
        sa.Column('reviewer_action', sa.String(length=100), nullable=True),
        sa.Column('reviewer_final_decision', sa.String(length=50), nullable=True),
        sa.Column('reviewer_rationale', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f('ix_disagreement_reviews_grading_event_id'), 'disagreement_reviews', ['grading_event_id'], unique=False)
    op.create_index(op.f('ix_disagreement_reviews_status'), 'disagreement_reviews', ['status'], unique=False)

    # 2. Create experiment_results
    op.create_table(
        'experiment_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('experiment_name', sa.String(length=255), nullable=False),
        sa.Column('dataset_version', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=100), nullable=False),
        sa.Column('evaluation_timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('evaluation_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.Column('dataset_sample_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('test_sample_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('performance_metrics', sa.JSON(), nullable=False),
        sa.Column('expert_agreement_metrics', sa.JSON(), nullable=False),
        sa.Column('confidence_distribution', sa.JSON(), nullable=False),
        sa.Column('error_category_counts', sa.JSON(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_experiment_results_experiment_name'), 'experiment_results', ['experiment_name'], unique=False)
    op.create_index(op.f('ix_experiment_results_evaluation_type'), 'experiment_results', ['evaluation_type'], unique=False)
    op.create_index(op.f('ix_experiment_results_status'), 'experiment_results', ['status'], unique=False)


def downgrade() -> None:
    op.drop_table('experiment_results')
    op.drop_table('disagreement_reviews')

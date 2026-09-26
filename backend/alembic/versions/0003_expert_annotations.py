"""expert annotations table

Revision ID: 0003_expert_annotations
Revises: 0002_persistent_reviews_and_experiments
Create Date: 2026-09-24 23:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003_expert_annotations'
down_revision: Union[str, None] = '0002_persistent_reviews_and_experiments'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'expert_annotations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('sample_id', sa.String(length=64), nullable=False),
        sa.Column('image_path', sa.String(length=500), nullable=False),
        sa.Column('species', sa.String(length=32), server_default='cattle', nullable=False),
        sa.Column('body_condition', sa.Float(), nullable=True),
        sa.Column('coat_quality', sa.String(length=32), nullable=True),
        sa.Column('eye_condition', sa.String(length=32), nullable=True),
        sa.Column('wound_presence', sa.String(length=32), nullable=True),
        sa.Column('mobility', sa.String(length=32), nullable=True),
        sa.Column('appetite', sa.String(length=32), nullable=True),
        sa.Column('weight_if_available', sa.Float(), nullable=True),
        sa.Column('expert_grader_1_id', sa.String(length=100), nullable=True),
        sa.Column('expert_grade_1', sa.String(length=10), nullable=True),
        sa.Column('expert_grade_1_notes', sa.Text(), nullable=True),
        sa.Column('expert_grade_1_submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expert_grader_2_id', sa.String(length=100), nullable=True),
        sa.Column('expert_grade_2', sa.String(length=10), nullable=True),
        sa.Column('expert_grade_2_notes', sa.Text(), nullable=True),
        sa.Column('expert_grade_2_submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('final_consensus_grade', sa.String(length=10), nullable=True),
        sa.Column('consensus_reviewer_id', sa.String(length=100), nullable=True),
        sa.Column('consensus_rationale', sa.Text(), nullable=True),
        sa.Column('consensus_reached_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('annotation_status', sa.String(length=50), server_default='PENDING', nullable=False),
        sa.Column('quality_flagged', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('quality_issue_reason', sa.Text(), nullable=True),
        sa.Column('flagged_by_id', sa.String(length=100), nullable=True),
        sa.Column('flagged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(op.f('ix_expert_annotations_sample_id'), 'expert_annotations', ['sample_id'], unique=True)
    op.create_index(op.f('ix_expert_annotations_annotation_status'), 'expert_annotations', ['annotation_status'], unique=False)
    op.create_index(op.f('ix_expert_annotations_quality_flagged'), 'expert_annotations', ['quality_flagged'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_expert_annotations_quality_flagged'), table_name='expert_annotations')
    op.drop_index(op.f('ix_expert_annotations_annotation_status'), table_name='expert_annotations')
    op.drop_index(op.f('ix_expert_annotations_sample_id'), table_name='expert_annotations')
    op.drop_table('expert_annotations')

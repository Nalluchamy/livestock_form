"""initial schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-08-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create dim_sample
    op.create_table('dim_sample',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('farm_location', sa.String(length=255), nullable=False),
        sa.Column('species', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dim_sample_farm_location'), 'dim_sample', ['farm_location'], unique=False)
    op.create_index(op.f('ix_dim_sample_species'), 'dim_sample', ['species'], unique=False)

    # Create dim_grader
    op.create_table('dim_grader',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dim_grader_role'), 'dim_grader', ['role'], unique=False)
    op.create_index(op.f('ix_dim_grader_username'), 'dim_grader', ['username'], unique=True)

    # Create dim_image
    op.create_table('dim_image',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_path', sa.String(length=512), nullable=False),
        sa.Column('exif_stripped', sa.Boolean(), nullable=False),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('resolution', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('file_path')
    )

    # Create dim_criterion
    op.create_table('dim_criterion',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('attribute_name', sa.String(length=100), nullable=False),
        sa.Column('rule_condition', sa.String(length=255), nullable=True),
        sa.Column('measured_value', sa.String(length=100), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dim_criterion_attribute_name'), 'dim_criterion', ['attribute_name'], unique=False)

    # Create fact_grading_events
    op.create_table('fact_grading_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sample_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('grader_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('image_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('criterion_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('human_grade', sa.String(length=50), nullable=True),
        sa.Column('ai_grade', sa.String(length=50), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('review_status', sa.String(length=50), nullable=False),
        sa.Column('client_offline_id', sa.String(length=255), nullable=True),
        sa.Column('is_synced', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['criterion_id'], ['dim_criterion.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['grader_id'], ['dim_grader.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['image_id'], ['dim_image.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['sample_id'], ['dim_sample.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fact_grading_events_client_offline_id'), 'fact_grading_events', ['client_offline_id'], unique=False)
    op.create_index(op.f('ix_fact_grading_events_criterion_id'), 'fact_grading_events', ['criterion_id'], unique=False)
    op.create_index(op.f('ix_fact_grading_events_grader_id'), 'fact_grading_events', ['grader_id'], unique=False)
    op.create_index(op.f('ix_fact_grading_events_image_id'), 'fact_grading_events', ['image_id'], unique=False)
    op.create_index(op.f('ix_fact_grading_events_is_synced'), 'fact_grading_events', ['is_synced'], unique=False)
    op.create_index(op.f('ix_fact_grading_events_review_status'), 'fact_grading_events', ['review_status'], unique=False)
    op.create_index(op.f('ix_fact_grading_events_sample_id'), 'fact_grading_events', ['sample_id'], unique=False)


def downgrade() -> None:
    op.drop_table('fact_grading_events')
    op.drop_table('dim_criterion')
    op.drop_table('dim_image')
    op.drop_table('dim_grader')
    op.drop_table('dim_sample')

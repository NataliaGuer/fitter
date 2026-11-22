"""exercises

Exercise catalog from the RepDB dataset (ALL-001-BE-01, D-016).

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

import app.core.types

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Single row (id = 1): fingerprint of the last dataset load.
    op.create_table(
        "exercise_catalog_state",
        sa.Column("id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("fingerprint", sa.Text(), nullable=False),
        sa.Column("dataset_version", sa.Text(), nullable=False),
        sa.Column("synced_at", app.core.types.UTCDateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercise_catalog_state")),
    )
    # Shared catalog: no user_id. The primary key is the dataset id (slug).
    op.create_table(
        "exercises",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name_it", sa.Text(), nullable=False),
        sa.Column("name_en", sa.Text(), nullable=False),
        sa.Column("search_text", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("body_part", sa.Text(), nullable=True),
        sa.Column("equipment", sa.Text(), nullable=True),
        sa.Column("difficulty", sa.Text(), nullable=True),
        sa.Column("force_type", sa.Text(), nullable=True),
        sa.Column("mechanic", sa.Text(), nullable=True),
        sa.Column("met", sa.Float(), nullable=True),
        sa.Column("is_unilateral", sa.Boolean(), nullable=False),
        sa.Column("is_bodyweight", sa.Boolean(), nullable=False),
        sa.Column("primary_muscles", sa.JSON(), nullable=False),
        sa.Column("secondary_muscles", sa.JSON(), nullable=False),
        sa.Column("image_start", sa.Text(), nullable=True),
        sa.Column("image_peak", sa.Text(), nullable=True),
        sa.Column("image_main", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exercises")),
    )
    with op.batch_alter_table("exercises", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_exercises_body_part"), ["body_part"], unique=False)
        batch_op.create_index(batch_op.f("ix_exercises_equipment"), ["equipment"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("exercises", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_exercises_equipment"))
        batch_op.drop_index(batch_op.f("ix_exercises_body_part"))

    op.drop_table("exercises")
    op.drop_table("exercise_catalog_state")

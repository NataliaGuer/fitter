"""users sessions

Users and login sessions (CORE-002-BE-01, D-009).

Revision ID: 0001
Revises:
Create Date: 2026-11-15

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

import app.core.types

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        # NOCASE: nickname unique regardless of letter case
        sa.Column("nickname", sa.Text(collation="NOCASE"), nullable=False),
        sa.Column("pin_hash", sa.Text(), nullable=False),
        sa.Column("created_at", app.core.types.UTCDateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("nickname", name=op.f("uq_users_nickname")),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", app.core.types.UTCDateTime(), nullable=False),
        sa.Column("last_seen_at", app.core.types.UTCDateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_sessions_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("token_hash", name=op.f("uq_sessions_token_hash")),
    )
    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_sessions_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("sessions", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_sessions_user_id"))

    op.drop_table("sessions")
    op.drop_table("users")

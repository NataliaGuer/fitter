"""Migration 0002 (ALL-001-BE-01): exercise catalog tables."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import Engine, inspect, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.core.db import make_engine
from app.exercises.models import Exercise

BACKEND_DIR = Path(__file__).resolve().parent.parent
CATALOG_TABLES = {"exercises", "exercise_catalog_state"}


def _upgrade(engine: Engine, revision: str) -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


def _downgrade(engine: Engine, revision: str) -> None:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, revision)


@pytest.fixture
def empty_engine(tmp_path: Path) -> Iterator[Engine]:
    """Engine on a new SQLite file with no migration applied."""
    engine = make_engine(f"sqlite:///{tmp_path / 'migration.db'}")
    yield engine
    engine.dispose()


def test_upgrade_head_creates_catalog_tables_and_indexes(empty_engine: Engine) -> None:
    _upgrade(empty_engine, "head")

    inspector = inspect(empty_engine)
    assert CATALOG_TABLES <= set(inspector.get_table_names())

    indexes = {index["name"]: index["column_names"] for index in inspector.get_indexes("exercises")}
    assert indexes["ix_exercises_body_part"] == ["body_part"]
    assert indexes["ix_exercises_equipment"] == ["equipment"]

    assert inspector.get_pk_constraint("exercises")["constrained_columns"] == ["id"]
    assert inspector.get_pk_constraint("exercise_catalog_state")["constrained_columns"] == ["id"]


def test_upgrade_from_0001_keeps_existing_user(empty_engine: Engine) -> None:
    _upgrade(empty_engine, "0001")
    assert not CATALOG_TABLES & set(inspect(empty_engine).get_table_names())
    with Session(empty_engine) as session:
        session.add(User(nickname="Mario", pin_hash="not-a-real-hash"))
        session.commit()

    _upgrade(empty_engine, "head")

    assert CATALOG_TABLES <= set(inspect(empty_engine).get_table_names())
    with Session(empty_engine) as session:
        user = session.scalars(select(User)).one()
        assert user.nickname == "Mario"
        assert user.pin_hash == "not-a-real-hash"


def test_downgrade_to_0001_removes_catalog_tables(empty_engine: Engine) -> None:
    _upgrade(empty_engine, "head")

    _downgrade(empty_engine, "0001")

    tables = set(inspect(empty_engine).get_table_names())
    assert not CATALOG_TABLES & tables
    assert {"users", "sessions"} <= tables


def test_exercise_roundtrip(db: Session) -> None:
    db.add(
        Exercise(
            id="test-press",
            name_it="Distensioni di prova",
            name_en="Test Press",
            search_text="distensioni di prova test press",
            category="strength",
            body_part="shoulders",
            equipment=None,
            is_unilateral=False,
            is_bodyweight=True,
            primary_muscles=["anterior_deltoid"],
            secondary_muscles=[],
        )
    )
    db.commit()
    db.expire_all()

    stored = db.get(Exercise, "test-press")
    assert stored is not None
    assert stored.is_active is True
    assert stored.equipment is None
    assert stored.primary_muscles == ["anterior_deltoid"]
    assert stored.secondary_muscles == []

from datetime import UTC

import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, delete, exc, func, select
from sqlalchemy.orm import Session

from app.auth.models import User, UserSession
from app.core.db import Base


def _user(nickname: str) -> User:
    return User(nickname=nickname, pin_hash="not-a-real-hash")


def test_nickname_unique_case_insensitive(db: Session) -> None:
    db.add(_user("Mario"))
    db.commit()

    db.add(_user("mario"))
    with pytest.raises(exc.IntegrityError):
        db.commit()


def test_nickname_lookup_case_insensitive(db: Session) -> None:
    db.add(_user("Mario"))
    db.commit()

    found = db.scalars(select(User).where(User.nickname == "MARIO")).one()
    assert found.nickname == "Mario"


def test_delete_user_cascades_sessions(db: Session) -> None:
    user = _user("anna")
    user.sessions.append(UserSession(token_hash="a" * 64))
    user.sessions.append(UserSession(token_hash="b" * 64))
    db.add(user)
    db.commit()

    # Plain SQL delete: the cascade must come from the DB (ON DELETE CASCADE + foreign_keys=ON).
    db.execute(delete(User).where(User.id == user.id))
    db.commit()

    assert db.scalar(select(func.count()).select_from(UserSession)) == 0


def test_session_requires_existing_user(db: Session) -> None:
    db.add(UserSession(token_hash="c" * 64, user_id=999))
    with pytest.raises(exc.IntegrityError):
        db.commit()


def test_session_token_hash_unique(db: Session) -> None:
    user = _user("luca")
    user.sessions.append(UserSession(token_hash="d" * 64))
    user.sessions.append(UserSession(token_hash="d" * 64))
    db.add(user)
    with pytest.raises(exc.IntegrityError):
        db.commit()


def test_timestamps_default_to_aware_utc(db: Session) -> None:
    user = _user("sara")
    user.sessions.append(UserSession(token_hash="e" * 64))
    db.add(user)
    db.commit()
    db.expire_all()

    stored = db.scalars(select(User)).one()
    assert stored.created_at.tzinfo is UTC
    assert stored.sessions[0].last_seen_at.tzinfo is UTC


def test_models_match_migrations(engine: Engine) -> None:
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        diff = compare_metadata(context, Base.metadata)
    assert diff == []

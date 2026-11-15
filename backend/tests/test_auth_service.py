from datetime import timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.models import User, UserSession


def test_pin_stored_as_argon2_hash(db: Session) -> None:
    user = service.register_user(db, "mario", "4821")

    stored = db.scalars(select(User).where(User.id == user.id)).one()
    assert stored.pin_hash.startswith("$argon2id$")
    assert "4821" not in stored.pin_hash


def test_register_duplicate_nickname_case_insensitive_raises(db: Session) -> None:
    service.register_user(db, "Mario", "1234")

    with pytest.raises(service.NicknameTakenError):
        service.register_user(db, "MARIO", "5678")

    # The session is still usable after the rollback.
    assert db.scalars(select(User)).one().nickname == "Mario"


def test_authenticate_ok_case_insensitive(db: Session) -> None:
    user = service.register_user(db, "Mario", "1234")

    assert service.authenticate(db, "mario", "1234") == user


def test_authenticate_wrong_pin_returns_none(db: Session) -> None:
    service.register_user(db, "mario", "1234")

    assert service.authenticate(db, "mario", "1235") is None


def test_authenticate_unknown_nickname_returns_none(db: Session) -> None:
    assert service.authenticate(db, "nessuno", "1234") is None


def test_authenticate_unknown_nickname_still_verifies_a_hash(
    db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[str] = []
    real_verify = service.verify_pin

    def spy(pin_hash: str, pin: str) -> bool:
        calls.append(pin_hash)
        return real_verify(pin_hash, pin)

    monkeypatch.setattr(service, "verify_pin", spy)

    service.authenticate(db, "nessuno", "1234")

    assert len(calls) == 1
    assert calls[0].startswith("$argon2id$")


def test_verify_pin_with_invalid_hash_returns_false() -> None:
    assert service.verify_pin("not-a-hash", "1234") is False


def test_session_token_not_stored_in_clear(db: Session) -> None:
    user = service.register_user(db, "mario", "1234")

    token = service.create_session(db, user)

    stored = db.scalars(select(UserSession)).one()
    assert stored.token_hash != token
    assert token not in stored.token_hash
    assert stored.token_hash == service.hash_token(token)
    assert len(token) >= 43  # 32 random bytes, base64url


def test_get_user_by_token(db: Session) -> None:
    user = service.register_user(db, "mario", "1234")
    token = service.create_session(db, user)

    assert service.get_user_by_token(db, token) == user
    assert service.get_user_by_token(db, "token-inventato") is None


def test_each_session_has_its_own_token(db: Session) -> None:
    user = service.register_user(db, "mario", "1234")

    assert service.create_session(db, user) != service.create_session(db, user)


def test_last_seen_updated_at_most_daily(db: Session) -> None:
    user = service.register_user(db, "mario", "1234")
    token = service.create_session(db, user)
    session = db.scalars(select(UserSession)).one()
    created = session.last_seen_at

    service.get_user_by_token(db, token, now=created + timedelta(hours=23))
    db.refresh(session)
    assert session.last_seen_at == created

    later = created + timedelta(hours=25)
    service.get_user_by_token(db, token, now=later)
    db.refresh(session)
    assert session.last_seen_at == later


def test_deleted_session_token_is_invalid(db: Session) -> None:
    user = service.register_user(db, "mario", "1234")
    token = service.create_session(db, user)
    other_token = service.create_session(db, user)

    service.delete_session(db, token)

    assert service.get_user_by_token(db, token) is None
    assert service.get_user_by_token(db, other_token) == user


def test_delete_session_is_idempotent(db: Session) -> None:
    service.delete_session(db, "token-inventato")

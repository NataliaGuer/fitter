"""Authentication domain logic: PIN hashing and login sessions (CORE-002, D-009).

- PINs are stored only as argon2id hashes.
- Session tokens are random and opaque; only their SHA-256 is stored.
- Sessions never expire server-side: they end only with logout.
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from functools import cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from sqlalchemy import delete, exc, select
from sqlalchemy.orm import Session

from app.auth.models import User, UserSession

TOKEN_BYTES = 32
LAST_SEEN_UPDATE_INTERVAL = timedelta(hours=24)

_hasher = PasswordHasher()


class NicknameTakenError(Exception):
    """The nickname is already used (case-insensitive)."""


def hash_pin(pin: str) -> str:
    return _hasher.hash(pin)


def verify_pin(pin_hash: str, pin: str) -> bool:
    try:
        return _hasher.verify(pin_hash, pin)
    except (VerificationError, InvalidHashError):
        return False


@cache
def _dummy_pin_hash() -> str:
    # Verified when the nickname does not exist, so that response times are similar.
    return hash_pin(secrets.token_hex(8))


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def register_user(db: Session, nickname: str, pin: str) -> User:
    user = User(nickname=nickname, pin_hash=hash_pin(pin))
    db.add(user)
    try:
        db.commit()
    except exc.IntegrityError as error:
        db.rollback()
        raise NicknameTakenError(nickname) from error
    return user


def authenticate(db: Session, nickname: str, pin: str) -> User | None:
    """Return the user if nickname and PIN match, otherwise None."""
    user = db.scalars(select(User).where(User.nickname == nickname)).one_or_none()
    if user is None:
        verify_pin(_dummy_pin_hash(), pin)
        return None
    if not verify_pin(user.pin_hash, pin):
        return None
    return user


def create_session(db: Session, user: User) -> str:
    """Create a session and return the token in clear (to be put in the cookie only)."""
    token = secrets.token_urlsafe(TOKEN_BYTES)
    db.add(UserSession(user_id=user.id, token_hash=hash_token(token)))
    db.commit()
    return token


def get_user_by_token(db: Session, token: str, now: datetime | None = None) -> User | None:
    """Return the session's user, refreshing last_seen_at at most once every 24 hours."""
    session = db.scalars(
        select(UserSession).where(UserSession.token_hash == hash_token(token))
    ).one_or_none()
    if session is None:
        return None

    now = now or datetime.now(UTC)
    if now - session.last_seen_at >= LAST_SEEN_UPDATE_INTERVAL:
        session.last_seen_at = now
        db.commit()
    return session.user


def delete_session(db: Session, token: str) -> None:
    """Delete the session for this token, if any (idempotent)."""
    db.execute(delete(UserSession).where(UserSession.token_hash == hash_token(token)))
    db.commit()

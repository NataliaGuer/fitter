"""Database engine, ORM base class and FastAPI session dependency."""

from collections.abc import Iterator
from functools import lru_cache
from typing import Any

from sqlalchemy import Engine, MetaData, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

# Named constraints: SQLite batch migrations (render_as_batch) need names to alter/drop them.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def _set_sqlite_pragmas(dbapi_connection: Any, _connection_record: Any) -> None:
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
    finally:
        cursor.close()


def make_engine(url: str) -> Engine:
    """Create an engine with the PRAGMAs required on every SQLite connection."""
    engine = create_engine(url)
    event.listen(engine, "connect", _set_sqlite_pragmas)
    return engine


@lru_cache
def get_engine() -> Engine:
    return make_engine(get_settings().database_url)


@lru_cache
def _get_sessionmaker() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine())


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one DB session per request, closed at the end."""
    with _get_sessionmaker()() as session:
        yield session

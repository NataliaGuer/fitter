"""Alembic environment (D-003): SQLite with render_as_batch, URL from app settings."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

from app.core.config import get_settings
from app.core.db import Base, make_engine

# Import model modules here so autogenerate sees their tables.
import app.auth.models  # noqa: F401, E402
import app.exercises.models  # noqa: F401, E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def _configure(**kwargs: object) -> None:
    context.configure(
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
        **kwargs,  # type: ignore[arg-type]
    )


def run_migrations_offline() -> None:
    _configure(url=get_settings().database_url, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def _run_with_connection(connection: Connection) -> None:
    _configure(connection=connection)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Tests pass an existing connection (see tests/conftest.py).
    connection = config.attributes.get("connection")
    if connection is not None:
        _run_with_connection(connection)
        return

    engine = make_engine(get_settings().database_url)
    try:
        with engine.connect() as connection:
            _run_with_connection(connection)
    finally:
        engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

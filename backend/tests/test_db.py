from datetime import UTC, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Column, Engine, Integer, MetaData, Table, exc, insert, select

from app.core.types import UTCDateTime


def test_pragmas_wal_and_foreign_keys(engine: Engine) -> None:
    with engine.connect() as connection:
        assert connection.exec_driver_sql("PRAGMA journal_mode").scalar() == "wal"
        assert connection.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


@pytest.fixture
def events_table(engine: Engine) -> Table:
    metadata = MetaData()
    table = Table(
        "test_events",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("at", UTCDateTime, nullable=True),
    )
    metadata.create_all(engine)
    return table


def test_utc_datetime_roundtrip_returns_aware_utc(engine: Engine, events_table: Table) -> None:
    rome_summer = timezone(timedelta(hours=2))
    value = datetime(2026, 7, 1, 12, 30, tzinfo=rome_summer)

    with engine.begin() as connection:
        connection.execute(insert(events_table).values(id=1, at=value))
        stored = connection.execute(select(events_table.c.at)).scalar_one()

    assert stored.tzinfo is UTC
    assert stored == value
    assert stored.hour == 10


def test_utc_datetime_stores_naive_utc_in_sqlite(engine: Engine, events_table: Table) -> None:
    value = datetime(2026, 1, 15, 8, 0, tzinfo=UTC)

    with engine.begin() as connection:
        connection.execute(insert(events_table).values(id=1, at=value))
        raw = connection.exec_driver_sql("SELECT at FROM test_events").scalar_one()

    assert raw.startswith("2026-01-15 08:00:00")


def test_utc_datetime_rejects_naive(engine: Engine, events_table: Table) -> None:
    with engine.begin() as connection, pytest.raises(exc.StatementError):
        connection.execute(insert(events_table).values(id=1, at=datetime(2026, 1, 15, 8, 0)))


def test_utc_datetime_allows_null(engine: Engine, events_table: Table) -> None:
    with engine.begin() as connection:
        connection.execute(insert(events_table).values(id=1, at=None))
        assert connection.execute(select(events_table.c.at)).scalar_one() is None


def test_example_items_endpoint_removed(client: TestClient) -> None:
    assert client.get("/items/1").status_code == 404

"""Application settings read from environment variables."""

import os
from dataclasses import dataclass
from functools import lru_cache

DEFAULT_DATABASE_URL = "sqlite:////data/fitter.db"
DEFAULT_EXERCISES_DATASET_DIR = "/backend/dataset"


def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Invalid boolean value for {name}: {value!r}")


@dataclass(frozen=True)
class Settings:
    database_url: str
    cookie_secure: bool
    exercises_dataset_dir: str = DEFAULT_EXERCISES_DATASET_DIR


@lru_cache
def get_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("DATABASE_URL") or DEFAULT_DATABASE_URL,
        cookie_secure=_env_bool("COOKIE_SECURE", default=True),
        exercises_dataset_dir=(
            os.environ.get("EXERCISES_DATASET_DIR") or DEFAULT_EXERCISES_DATASET_DIR
        ),
    )

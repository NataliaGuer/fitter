"""Exercise catalog loaded from the RepDB dataset (ALL-001, D-016).

Shared by all users and read-only from the API: no ``user_id``.
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.core.types import UTCDateTime


class Exercise(Base):
    __tablename__ = "exercises"

    # Dataset id (slug, e.g. "arnold-press"): stable key for upserts and future foreign keys.
    id: Mapped[str] = mapped_column(Text, primary_key=True)
    name_it: Mapped[str] = mapped_column(Text)
    name_en: Mapped[str] = mapped_column(Text)
    # Italian + English names, casefolded and without accents (see D-016, search).
    search_text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    body_part: Mapped[str | None] = mapped_column(Text, index=True)
    equipment: Mapped[str | None] = mapped_column(Text, index=True)
    difficulty: Mapped[str | None] = mapped_column(Text)
    force_type: Mapped[str | None] = mapped_column(Text)
    mechanic: Mapped[str | None] = mapped_column(Text)
    met: Mapped[float | None] = mapped_column(Float)
    is_unilateral: Mapped[bool] = mapped_column(Boolean)
    is_bodyweight: Mapped[bool] = mapped_column(Boolean)
    # Lists of muscle codes from the dataset.
    primary_muscles: Mapped[list[str]] = mapped_column(JSON)
    secondary_muscles: Mapped[list[str]] = mapped_column(JSON)
    # File names only (e.g. "arnold-press-peak.webp"): where they are served is up to the frontend.
    image_start: Mapped[str | None] = mapped_column(Text)
    image_peak: Mapped[str | None] = mapped_column(Text)
    image_main: Mapped[str | None] = mapped_column(Text)
    # False when the exercise is no longer in the dataset: rows are never deleted.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ExerciseCatalogState(Base):
    """Single row (id = 1) with the fingerprint of the last dataset load."""

    __tablename__ = "exercise_catalog_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    fingerprint: Mapped[str] = mapped_column(Text)
    dataset_version: Mapped[str] = mapped_column(Text)
    synced_at: Mapped[datetime] = mapped_column(UTCDateTime)

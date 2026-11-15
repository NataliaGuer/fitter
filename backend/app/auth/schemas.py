"""Request/response models for /api/auth (contract in CORE-002-BE-01)."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# ASCII only: [0-9] instead of \d, because in Pydantic's regex engine \d also matches non-ASCII digits.
NICKNAME_PATTERN = r"^[A-Za-z0-9_.-]{3,30}$"
PIN_PATTERN = r"^[0-9]{4}$"


class Credentials(BaseModel):
    nickname: Annotated[str, Field(pattern=NICKNAME_PATTERN, examples=["mario"])]
    pin: Annotated[str, Field(pattern=PIN_PATTERN, examples=["1234"])]


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nickname: str

"""/api/auth endpoints (CORE-002-BE-01). The frontend relies on status codes, not on `detail`."""

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth import service
from app.auth.schemas import Credentials, UserOut
from app.core.config import get_settings
from app.core.db import get_db

COOKIE_NAME = "fitter_session"
# 400 days: the maximum cookie lifetime allowed by browsers (D-009).
COOKIE_MAX_AGE = 400 * 24 * 60 * 60

router = APIRouter(tags=["auth"])

DbSession = Annotated[Session, Depends(get_db)]
SessionToken = Annotated[str | None, Cookie(alias=COOKIE_NAME)]


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        COOKIE_NAME,
        token,
        max_age=COOKIE_MAX_AGE,
        path="/",
        httponly=True,
        samesite="lax",
        secure=get_settings().cookie_secure,
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(
        COOKIE_NAME,
        path="/",
        httponly=True,
        samesite="lax",
        secure=get_settings().cookie_secure,
    )


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOut,
    responses={status.HTTP_409_CONFLICT: {"description": "Nickname already in use"}},
)
def register(credentials: Credentials, response: Response, db: DbSession) -> UserOut:
    try:
        user = service.register_user(db, credentials.nickname, credentials.pin)
    except service.NicknameTakenError:
        raise HTTPException(status.HTTP_409_CONFLICT, "Nickname already in use") from None
    set_session_cookie(response, service.create_session(db, user))
    return UserOut.model_validate(user)


@router.post(
    "/login",
    response_model=UserOut,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Invalid nickname or PIN"}},
)
def login(credentials: Credentials, response: Response, db: DbSession) -> UserOut:
    user = service.authenticate(db, credentials.nickname, credentials.pin)
    if user is None:
        # Same message whether the nickname exists or not.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid nickname or PIN")
    set_session_cookie(response, service.create_session(db, user))
    return UserOut.model_validate(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, db: DbSession, token: SessionToken = None) -> None:
    """Idempotent: always 204, with or without a valid cookie."""
    if token:
        service.delete_session(db, token)
    clear_session_cookie(response)

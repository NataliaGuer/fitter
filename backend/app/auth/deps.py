"""FastAPI dependencies for authentication.

Every endpoint with personal data uses `CurrentUser` and filters its queries by `user.id`:

    @router.get("/api/workouts")
    def list_workouts(user: CurrentUser, db: DbSession) -> ...:
        ...
"""

from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status

from app.auth import service
from app.auth.models import User
from app.core.db import DbSession

COOKIE_NAME = "fitter_session"

SessionToken = Annotated[str | None, Cookie(alias=COOKIE_NAME)]


def current_user(db: DbSession, token: SessionToken = None) -> User:
    """The authenticated user, or 401 if the session cookie is missing or not valid."""
    if token:
        user = service.get_user_by_token(db, token)
        if user is not None:
            return user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")


CurrentUser = Annotated[User, Depends(current_user)]

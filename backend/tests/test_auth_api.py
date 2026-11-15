import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import router as auth_router
from app.auth.models import UserSession
from app.core.config import Settings

REGISTER = "/api/auth/register"
LOGIN = "/api/auth/login"
LOGOUT = "/api/auth/logout"
ME = "/api/auth/me"
COOKIE = "fitter_session"


def _credentials(nickname: str = "mario", pin: str = "1234") -> dict[str, str]:
    return {"nickname": nickname, "pin": pin}


def _session_count(db: Session) -> int:
    return db.scalar(select(func.count()).select_from(UserSession)) or 0


# --- register -----------------------------------------------------------------


def test_register_returns_user_and_session_cookie(client: TestClient, db: Session) -> None:
    response = client.post(REGISTER, json=_credentials("Mario"))

    assert response.status_code == 201
    body = response.json()
    assert body["nickname"] == "Mario"
    assert isinstance(body["id"], int)
    assert set(body) == {"id", "nickname"}

    cookie = response.headers.get("set-cookie", "").lower()
    assert cookie.startswith(f"{COOKIE}=")
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    assert "path=/" in cookie
    assert "max-age=34560000" in cookie
    assert _session_count(db) == 1


def test_register_duplicate_nickname_case_insensitive_409(client: TestClient) -> None:
    assert client.post(REGISTER, json=_credentials("Mario")).status_code == 201

    response = client.post(REGISTER, json=_credentials("mARIO", "9999"))

    assert response.status_code == 409
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize(
    "nickname",
    ["ab", "a" * 31, "ma rio", "niccolò", "mario!", "", " mario"],
)
def test_register_invalid_nickname_422(client: TestClient, nickname: str) -> None:
    assert client.post(REGISTER, json=_credentials(nickname)).status_code == 422


@pytest.mark.parametrize("nickname", ["abc", "a" * 30, "Mario_99", "m.r-x"])
def test_register_valid_nickname_edge_cases(client: TestClient, nickname: str) -> None:
    assert client.post(REGISTER, json=_credentials(nickname)).status_code == 201


@pytest.mark.parametrize("pin", ["123", "12345", "12a4", "١٢٣٤", " 123", ""])
def test_register_invalid_pin_422(client: TestClient, pin: str) -> None:
    assert client.post(REGISTER, json=_credentials(pin=pin)).status_code == 422


def test_register_pin_as_number_422(client: TestClient) -> None:
    response = client.post(REGISTER, json={"nickname": "mario", "pin": 1234})
    assert response.status_code == 422


def test_register_missing_fields_422(client: TestClient) -> None:
    assert client.post(REGISTER, json={"nickname": "mario"}).status_code == 422


# --- login --------------------------------------------------------------------


def test_login_ok_case_insensitive(client: TestClient, db: Session) -> None:
    client.post(REGISTER, json=_credentials("Mario"))
    client.cookies.clear()

    response = client.post(LOGIN, json=_credentials("MARIO"))

    assert response.status_code == 200
    assert response.json()["nickname"] == "Mario"
    assert response.headers.get("set-cookie", "").startswith(f"{COOKIE}=")
    assert _session_count(db) == 2


def test_login_wrong_pin_and_unknown_nickname_same_401(client: TestClient) -> None:
    client.post(REGISTER, json=_credentials("mario", "1234"))
    client.cookies.clear()

    wrong_pin = client.post(LOGIN, json=_credentials("mario", "4321"))
    unknown = client.post(LOGIN, json=_credentials("nessuno", "1234"))

    assert wrong_pin.status_code == 401
    assert unknown.status_code == 401
    assert wrong_pin.json() == unknown.json()
    assert "set-cookie" not in wrong_pin.headers
    assert "set-cookie" not in unknown.headers


def test_login_invalid_input_422(client: TestClient) -> None:
    assert client.post(LOGIN, json=_credentials(pin="12")).status_code == 422


# --- logout -------------------------------------------------------------------


def test_logout_deletes_session_and_clears_cookie(client: TestClient, db: Session) -> None:
    client.post(REGISTER, json=_credentials())
    assert _session_count(db) == 1

    response = client.post(LOGOUT)

    assert response.status_code == 204
    assert response.content == b""
    cookie = response.headers.get("set-cookie", "").lower()
    assert cookie.startswith(f'{COOKIE}=""') or cookie.startswith(f"{COOKIE}=;")
    assert "max-age=0" in cookie
    assert _session_count(db) == 0


def test_logout_only_deletes_own_session(client: TestClient, db: Session) -> None:
    client.post(REGISTER, json=_credentials("anna"))
    client.cookies.clear()
    client.post(REGISTER, json=_credentials("luca"))

    client.post(LOGOUT)

    assert _session_count(db) == 1


def test_logout_without_cookie_204(client: TestClient) -> None:
    assert client.post(LOGOUT).status_code == 204


def test_logout_with_unknown_cookie_204(client: TestClient) -> None:
    client.cookies.set(COOKIE, "token-inventato")
    assert client.post(LOGOUT).status_code == 204


# --- cookie flags -------------------------------------------------------------


def test_cookie_secure_flag(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    insecure = client.post(REGISTER, json=_credentials("anna"))
    assert "secure" not in insecure.headers.get("set-cookie", "").lower()

    monkeypatch.setattr(
        auth_router,
        "get_settings",
        lambda: Settings(database_url="unused", cookie_secure=True),
    )
    secure = client.post(REGISTER, json=_credentials("luca"))
    assert "secure" in secure.headers.get("set-cookie", "").lower()


# --- me / current_user --------------------------------------------------------


def _register_and_get_token(client: TestClient, nickname: str) -> str:
    response = client.post(REGISTER, json=_credentials(nickname))
    assert response.status_code == 201
    return response.cookies[COOKIE]


def test_me_without_cookie_401(client: TestClient) -> None:
    response = client.get(ME)

    assert response.status_code == 401
    assert "set-cookie" not in response.headers


def test_me_with_invented_cookie_401(client: TestClient) -> None:
    client.cookies.set(COOKIE, "token-inventato")

    assert client.get(ME).status_code == 401


def test_me_after_register_returns_user_and_renews_cookie(client: TestClient) -> None:
    token = _register_and_get_token(client, "Mario")

    response = client.get(ME)

    assert response.status_code == 200
    assert response.json() == {"id": response.json()["id"], "nickname": "Mario"}
    cookie = response.headers.get("set-cookie", "").lower()
    assert cookie.startswith(f"{COOKIE}={token.lower()};")
    assert "max-age=34560000" in cookie
    assert "httponly" in cookie


def test_me_after_login(client: TestClient) -> None:
    _register_and_get_token(client, "mario")
    client.cookies.clear()
    client.post(LOGIN, json=_credentials("mario"))

    assert client.get(ME).json()["nickname"] == "mario"


def test_old_cookie_rejected_after_logout(client: TestClient) -> None:
    token = _register_and_get_token(client, "mario")
    assert client.post(LOGOUT).status_code == 204

    client.cookies.set(COOKIE, token)  # the browser could still send the old cookie

    assert client.get(ME).status_code == 401


def test_me_returns_only_own_user(client: TestClient) -> None:
    anna_token = _register_and_get_token(client, "anna")
    client.cookies.clear()
    luca_token = _register_and_get_token(client, "luca")

    client.cookies.clear()
    client.cookies.set(COOKIE, anna_token)
    anna = client.get(ME).json()

    client.cookies.clear()
    client.cookies.set(COOKIE, luca_token)
    luca = client.get(ME).json()

    assert anna["nickname"] == "anna"
    assert luca["nickname"] == "luca"
    assert anna["id"] != luca["id"]

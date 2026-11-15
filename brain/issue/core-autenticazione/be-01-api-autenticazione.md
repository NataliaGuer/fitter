# CORE-002-BE-01 — Setup DB e API di autenticazione

- **Feature**: CORE-002 (`features/core-autenticazione.md`), include CORE-001 (setup DB)
- **Lato**: backend
- **Stato**: in corso (approvata 2026-11-15)
- **Dipende da**: —

## Obiettivo

Creare il layer di accesso al DB (SQLite + SQLAlchemy 2.x + Alembic, CORE-001) e, sopra di esso, utenti e sessioni
con le API `/api/auth/*`: registrazione, login, logout e verifica della sessione. Alla fine il backend è pronto
per essere usato dall'issue frontend `CORE-002-FE-01`; nessuna modifica a `frontend/`.

## Requisiti coperti

Dalla sezione *Requisiti → Backend* della feature:
- [ ] Registrazione libera: nickname univoco (case-insensitive) di 3–30 caratteri tra lettere, cifre, `_`, `-`, `.`; PIN di esattamente 4 cifre.
- [ ] La registrazione effettua anche il login (crea la sessione).
- [ ] PIN salvato solo come hash (argon2).
- [ ] Login → sessione nel DB + cookie `HttpOnly`, `SameSite=Lax`, `Secure` in prod.
- [ ] Sessione senza scadenza lato server; cookie da 400 giorni rinnovato a ogni `GET /api/auth/me`.
- [ ] Logout → elimina la sessione dal DB e cancella il cookie.
- [ ] Dipendenza FastAPI `current_user` (401 senza sessione valida).
- [ ] Errore generico al login e tempi di risposta simili per nickname esistente o no.

Criteri di accettazione della feature coperti: nickname duplicati rifiutati (anche con maiuscole diverse), PIN non
valido rifiutato, `401` senza sessione, cookie non più valido dopo il logout, nessun PIN/token in chiaro nel DB.
Il criterio "chiudendo e riaprendo l'app l'utente è ancora autenticato" è verificato end-to-end in `CORE-002-FE-01`.

## Fuori scope

- Tutto il frontend (`CORE-002-FE-01`), incluso il proxy Vite.
- Linter Python in CI (non previsto da CORE-003 per ora).
- Limite ai tentativi di login, cambio/recupero PIN, gestione sessioni attive (fuori scope della feature, D-009).

## Piano tecnico

Le scelte di fondo sono già decise e **non si ripropongono**: SQLite + SQLAlchemy 2.x + Alembic con
`render_as_batch=True` (D-001, D-003), sessione opaca permanente, argon2, `COLLATE NOCASE`, config da variabili
d'ambiente, migrazioni all'avvio del container (D-006, D-009). I dettagli rimanenti sono decisi sotto (D-012).

- **Contesto**: in `backend/` c'è solo `app/main.py` con l'endpoint d'esempio `/items` e le cartelle vuote
  `alembic/` e `tests/`. Non esistono config, accesso al DB, test né dipendenze di sviluppo. La CI esegue `pytest`
  solo se `tests/` contiene qualcosa.

- **Decisioni** (prese il 2026-11-15, D-012):
  - *Date in UTC su SQLite* (SQLite non ha un tipo con fuso orario): `TypeDecorator` `UTCDateTime` in
    `core/types.py`, che salva datetime naive in UTC, restituisce datetime aware UTC e rifiuta datetime naive in
    scrittura. La regola "date in UTC" è garantita in un punto solo ed è riusabile da tutte le tabelle future.
    Scartato: `DateTime` standard con `datetime.now(UTC)` nel codice (in lettura si ottengono datetime naive,
    facili da mescolare con quelli aware).
  - *DB nei test*: file SQLite temporaneo per ogni test, schema creato **eseguendo le migrazioni Alembic**,
    dipendenza `get_db` sovrascritta. I test verificano così anche le migrazioni e i PRAGMA reali.
    Scartato: SQLite in memoria con `Base.metadata.create_all` (non prova le migrazioni; WAL non si applica in
    memoria).
  - *Dipendenze di sviluppo*: nuovo `backend/requirements-dev.txt` (`-r requirements.txt` + `pytest`, `httpx2`),
    installato nello stage Docker `dev` e in CI, così i test girano anche nel container di sviluppo; l'immagine
    prod non cambia. Scartato: dipendenze di test solo in CI (in locale servirebbe Python 3.14 installato a parte).

- **Dettagli**:
  - `core/config.py`: legge `DATABASE_URL` (default `sqlite:////data/fitter.db`) e `COOKIE_SECURE` (default
    `true`) da variabili d'ambiente, in un `dataclass` immutabile restituito da `get_settings()` (con cache).
  - `core/db.py`: `Base` (`DeclarativeBase`), engine creato da `DATABASE_URL`, listener `connect` che esegue
    `PRAGMA journal_mode=WAL` e `PRAGMA foreign_keys=ON`, `SessionLocal` e dipendenza `get_db()` (una sessione
    per richiesta, chiusa a fine richiesta).
  - Alembic: `backend/alembic.ini` + `backend/alembic/env.py` che prende l'URL da `get_settings()` (non dal file
    `.ini`), `target_metadata = Base.metadata` importando i modelli, `render_as_batch=True`. Revisioni con nome
    `0001_...` e `revision = "0001"`.
  - Validazione (Pydantic): nickname `^[A-Za-z0-9_.-]{3,30}$`, PIN `^[0-9]{4}$` (non `\d`: nel motore regex di
    Pydantic `\d` accetta anche cifre Unicode non ASCII).
  - Token di sessione `secrets.token_urlsafe(32)`, nel DB `sha256(token)` in esadecimale. Cookie `fitter_session`,
    `HttpOnly`, `SameSite=Lax`, `Path=/`, `Max-Age=34560000` (400 giorni), `Secure` = `COOKIE_SECURE`.
  - `last_seen_at` aggiornato al massimo una volta ogni 24 ore.
  - Login con nickname inesistente: si verifica il PIN contro un hash fittizio calcolato all'avvio (tempi simili).
  - Nickname già usato: si intercetta l'`IntegrityError` del vincolo unique → `409` (niente controllo preventivo
    soggetto a race).
  - Codici HTTP: il frontend si basa sullo **status code**, non sul testo di `detail`.
  - Container: `CMD` = `alembic upgrade head && uvicorn ...` sia in `dev` (con `--reload`) che in `prod`.

- **Contratto** (identico in `CORE-002-FE-01`):

  | Metodo | Endpoint | Request (JSON) | Risposta |
  |--------|----------|----------------|----------|
  | POST | `/api/auth/register` | `{"nickname": str, "pin": str}` | `201 {"id": int, "nickname": str}` + cookie · `409` nickname già usato · `422` input non valido |
  | POST | `/api/auth/login` | `{"nickname": str, "pin": str}` | `200 {"id": int, "nickname": str}` + cookie · `401` credenziali errate · `422` input non valido |
  | POST | `/api/auth/logout` | — | `204`, cookie cancellato; idempotente (anche senza cookie) |
  | GET  | `/api/auth/me` | — | `200 {"id": int, "nickname": str}` + cookie rinnovato · `401` |

  - `nickname` nella risposta è quello scritto alla registrazione (maiuscole comprese).
  - Errori nel formato standard FastAPI `{"detail": ...}`.
  - Cookie: `fitter_session` come sopra; il frontend non lo legge mai (è `HttpOnly`).

- **Impatto**:
  - `requirements.txt`: FastAPI aggiornata da `0.115.6` a `0.163.1` (Starlette 1.10, richiesta dall'utente il
    2026-11-15). Nuove dipendenze: `sqlalchemy==2.1.8`, `alembic==1.20.1`, `argon2-cffi==25.1.0`
    (tutte con wheel `cp314`/`abi3` per `aarch64`, verificate su PyPI il 2026-11-15).
  - Nuovo `requirements-dev.txt`: `pytest==9.2.0`, `httpx2==2.16.0` (client usato dal `TestClient` di Starlette 1.x,
    che depreca `httpx`; scelto dall'utente il 2026-11-15).
  - Nuovi file: `backend/app/core/{__init__,config,db,types}.py`,
    `backend/app/auth/{__init__,models,schemas,service,router,deps}.py`, `backend/alembic.ini`,
    `backend/alembic/{env.py,script.py.mako}`, `backend/alembic/versions/0001_users_sessions.py`,
    `backend/tests/{conftest,test_db,test_models,test_auth_service,test_auth_api}.py`.
  - Modificati: `backend/app/main.py` (router `/api/auth` prima di `StaticFiles`, rimozione di `/items`),
    `Dockerfile` (copia di `alembic/` e `alembic.ini`, stage `dev` con `requirements-dev.txt`, `CMD` con
    migrazioni), `docker-compose.dev.yaml` (volumi `./data:/data`, `./backend/alembic`, `./backend/tests`),
    `.github/workflows/ci.yml` (installa `requirements-dev.txt`, `pytest` sempre eseguito), `.env.dev`
    (`COOKIE_SECURE=false`, file non versionato: va aggiunto a mano).
  - Schema DB (migrazione `0001`):
    - `users`: `id` INTEGER PK, `nickname` TEXT `COLLATE NOCASE` NOT NULL UNIQUE, `pin_hash` TEXT NOT NULL,
      `created_at` DATETIME NOT NULL.
    - `sessions`: `id` INTEGER PK, `token_hash` TEXT NOT NULL UNIQUE, `user_id` INTEGER NOT NULL FK → `users.id`
      `ON DELETE CASCADE` (indice), `created_at` DATETIME NOT NULL, `last_seen_at` DATETIME NOT NULL.
    - Nota: il piano nella feature citava anche `LoginFailure` / "3 tabelle", residuo di D-006 superato da D-009
      (niente anti forza bruta): **non** si crea.
  - Rischi:
    - PIN di 4 cifre indovinabile senza limite di tentativi (accettato, D-009: sicurezza affidata alla VPN).
    - Con `COOKIE_SECURE=true` il login funziona solo se l'app è servita in HTTPS dal reverse proxy: se sul Pi si
      accede in HTTP, va impostato `COOKIE_SECURE=false` in `.env`.
    - argon2 usa ~64 MiB di RAM per hash: con un solo worker e pochi utenti è accettabile sul Pi.

- **Decisioni registrate**: D-009 (già esistente), D-012 (date UTC, DB dei test, dipendenze di sviluppo).

## Passi

Ogni passo è un'unità di lavoro incrementale: lascia `main` rilasciabile (CI verde) e si chiude solo quando
l'utente conferma che la definition of done è soddisfatta.

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.

Comando dei test usato sotto (ambiente dev avviato con `./script/start-dev.sh`):
`docker compose -f docker-compose.dev.yaml exec app python -m pytest -v`

### Passo 1 — Layer DB, Alembic e infrastruttura di test (CORE-001)

- **Stato**: fatto (2026-11-15)
- **Obiettivo**: il backend si collega a SQLite con i PRAGMA giusti, Alembic è configurato (ancora senza
  revisioni), le migrazioni partono all'avvio del container e i test girano in locale e in CI.
- **Lavoro**:
  - `requirements.txt` con `sqlalchemy`, `alembic`; nuovo `requirements-dev.txt`.
  - `core/config.py`, `core/db.py`, `core/types.py` (`UTCDateTime`).
  - `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`, cartella `alembic/versions/` (con `.gitkeep`).
  - `tests/conftest.py`: fixture con DB SQLite temporaneo migrato con Alembic, `TestClient` con `get_db`
    sovrascritta, `COOKIE_SECURE=false`.
  - `tests/test_db.py`: PRAGMA attivi; `UTCDateTime` restituisce datetime aware UTC e rifiuta i naive.
  - `main.py`: rimozione di `/items`.
  - `Dockerfile`, `docker-compose.dev.yaml`, `ci.yml` come da *Impatto*.
- **Definition of done**:
  - [x] Il comando dei test termina con tutti i test verdi, inclusi `test_pragmas_wal_and_foreign_keys` e i test
        di `UTCDateTime`.
  - [x] `docker compose -f docker-compose.dev.yaml logs app` mostra l'esecuzione di Alembic prima dell'avvio di
        Uvicorn, senza errori.
  - [x] Dopo l'avvio esiste il file `data/fitter.db` sull'host.
  - [x] `curl -i http://localhost:8000/items/1` risponde `404`.
  - [ ] La CI del push è verde e il job `backend` esegue `pytest` (si vede nel log).
        _Non verificata: nessun push al momento della chiusura; passo chiuso su conferma dell'utente._

### Passo 2 — Modelli `User` e `Session` e migrazione `0001`

- **Stato**: fatto (2026-11-15)
- **Obiettivo**: le tabelle `users` e `sessions` esistono nel DB tramite migrazione, con i vincoli previsti.
- **Lavoro**:
  - `auth/models.py`: `User`, `Session` (stile `Mapped[...]` / `mapped_column`, date con `UTCDateTime`).
  - `alembic/env.py`: import dei modelli.
  - `alembic/versions/0001_users_sessions.py`: autogenerata e rivista a mano (`COLLATE NOCASE`, `ON DELETE
    CASCADE`, indice su `sessions.user_id`, `downgrade` completo).
  - `tests/test_models.py`.
- **Definition of done**:
  - [x] Test verdi, inclusi: `test_nickname_unique_case_insensitive` (inserire `Mario` e poi `mario` genera
        `IntegrityError`) e `test_delete_user_cascades_sessions`.
  - [x] `docker compose -f docker-compose.dev.yaml exec app alembic upgrade head` su DB vuoto (dopo aver
        cancellato `data/fitter.db`) crea le tabelle;
        `docker compose -f docker-compose.dev.yaml exec app python -m sqlite3 /data/fitter.db "select sql from sqlite_master where name='users'"`
        mostra `COLLATE NOCASE` sulla colonna `nickname`.
  - [x] `alembic downgrade base` seguito da `alembic upgrade head` termina senza errori.
  - [x] `alembic check` risponde che non ci sono differenze tra modelli e migrazioni.
  - [ ] CI verde.
        _Non verificata: nessun push al momento della chiusura; passo chiuso su conferma dell'utente._

### Passo 3 — Servizio di autenticazione

- **Stato**: da fare
- **Obiettivo**: le funzioni di dominio per PIN e sessioni esistono e sono testate, senza ancora esporre endpoint.
- **Lavoro**:
  - `requirements.txt`: `argon2-cffi`.
  - `auth/service.py`: `hash_pin`, `verify_pin`, `register_user`, `authenticate` (con hash fittizio per nickname
    inesistente), `create_session` (restituisce il token in chiaro, salva lo SHA-256),
    `get_user_by_token` (aggiorna `last_seen_at` se più vecchio di 24 ore), `delete_session`.
  - `tests/test_auth_service.py`.
- **Definition of done**:
  - [ ] Test verdi, inclusi: `test_pin_stored_as_argon2_hash` (`pin_hash` inizia con `$argon2id$` e non contiene
        il PIN), `test_session_token_not_stored_in_clear`, `test_authenticate_wrong_pin_returns_none`,
        `test_authenticate_unknown_nickname_returns_none`, `test_last_seen_updated_at_most_daily`,
        `test_deleted_session_token_is_invalid`.
  - [ ] Nessun nuovo endpoint: `curl -i http://localhost:8000/api/auth/me` risponde ancora `404`.
  - [ ] CI verde.

### Passo 4 — Endpoint di registrazione, login e logout

- **Stato**: da fare
- **Obiettivo**: `register`, `login` e `logout` funzionano secondo il contratto e impostano/cancellano il cookie.
- **Lavoro**:
  - `auth/schemas.py`: `Credentials` (nickname, PIN con le regex sopra), `UserOut`.
  - `auth/router.py`: `POST /register`, `POST /login`, `POST /logout`, gestione del cookie.
  - `main.py`: `include_router(..., prefix="/api/auth")` prima del mount di `StaticFiles`.
  - `tests/test_auth_api.py` (prima parte).
- **Definition of done**:
  - [ ] Test verdi, inclusi: register `201` con cookie `fitter_session` `HttpOnly` e `SameSite=Lax`; register
        duplicato con maiuscole diverse `409`; nickname di 2 o 31 caratteri, con spazi o accenti `422`; PIN `123`,
        `12345`, `12a4` e `١٢٣٤` (cifre arabe) `422`; login corretto `200`; PIN errato e nickname inesistente
        `401` con lo stesso `detail`; logout `204` anche senza cookie.
  - [ ] Test `test_cookie_secure_flag`: con `COOKIE_SECURE=true` il cookie ha l'attributo `Secure`.
  - [ ] A mano, nell'ambiente dev:
        `curl -i -X POST localhost:8000/api/auth/register -H 'Content-Type: application/json' -d '{"nickname":"prova","pin":"1234"}'`
        risponde `201` con un header `set-cookie: fitter_session=...`.
  - [ ] `http://localhost:8000/docs` mostra i tre endpoint sotto `/api/auth`.
  - [ ] CI verde.

### Passo 5 — `GET /api/auth/me` e dipendenza `current_user`

- **Stato**: da fare
- **Obiettivo**: c'è un modo unico per proteggere gli endpoint (`current_user`) e il frontend può verificare la
  sessione rinnovando il cookie.
- **Lavoro**:
  - `auth/deps.py`: `current_user` (legge il cookie, cerca la sessione, `401` se assente o non valida).
  - `auth/router.py`: `GET /me` che usa `current_user` e reimposta il cookie con `Max-Age` di 400 giorni.
  - `tests/test_auth_api.py` (seconda parte).
- **Definition of done**:
  - [ ] Test verdi, inclusi: `/me` senza cookie `401`; con cookie inventato `401`; dopo register `200` con
        `{id, nickname}` e `set-cookie` con `Max-Age=34560000`; dopo logout il vecchio cookie riceve `401`;
        `test_me_returns_only_own_user` (due utenti con due cookie: ognuno vede solo sé stesso).
  - [ ] A mano, nell'ambiente dev, sequenza `curl` con file dei cookie (`-c`/`-b cookies.txt`):
        register → `me` `200` → logout `204` → `me` `401`.
  - [ ] `docker compose -f docker-compose.dev.yaml exec app python -m sqlite3 /data/fitter.db "select token_hash from sessions"`
        non contiene il valore del cookie salvato in `cookies.txt`.
  - [ ] CI verde.
  - [ ] Se il rilascio è attivo (`RELEASE_ENABLED=true`): sul Pi, dopo il deploy, `docker compose logs app` mostra
        la migrazione `0001` applicata e `curl -i http://127.0.0.1:8000/api/auth/me` risponde `401`.
        Se il rilascio non è attivo, la voce si segna come non applicabile.

## Note di implementazione

### Passo 1 (2026-11-15)
- File creati: `app/__init__.py`, `app/core/{__init__,config,db,types}.py`, `alembic.ini`,
  `alembic/{env.py,script.py.mako}`, `alembic/versions/.gitkeep`, `tests/{__init__,conftest,test_db}.py`,
  `requirements-dev.txt`. Modificati: `requirements.txt`, `app/main.py`, `Dockerfile`, `docker-compose.dev.yaml`,
  `.github/workflows/ci.yml`; `.env.dev` (non versionato) ora contiene `COOKIE_SECURE=false`.
- `env.py` accetta una connessione già aperta tramite `config.attributes["connection"]`: la usano i test per
  migrare il DB temporaneo. `script.py.mako` importa già `app.core.types` per le colonne `UTCDateTime`.
- Esito verifiche locali: 6 test verdi nel container dev; log con Alembic prima di Uvicorn; `data/fitter.db`
  creato; `/items/1` → `404`. Immagine `prod` costruita (amd64) e avviata con un volume vuoto: migrazioni eseguite,
  `/` → `200`.
- FastAPI aggiornata a `0.163.1` (Starlette `1.10.0`, Pydantic `2.14.3`) su richiesta dell'utente: spariti i
  warning di deprecazione della vecchia Starlette su Python 3.14; test ancora verdi, `/items/1` → `404`.
  Sostituito `httpx` con `httpx2` in `requirements-dev.txt`: `pytest -W error` → 6 test verdi, nessun warning.
- Verifica CI: non eseguita (nessun push); l'utente ha chiuso il passo il 2026-11-15. Da controllare al primo push.

### Passo 2 (2026-11-15)
- File creati: `app/auth/{__init__,models}.py`, `alembic/versions/0001_users_sessions.py` (autogenerata e
  riformattata a mano: il contenuto coincide con quello generato), `tests/test_models.py`. Modificati:
  `app/core/db.py`, `alembic/env.py` (import dei modelli). Rimosso `alembic/versions/.gitkeep`.
- Il modello delle sessioni si chiama **`UserSession`** (tabella `sessions`) invece di `Session`, per non
  confondersi con `sqlalchemy.orm.Session` nel servizio e nelle dipendenze.
- `Base.metadata` ha una **naming convention** per vincoli e indici (`pk_users`, `uq_users_nickname`,
  `fk_sessions_user_id_users`, `ix_sessions_user_id`, ...): con SQLite in batch mode le migrazioni future possono
  modificare o eliminare un vincolo solo se ha un nome.
- Test aggiunto oltre a quelli previsti: `test_models_match_migrations`, l'equivalente di `alembic check` eseguito
  in ogni test run (anche in CI).
- Esito verifiche locali: 13 test verdi con `pytest -W error`; `upgrade head` su DB vuoto → revisione `0001`;
  schema con `COLLATE "NOCASE"` su `nickname` e `ON DELETE CASCADE` su `sessions.user_id`; `downgrade base` +
  `upgrade head` senza errori; `alembic check` → "No new upgrade operations detected".
- Da Git Bash su Windows i comandi con un percorso del container (`/data/fitter.db`) vanno lanciati con
  `MSYS_NO_PATHCONV=1`, altrimenti il percorso viene convertito in un percorso Windows.

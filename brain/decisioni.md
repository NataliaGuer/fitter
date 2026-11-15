# Registro decisioni

Formato: una sezione per decisione, la più recente in fondo.

---

## D-001 — SQLite come database
- **Data**: 2026-11-14
- **Stato**: accettata
- **Contesto**: l'app gira su un Raspberry Pi con risorse limitate; uso personale, pochi utenti.
- **Decisione**: SQLite, file su volume `/data` (host `./data`), modalità WAL, un solo worker Uvicorn.
- **Conseguenze**: niente server DB da gestire, backup = copia del file; scritture concorrenti limitate (accettabile per questo carico).

## D-002 — Stack applicativo
- **Data**: 2026-11-14
- **Stato**: accettata
- **Decisione**: backend FastAPI, frontend React + Vite come PWA; in produzione un unico container in cui FastAPI serve sia le API (`/api`) sia il build statico del frontend.

## D-003 — Accesso al DB: SQLAlchemy + Alembic
- **Data**: 2026-11-14
- **Stato**: accettata
- **Decisione**: ORM **SQLAlchemy 2.x** (stile tipizzato `Mapped[...]` / `mapped_column`), migrazioni con **Alembic**.
- **Conseguenze**:
  - Ogni modifica allo schema = nuova revisione Alembic (`alembic revision --autogenerate`, poi revisione manuale del file generato).
  - SQLite ha un `ALTER TABLE` limitato: in `env.py` usare `render_as_batch=True`.
  - Le migrazioni vengono applicate all'avvio del container (`alembic upgrade head`) o con un comando esplicito.

## D-004 — App multi-utente
- **Data**: 2026-11-14
- **Stato**: accettata
- **Decisione**: l'app supporta più utenti, ognuno con i propri dati (schede, sessioni, diario alimentare, obiettivi).
- **Conseguenze**:
  - Serve autenticazione (registrazione, login, sessione) → feature `CORE-002`.
  - Tutte le tabelle con dati personali hanno `user_id` (FK) e ogni query è filtrata per l'utente autenticato.
  - Nessun endpoint deve restituire dati di altri utenti: va coperto da test.

## D-005 — Sorgente dati alimenti: API esterne + DB interno
- **Data**: 2026-11-14
- **Stato**: accettata
- **Decisione**: la ricerca di un alimento interroga **API esterne**; gli alimenti non trovati possono essere **inseriti dall'utente** e vengono salvati in un DB interno.
- **Conseguenze**:
  - Tabella `foods` con campo `source` (es. `external` / `user`) e, per gli esterni, l'ID esterno (es. barcode).
  - Quando un alimento esterno viene usato in un pasto, se ne salva una copia locale dei valori nutrizionali: il diario non deve cambiare se l'API cambia o non risponde.
  - La ricerca deve funzionare (sui dati locali) anche se l'API esterna non è raggiungibile.
  - Le chiamate esterne passano da un modulo client dedicato, con timeout e gestione errori.

## D-006 — Autenticazione: cookie di sessione, nickname + PIN
- **Data**: 2026-11-14
- **Stato**: accettata
- **Decisione**:
  - Autenticazione con **cookie di sessione** (`HttpOnly`, `Secure` in prod, `SameSite=Lax`); sessioni salvate nel DB.
  - **Registrazione libera** con **nickname** (univoco) e **PIN di 4 cifre**.
- **Conseguenze**:
  - ~~Un PIN di 4 cifre ha solo 10.000 combinazioni: servono contromisure obbligatorie contro i tentativi a forza bruta.~~ **Superato da D-009**: per ora nessun limite ai tentativi.
  - Il PIN si salva solo come hash (argon2 o bcrypt), mai in chiaro.
  - Logout = invalidazione della sessione lato server.
- **Dettagli**: vedi `features/core-autenticazione.md` (CORE-002).

## D-007 — Libreria UI frontend: HeroUI
- **Data**: 2026-11-14
- **Stato**: accettata
- **Decisione**: i componenti dell'interfaccia del frontend si costruiscono con **HeroUI**.
- **Conseguenze**:
  - HeroUI si basa su **Tailwind CSS**: lo styling si fa con Tailwind e i temi di HeroUI, non con CSS custom sparso.
  - Usare i componenti HeroUI esistenti prima di crearne di propri; niente altre librerie di componenti UI.
  - Versione, setup (Tailwind, provider, tema chiaro/scuro) e pulizia del boilerplate Vite vanno definiti nel piano tecnico della prima feature con UI.

## D-008 — CI/CD: GitHub Actions + GHCR + deploy pull-based sul Raspberry Pi
- **Data**: 2026-11-14
- **Stato**: accettata (piano CORE-003 approvato)
- **Decisione**:
  - CI con **GitHub Actions** su ogni push e PR (`.github/workflows/ci.yml`).
  - Immagine **ARM64** costruita su runner ARM nativo GitHub (`ubuntu-24.04-arm`), pubblicata su **GHCR** con tag `latest` + `sha-<commit>`.
  - Rilascio solo su push a `main` con la variabile di repository `RELEASE_ENABLED=true`.
  - Deploy **pull-based**: timer systemd sul Pi ogni 5 minuti → `deploy/deploy.sh` (git pull, pull dell'immagine, backup del DB, riavvio). Ultimi 10 backup conservati.
  - Esclusi: runner self-hosted (rischioso con repo pubblica), deploy via SSH (porte esposte), Watchtower.
- **Conseguenze**: branch principale `main`; Raspberry Pi con Debian 13 `arm64` (confermato); nessun segreto del Pi su GitHub; `docker-compose.yaml` di produzione usa l'immagine (`APP_IMAGE` in `.env`) invece della build locale.

## D-009 — Autenticazione backend: sessione permanente, niente anti forza bruta
- **Data**: 2026-11-15
- **Stato**: accettata (piano CORE-002-BE approvato)
- **Contesto**: l'app è usata solo dall'utente e dalla sua famiglia ed è raggiungibile **solo tramite VPN**.
- **Decisione**:
  - **Nessun limite ai tentativi di login** (né per nickname né per IP): modifica D-006. Da reintrodurre se l'app si apre a utenti esterni o esce dalla VPN.
  - **Sessione permanente**: token casuale opaco (`secrets.token_urlsafe(32)`) nel cookie `fitter_session`, nel DB solo il suo SHA-256; nessuna scadenza lato server; cookie da 400 giorni (massimo dei browser) rinnovato a ogni `GET /api/auth/me`. Logout = eliminazione della riga di sessione.
  - Hash del PIN con **argon2-cffi**. Il PIN non si può cambiare.
  - Nickname univoco case-insensitive con `COLLATE NOCASE` (ammessi solo caratteri ASCII `A-Z a-z 0-9 _ - .`).
  - Config da variabili d'ambiente senza `pydantic-settings`; migrazioni Alembic applicate all'avvio del container.
- **Conseguenze**: un PIN di 4 cifre è indovinabile in pochi minuti da chi raggiunge l'app: la sicurezza poggia sulla VPN.

## D-010 — Frontend: HeroUI v3, niente router, proxy Vite
- **Data**: 2026-11-15
- **Stato**: accettata (piano CORE-002-FE approvato)
- **Decisione**:
  - **HeroUI v3** (`@heroui/react` + `@heroui/styles`) con **Tailwind CSS 4** (`@tailwindcss/vite`); tema chiaro/scuro che segue il sistema.
  - Nessun router per ora: un `AuthProvider` (React context) decide tra accesso e home. Router da introdurre con la prima feature a più pagine.
  - Chiamate API con un piccolo wrapper su `fetch` (niente TanStack Query per ora).
  - In sviluppo Vite fa da proxy per `/api` verso il backend (stessa origine come in prod, niente CORS).
  - Il service worker della PWA non intercetta `/api` (`navigateFallbackDenylist`).
  - Offline all'avvio: messaggio con "Riprova", mai logout automatico.

## D-011 — Flusso di lavoro: feature → issue → passi con definition of done
- **Data**: 2026-11-15
- **Stato**: accettata
- **Decisione**:
  - Le feature (`brain/features/`) non si implementano direttamente: vanno prima trasformate in **issue** (`brain/issue/<feature>/`, una cartella per feature) con la skill `/feature-to-issue`.
  - Ogni issue riguarda **solo il backend** o **solo il frontend**; il contratto API è la frontiera tra le due.
  - Il **piano tecnico** sta nell'issue (non più nella feature) e contiene passi incrementali, ognuno con una **definition of done** verificabile.
  - Si implementa un passo alla volta; il passo si chiude solo quando l'**utente** conferma che la DoD è soddisfatta.
- **Conseguenze**: i piani tecnici già scritti nelle feature (CORE-002, CORE-003) restano validi come base, ma vanno convertiti in issue prima di proseguire.

## D-012 — Backend: date UTC, DB dei test, dipendenze di sviluppo
- **Data**: 2026-11-15
- **Stato**: accettata (issue CORE-002-BE-01)
- **Decisione**:
  - **Date**: tipo `UTCDateTime` (`backend/app/core/types.py`, `TypeDecorator`) per tutte le colonne data/ora: salva in UTC, restituisce datetime aware UTC, rifiuta i datetime naive.
  - **Test**: ogni test usa un file SQLite temporaneo con lo schema creato dalle migrazioni Alembic (non `create_all`, non DB in memoria) e `get_db` sovrascritta.
  - **Dipendenze di sviluppo** in `backend/requirements-dev.txt` (`-r requirements.txt` + strumenti di test), installate nello stage Docker `dev` e in CI; l'immagine prod non le contiene.
- **Conseguenze**: ogni nuova colonna data/ora usa `UTCDateTime`; ogni migrazione è provata dai test.

## Rimandate all'implementazione della sezione calorie (CAL-001)
- **Quale API esterna** per gli alimenti (es. Open Food Facts: gratuita, senza chiave, supporta i barcode; alternative: USDA FoodData Central, Edamam).
- **Visibilità degli alimenti inseriti dagli utenti**: privati per l'utente che li crea o condivisi con tutti?

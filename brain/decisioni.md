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
  - Un PIN di 4 cifre ha solo 10.000 combinazioni: servono contromisure obbligatorie contro i tentativi a forza bruta, cioè un limite ai tentativi falliti per nickname e per IP, con blocco temporaneo.
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

## Rimandate all'implementazione della sezione calorie (CAL-001)
- **Quale API esterna** per gli alimenti (es. Open Food Facts: gratuita, senza chiave, supporta i barcode; alternative: USDA FoodData Central, Edamam).
- **Visibilità degli alimenti inseriti dagli utenti**: privati per l'utente che li crea o condivisi con tutti?

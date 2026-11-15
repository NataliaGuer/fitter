# CORE-002 — Utenti e autenticazione

- **Area**: core
- **Stato**: in corso
- **Priorità**: alta
- **Dipende da**: CORE-001 (setup DB, incluso nel piano backend)

L'implementazione è divisa in due parti, rilasciabili separatamente:
- **CORE-002-BE** — backend (modelli, migrazione, API, test).
- **CORE-002-FE** — frontend (setup HeroUI, schermate di accesso, stato di autenticazione).

## Obiettivo

Permettere a più persone di usare l'app, ognuna con i propri dati, con un accesso rapido dal telefono (nickname + PIN di 4 cifre). Dopo il login l'utente resta autenticato **per sempre**, finché non fa logout. Vedi D-004 e D-006.

## User story

- Come nuovo utente voglio registrarmi scegliendo un nickname e un PIN, per iniziare subito a usare l'app.
- Come utente voglio accedere con nickname e PIN e trovarmi già dentro ogni volta che apro l'app, per non dover rifare il login in palestra.
- Come utente voglio poter uscire (logout).

## Decisioni di prodotto (2026-11-15)

- **Sessione permanente**: la sessione non scade; termina solo con il logout.
- **Nessuna protezione anti forza bruta** per ora: l'app è usata solo dall'utente e dalla sua famiglia. Questo modifica D-006, dove il limite era obbligatorio. Rischio accettato perché l'app è raggiungibile solo tramite **VPN** (D-009).
- **Il PIN non si può cambiare.**

## Requisiti

### Backend (CORE-002-BE)
- [x] Registrazione libera: nickname univoco (case-insensitive) di 3–30 caratteri tra lettere, cifre, `_`, `-`, `.`; PIN di esattamente 4 cifre numeriche.
- [x] La registrazione effettua anche il login (crea la sessione).
- [x] PIN salvato solo come hash (argon2).
- [x] Login → crea una sessione nel DB e imposta un cookie `HttpOnly`, `SameSite=Lax`, `Secure` in prod.
- [x] Sessione senza scadenza lato server; cookie con durata massima consentita dai browser (400 giorni), **rinnovato a ogni apertura dell'app** (`GET /api/auth/me`), così in pratica non scade mai.
- [x] Logout → elimina la sessione dal DB e cancella il cookie.
- [x] Dipendenza FastAPI `current_user` per proteggere gli endpoint (401 senza sessione valida).
- [x] Messaggio di errore generico al login (non rivelare se il nickname esiste); tempo di risposta simile nei due casi.

### Frontend (CORE-002-FE)
- [ ] Setup HeroUI + Tailwind (prima feature con UI, vedi D-007) e pulizia del boilerplate Vite.
- [ ] All'avvio l'app verifica la sessione (`/api/auth/me`): se valida mostra direttamente la home, altrimenti la schermata di accesso.
- [ ] Schermata di accesso con due modalità: "Accedi" / "Registrati".
- [ ] Campo nickname + input PIN a 4 caselle con tastierino numerico.
- [ ] Messaggi di errore chiari: credenziali errate, nickname già usato, input non valido.
- [ ] Pulsante di logout (per ora nella home segnaposto).
- [ ] Se il backend non è raggiungibile (offline) **non** si torna al login: si mostra un messaggio con "Riprova".

## Fuori scope

- Recupero del PIN dimenticato.
- Cambio del PIN.
- Protezione anti forza bruta (limite di tentativi per nickname o per IP): da aggiungere se l'app si apre a utenti esterni alla famiglia.
- Elenco/gestione delle sessioni attive, "esci da tutti i dispositivi".
- Ruoli/amministrazione.

## Modello dati

- `users`: `id` (PK), `nickname` (TEXT `COLLATE NOCASE`, unique), `pin_hash`, `created_at`
- `sessions`: `id` (PK), `token_hash` (SHA-256 del token, unique), `user_id` (FK → `users`, `ON DELETE CASCADE`), `created_at`, `last_seen_at`

Tutte le date in UTC.

## API

| Metodo | Endpoint | Request | Risposta |
|--------|----------|---------|----------|
| POST | `/api/auth/register` | `{nickname, pin}` | `201 {id, nickname}` + cookie · `409` nickname già usato · `422` input non valido |
| POST | `/api/auth/login` | `{nickname, pin}` | `200 {id, nickname}` + cookie · `401` credenziali errate |
| POST | `/api/auth/logout` | — | `204`, cookie cancellato (idempotente) |
| GET  | `/api/auth/me` | — | `200 {id, nickname}` + cookie rinnovato · `401` |

Errori nel formato standard FastAPI (`{"detail": ...}`).

## UI

- **Avvio**: schermata di caricamento breve mentre si verifica la sessione.
- **Accesso**: tab "Accedi" / "Registrati"; campo nickname; PIN a 4 caselle (`inputmode="numeric"`); pulsante a tutta larghezza. In registrazione il PIN va inserito due volte (conferma).
- **Home** (segnaposto finché non ci sono altre feature): "Ciao, <nickname>" + pulsante "Esci".

## Criteri di accettazione

- [ ] Non si possono registrare due utenti con lo stesso nickname (nemmeno con maiuscole o minuscole diverse).
- [ ] Un PIN diverso da 4 cifre numeriche viene rifiutato.
- [ ] Gli endpoint protetti rispondono `401` senza una sessione valida.
- [ ] Chiudendo e riaprendo l'app (anche dopo settimane) l'utente è ancora autenticato.
- [ ] Dopo il logout il vecchio cookie non dà più accesso.
- [ ] Nel DB non c'è né il PIN né il token di sessione in chiaro.

## Domande aperte

- Nessuna.

## Issue

| ID | Lato | Stato | File |
|----|------|-------|------|
| CORE-002-BE-01 | backend | fatta (2026-11-15) | `issue/core-autenticazione/be-01-api-autenticazione.md` |
| CORE-002-FE-01 | frontend | in corso (approvata 2026-11-15) | `issue/core-autenticazione/fe-01-accesso-e-sessione.md` |

Il piano tecnico qui sotto (flusso precedente a D-011) è la base delle issue; in caso di differenze vale l'issue.

## Piano tecnico

### Piano backend (CORE-002-BE)

- **Stato piano**: approvato (2026-11-15)
- **Contesto**: non esiste ancora il layer DB (CORE-001) né alcun modulo applicativo; vanno decisi librerie, schema e flusso di sessione.
- **Alternative**:
  - *Hash del PIN*
    - A — `argon2-cffi` (pro: raccomandato OWASP, wheel ARM64 abi3, leggero / contro: una dipendenza in più; ~64 MiB di RAM per hash, ok sul Pi).
    - B — `bcrypt` (pro: diffuso / contro: nessun vantaggio rispetto ad A).
    - Nota: con 10.000 PIN possibili l'hash protegge poco se il file DB viene rubato; serve comunque a non tenere i PIN in chiaro.
  - *Sessione permanente*
    - A — token casuale opaco in cookie, hash del token nel DB, nessuna scadenza server, cookie da 400 giorni rinnovato a ogni `/me` (pro: logout reale, semplice / contro: una query per richiesta, trascurabile).
    - B — JWT senza stato (contro: il logout non invalida davvero il token; scartato, contrario a D-006).
- **Proposta**: argon2-cffi e sessione opaca A. Nessuna protezione anti forza bruta (decisione di prodotto del 2026-11-15).
- **Dettagli**:
  - Token: `secrets.token_urlsafe(32)`; nel DB solo `sha256(token)`. Cookie `fitter_session`, `Path=/`, `Max-Age` 400 giorni.
  - `last_seen_at` aggiornato al massimo una volta al giorno (evita scritture a ogni richiesta).
  - Login con nickname inesistente: si verifica comunque un hash fittizio per uniformare i tempi.
  - CSRF: coperto da `SameSite=Lax` + endpoint che accettano solo JSON.
  - Config da variabili d'ambiente (`DATABASE_URL`, default `sqlite:////data/fitter.db`; `COOKIE_SECURE`, default `true`, `false` in `.env.dev`) lette in `core/config.py`, senza `pydantic-settings`.
  - Migrazioni applicate all'avvio del container: `alembic upgrade head && uvicorn ...` (D-003); il backup del DB lo fa già `deploy.sh` prima del riavvio.
- **Impatto**:
  - Nuove dipendenze (`requirements.txt`): `sqlalchemy` 2.1.x, `alembic` 1.20.x, `argon2-cffi`. Solo test (`requirements-dev.txt`): `pytest`, `httpx`.
  - Nuovi file: `backend/app/core/{config,db}.py`, `backend/app/auth/{models,schemas,service,router,deps}.py`, `backend/alembic.ini`, `backend/alembic/` (`env.py` con `render_as_batch=True`), prima revisione con le 3 tabelle, `backend/tests/`.
  - Modificati: `main.py` (router `/api/auth` prima di `StaticFiles`, rimozione endpoint di esempio `/items`), `Dockerfile` (copia di alembic, CMD con migrazioni), `docker-compose.dev.yaml` (volume `./data:/data`), CI (installa `requirements-dev.txt`), `.env.dev` (`COOKIE_SECURE=false`).
  - Schema DB: tabelle `users`, `sessions` (migrazione `0001`).
  - Rischi: **senza limite ai tentativi un PIN di 4 cifre si indovina con uno script in pochi minuti**, se l'app è raggiungibile da internet e qualcuno conosce un nickname (rischio accettato: uso solo familiare e app raggiungibile solo tramite VPN). I browser limitano i cookie a 400 giorni → mitigato dal rinnovo a ogni apertura.
- **Passi**:
  1. CORE-001: config, engine SQLAlchemy con `PRAGMA journal_mode=WAL` e `foreign_keys=ON`, sessione DB come dipendenza FastAPI, setup Alembic.
  2. Modelli `User`, `Session`, `LoginFailure` + migrazione autogenerata e rivista.
  3. Servizio: hash/verifica PIN, creazione/lookup/eliminazione sessioni.
  4. Schemi Pydantic, router `/api/auth/*`, dipendenza `current_user`.
  5. Test: registrazione (duplicati case-insensitive, validazione), login/logout, 401 senza sessione, cookie dopo logout non valido.
  6. Dockerfile, compose dev, CI.
- **Decisioni registrate**: D-009 (aggiorna D-006)

### Piano frontend (CORE-002-FE)

- **Stato piano**: approvato (2026-11-15)
- **Contesto**: prima feature con UI → va definito il setup HeroUI (D-007), la gestione dello stato di autenticazione e il collegamento con il backend in sviluppo.
- **Alternative**:
  - *Versione HeroUI*
    - A — **HeroUI v3** (`@heroui/react` 3.2.x + `@heroui/styles`, Tailwind 4, React Aria; pro: versione corrente, nessun provider obbligatorio, ha `InputOTP` per il PIN / contro: API diverse dalla v2 in molti esempi online).
    - B — HeroUI v2 (contro: versione precedente, richiede framer-motion).
  - *Navigazione*
    - A — nessun router per ora: `AuthProvider` decide se mostrare accesso o home (pro: zero dipendenze / contro: andrà aggiunto un router con le prime feature con più pagine).
    - B — `react-router` subito (contro: dipendenza senza pagine da navigare).
  - *Chiamate API*
    - A — piccolo wrapper su `fetch` in `src/api/` (pro: nessuna dipendenza).
    - B — TanStack Query (contro: eccessivo per 4 endpoint; rivalutabile più avanti).
  - *Backend in sviluppo*
    - A — **proxy Vite** `/api` → backend (pro: stessa origine come in prod, cookie e niente CORS).
    - B — CORS con credenziali sul backend (contro: configurazione diversa da prod).
- **Proposta**: A in tutti i casi.
- **Dettagli**:
  - `AuthProvider` (React context): stato `loading | authenticated | anonymous | offline`; all'avvio `GET /api/auth/me`; `401` → anonymous; errore di rete → offline (con "Riprova"), mai logout automatico.
  - PWA: `workbox.navigateFallbackDenylist: [/^\/api\//]` per non far servire `/api` dalla cache del service worker.
  - Proxy Vite verso `http://app:8000` in docker (variabile `API_PROXY_TARGET`, default `http://localhost:8000`).
  - Tema chiaro/scuro: segue il sistema (`prefers-color-scheme`), senza selettore per ora.
- **Impatto**:
  - Nuove dipendenze: `@heroui/react`, `@heroui/styles`, `tailwindcss` 4, `@tailwindcss/vite` e le peer dependency richieste da HeroUI.
  - Nuovi file: `src/api/{client,auth}.ts`, `src/auth/{AuthProvider,useAuth}.tsx`, `src/pages/{AuthPage,HomePage}.tsx`.
  - Modificati: `vite.config.ts`, `index.css` (import Tailwind + HeroUI), `App.tsx`, `main.tsx`; rimossi `App.css` e asset del boilerplate.
  - Nessuna modifica al DB.
  - Rischi: peso del bundle (HeroUI è tree-shakeable, si verifica con `npm run build`).
- **Passi**:
  1. Installazione e setup Tailwind 4 + HeroUI v3, pulizia boilerplate.
  2. Proxy Vite e regola PWA per `/api`.
  3. Client API e `AuthProvider`.
  4. `AuthPage` (accedi/registrati, PIN con `InputOTP`, errori 401/409/422) e `HomePage` con logout.
  5. `npm run lint` + `npm run build`, prova manuale da telefono/emulazione mobile.
- **Decisioni registrate**: D-010

## Note di implementazione

Da compilare durante/dopo lo sviluppo.

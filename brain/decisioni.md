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

## D-013 — Frontend: validazione degli input e messaggi d'errore
- **Data**: 2026-11-15
- **Stato**: accettata (issue CORE-002-FE-01)
- **Decisione**:
  - **Validazione** dei form con controlli semplici nei componenti, senza librerie di form; le regole replicano quelle del backend, che resta la verifica definitiva (`422`).
  - **Messaggi d'errore** in italiano decisi dal frontend in base allo **status code** HTTP (ed errore di rete); il `detail` del backend non viene mostrato all'utente.
- **Conseguenze**: una regola di validazione cambiata nel backend va aggiornata anche nel frontend; i testi di `detail` del backend possono restare in inglese.

## D-014 — Frontend: icone, date e barra di navigazione
- **Data**: 2026-11-17
- **Stato**: accettata (issue CORE-004-FE-01)
- **Decisione**:
  - **Icone** con `@gravity-ui/icons` (set usato dalla documentazione HeroUI v3); scartati `lucide-react` e SVG a mano.
  - **Date lato client** con `@internationalized/date` (già presente come peer di HeroUI) e `Intl.DateTimeFormat('it-IT')`; settimana da lunedì, fuso del dispositivo. Niente `date-fns` o simili.
  - **Barra di navigazione** floating in basso, solo icone, composta con `Button` HeroUI + Tailwind (non `Tabs`), voce centrale "Start" in evidenza; `safe-area-inset-bottom` con `viewport-fit=cover`.
  - **Swipe** con gli eventi touch di React (soglia 50 px, prevalenza orizzontale), senza librerie di gesture né `scroll-snap`.
- **Conseguenze**: ogni nuova icona viene da `@gravity-ui/icons`; i calcoli di calendario non usano `Date` a mano.

## D-015 — Frontend: stile neobrutalista, font e cambio di tema
- **Data**: 2026-11-17
- **Stato**: accettata (issue CORE-005-FE-01)
- **Decisione**:
  - **Stile neobrutalista** (`brain/DESIGN.md`) applicato come **tema HeroUI**: variabili CSS di HeroUI ridefinite in `src/theme.css`, più token Tailwind (`@theme`) e utility (`@utility`, es. ombra piena ed effetto pressione) per ciò che HeroUI non copre. È l'unico posto con CSS nostro; niente librerie di componenti neobrutaliste.
  - **Font DM Sans** con `@fontsource-variable/dm-sans` servito dall'app e messo nella cache della PWA (niente Google Fonts).
  - **Due temi**: chiaro **Coral & Cream** (primario corallo `#E8635A`) e scuro **Dark Brut** (primario giallo `#FFE566`); testo nero sul colore primario in entrambi (contrasto ≥ 4.5:1).
  - **Scelta del tema** dell'utente salvata in `localStorage` (`fitter-theme`), applicata dallo script inline di `index.html` prima del primo render; senza scelta si segue il sistema. Modifica D-010 (prima: sempre il sistema).
- **Conseguenze**: le nuove schermate ereditano lo stile dal tema; i colori si prendono dai token, mai valori esadecimali sparsi nei componenti; la scelta del tema non passa tra dispositivi (eventuale preferenza sul profilo: futura issue backend).

## D-016 — Catalogo esercizi: dataset RepDB nell'immagine, caricato nel DB all'avvio
- **Data**: 2026-11-21
- **Stato**: accettata (issue ALL-001-BE-01)
- **Decisione**:
  - **Dataset** dal pacchetto npm `@repdb/exercises`, versione **esatta** fissata solo in `frontend/package.json`; nella build Docker lo stage `backend` copia `exercises.json` e `package.json` del pacchetto dallo stage `frontend` in `/backend/dataset/` (`EXERCISES_DATASET_DIR`). Dataset e immagini non entrano nel repo; i nomi italiani stanno in `backend/app/exercises/names_it.json` (versionato).
  - **Schema**: tabella `exercises` senza `user_id` (dati comuni, sola lettura), chiave = `id` del dataset; muscoli in colonne JSON (non tabella collegata); immagini come solo nome di file; `is_active = false` per gli esercizi spariti dal dataset, che non si cancellano mai.
  - **Caricamento** con `python -m app.exercises.sync` all'avvio del container, tra migrazioni e Uvicorn: una sola transazione, upsert per `id`, saltato se l'impronta SHA-256 (dataset + nomi italiani + `LOADER_VERSION`) coincide con quella salvata in `exercise_catalog_state`. Un fallimento **non blocca l'avvio** dell'app; un dataset incompatibile viene fermato in build (verifica nello stage `backend`).
  - **Ricerca** su colonna `search_text` (nome italiano + inglese normalizzati in Python: `casefold` e senza accenti) con `LIKE` per parola; scartati `COLLATE NOCASE` e FTS5.
  - **Rotte del frontend**: il mount statico restituisce `index.html` per le `GET` senza file corrispondente, tranne i percorsi `/api/` e quelli con estensione.
- **Conseguenze**: aggiornare il catalogo = cambiare la versione in `frontend/package.json` e rilasciare; le tabelle future (routine, sessioni) possono avere una chiave esterna su `exercises.id`; attribuzione "Exercise data by RepDB" obbligatoria in `README.md` e nell'app.

## D-017 — Il backend lo scrive l'utente (progetto usato per imparare Python)
- **Data**: 2026-11-22
- **Stato**: accettata
- **Contesto**: l'utente vuole usare il progetto per imparare Python; sa già programmare in altri linguaggi.
- **Decisione**:
  - Il codice sotto `backend/` (applicazione, test, migrazioni) lo scrive l'utente; Claude non lo tocca senza richiesta esplicita e, su richiesta, spiega e fa review.
  - Il frontend resta a Claude, con il flusso di D-011.
  - Le feature si decidono insieme; per il backend l'issue e il piano tecnico diventano facoltativi e le decisioni tecniche sono dell'utente. Modifica D-011 per il solo backend.
  - Il contratto API si concorda insieme e si scrive nell'issue frontend.
  - Il codice backend già esistente (`core/`, `auth/`) resta; l'autenticazione potrà essere riscritta dall'utente più avanti come esercizio, usando i test esistenti come specifica.
  - Il backend si sviluppa nel container `app` dell'ambiente dev (shell con `docker compose -f docker-compose.dev.yaml exec app bash`), non in un virtualenv locale: sul PC dell'utente il Controllo applicazioni di Windows blocca gli eseguibili non firmati.
  - Anche le modifiche al `Dockerfile` che servono al backend le fa l'utente.
- **Conseguenze**: le issue backend già approvate (ALL-001-BE-01) restano come guida per l'utente, che ne scrive i passi di codice dal passo 3 in poi (il passo 4, i nomi italiani degli esercizi, resta a Claude: è traduzione, non codice); la skill `/feature-to-issue` si usa per le issue frontend.

## Rimandate all'implementazione della sezione calorie (CAL-001)
- **Quale API esterna** per gli alimenti (es. Open Food Facts: gratuita, senza chiave, supporta i barcode; alternative: USDA FoodData Central, Edamam).
- **Visibilità degli alimenti inseriti dagli utenti**: privati per l'utente che li crea o condivisi con tutti?

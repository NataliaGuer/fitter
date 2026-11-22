# ALL-001-BE-01 — Catalogo esercizi: dataset RepDB nel DB e API

- **Feature**: ALL-001 (`features/allenamento-esercizi.md`)
- **Lato**: backend
- **Stato**: in corso (approvata 2026-11-21)
- **Dipende da**: CORE-002-BE-01 (fatta)

## Obiettivo

Portare il dataset `@repdb/exercises` nell'immagine Docker, caricarlo in automatico nel DB SQLite all'avvio del
container con i nomi in italiano, ed esporre le API di elenco (ricerca, filtri, paginazione), filtri disponibili
e dettaglio. Include il fallback del backend per le rotte del frontend, necessario al router che introduce
ALL-001-FE-01.

## Requisiti coperti

Da ALL-001:
- [ ] Dataset dal pacchetto con versione fissata; `exercises.json` e immagini fuori dal repo.
- [ ] Nomi degli esercizi in italiano (file JSON `{ "<id>": "<nome>" }`), con ripiego sul nome inglese e
  segnalazione nei log degli esercizi senza traduzione.
- [ ] Dataset nell'immagine (copiato durante la build Docker).
- [ ] Catalogo nel database, caricato automaticamente all'avvio del container; nessun duplicato; gli esercizi
  spariti dal dataset non vengono cancellati.
- [ ] Esercizi comuni a tutti gli utenti, in sola lettura.
- [ ] Ricerca senza distinzione tra maiuscole/minuscole e accenti; filtri combinabili; risultati paginati.
- [ ] Dati del dettaglio (parte del corpo, attrezzatura, difficoltà, muscoli, immagini).
- [ ] Attribuzione RepDB nel `README.md` del repo.
- [ ] API accessibili solo agli utenti autenticati (401 senza login).

## Fuori scope

- Schermate, router, etichette italiane dei codici, immagini servite al browser, link di attribuzione nell'app:
  ALL-001-FE-01.
- Descrizioni, istruzioni, consigli, `goals`, `tags`, `variation_group` del dataset: non si salvano (un
  caricamento successivo può aggiungerli senza perdere nulla).
- Uso del MET: si salva soltanto.

## Piano tecnico

Si applicano D-001, D-003, D-004, D-009, D-012: SQLite, SQLAlchemy 2.x + Alembic (`render_as_batch`), dipendenza
`CurrentUser`, test su file SQLite migrato con Alembic.

- **Contesto**: il pacchetto è npm, il backend è Python e in CI il job `backend` non ha Node. Già deciso nella
  feature: il dataset si copia dallo stage `frontend` durante la build Docker e si carica nel DB all'avvio del
  container. Restano da decidere: come il backend riceve i file, schema, come si riconosce un dataset già
  caricato, cosa succede se il caricamento fallisce, come si cerca, il contratto delle API.

- **Decisione 1 — Dataset nell'immagine**:
  - `@repdb/exercises` in `frontend/package.json` con versione **esatta** `2026.11.1` (senza `^`). È un file del
    frontend toccato da un'issue backend: è infrastruttura condivisa, serve prima al backend.
  - Nel `Dockerfile` lo stage `backend` (base di `dev` e `prod`) copia in `/backend/dataset/`
    `exercises.json` e `package.json` del pacchetto da `/frontend/node_modules/@repdb/exercises/` dello stage
    `frontend`. Percorso configurabile con `EXERCISES_DATASET_DIR` (default `/backend/dataset`).
  - Il file dei nomi italiani **non** passa dallo stage frontend: sta in `backend/app/exercises/names_it.json`,
    versionato, perché lo legge solo il caricamento (il frontend riceve i nomi dalle API). Piccola correzione
    alla feature, che lo dava copiato dallo stage frontend.
  - Scartato: scaricare il tarball da npm nello stage backend (versione fissata in due posti).

- **Decisione 2 — Schema**: due tabelle, senza `user_id` (dati comuni, sola lettura dalle API).
  - `exercises`: vedi Impatto. Muscoli come **colonne JSON** (liste di codici).
    - Scartata la tabella collegata `exercise_muscles`: oggi i muscoli si leggono sempre insieme all'esercizio
      e non si filtra per muscolo; per le statistiche future SQLite ha `json_each`. Si può introdurre dopo con
      una migrazione, ricaricando dal dataset.
  - Immagini: tre colonne `image_start`, `image_peak`, `image_main` con il **solo nome del file**
    (es. `arnold-press-peak.webp`); dove vengono servite lo decide il frontend.
  - `is_active`: `false` per gli esercizi non più presenti nel dataset. Restano nel DB e raggiungibili dal
    dettaglio (per routine e sessioni future), ma escono da elenco e filtri.
  - `exercise_catalog_state`: una riga con l'impronta dell'ultimo caricamento (Decisione 3).

- **Decisione 3 — Quando ricaricare**: impronta SHA-256 di `exercises.json` + `names_it.json` + una costante
  `LOADER_VERSION` nel codice. Se coincide con quella salvata, il caricamento esce subito.
  - A — confronto della sola versione del pacchetto: più semplice / contro: una correzione a un nome italiano
    senza aggiornare il pacchetto non verrebbe mai applicata.
  - B — ricaricare a ogni avvio: nessuno stato / contro: 708 scritture a ogni riavvio, contro il requisito.
  - **Proposta**: impronta (copre nuovo pacchetto, traduzioni corrette, modifiche al caricamento).

- **Decisione 4 — Caricamento e fallimenti**: modulo eseguibile `python -m app.exercises.sync`, lanciato nel
  `CMD` di `dev` e `prod` tra `alembic upgrade head` e Uvicorn.
  - Ogni record è validato con un modello Pydantic (campi extra ignorati); tutto in **una transazione**: o si
    applica l'intero dataset o niente.
  - Upsert per `id`; gli `id` presenti nel DB ma assenti dal dataset diventano `is_active = false`.
  - Esercizi senza nome italiano: `name_it` = nome inglese, elenco nei log (warning).
  - **Un fallimento all'avvio non blocca l'app**: errore nei log, Uvicorn parte con il catalogo precedente.
    Scartato il blocco dell'avvio: un dataset non valido manderebbe il container in riavvio continuo e l'intera
    app (diario, allenamenti) fuori servizio per un problema del solo catalogo.
  - **Verifica in build**: nello stage `backend` un `RUN` esegue migrazioni + caricamento su un DB temporaneo
    e fallisce se il caricamento fallisce o carica zero esercizi. Così un pacchetto incompatibile rompe la CI
    (job `image`) e non arriva sul Pi.
  - Opzione `--check`: stampa quanti esercizi ha il dataset e quali `id` non hanno un nome italiano, senza
    scrivere nel DB.

- **Decisione 5 — Ricerca**: colonna `search_text` = nome italiano + nome inglese **normalizzati in Python**
  (`casefold` + rimozione degli accenti con `unicodedata`). La query `q` si normalizza allo stesso modo, si
  divide in parole e ogni parola deve comparire (`LIKE '%parola%'`, con escape di `%` e `_`).
  - Cercare anche nel nome inglese è un'aggiunta rispetto alla feature: molti esercizi si conoscono col nome
    inglese ("deadlift", "pull up").
  - Scartati: `COLLATE NOCASE` (non gestisce gli accenti); FTS5 (tabella virtuale e migrazione a mano per 708
    righe, niente ricerca per sottostringa).
  - Ordinamento: `name_it` (`COLLATE NOCASE`), poi `id`.

- **Contratto** (tutte le risposte JSON; senza sessione valida `401`):

  `GET /api/exercises?q=&body_part=&equipment=&limit=&offset=`
  - `q` facoltativo (max 100 caratteri); `body_part` e `equipment` facoltativi, codici del dataset;
    `equipment=none` = esercizi senza attrezzatura; `limit` 1–100 (default 30); `offset` ≥ 0 (default 0).
  - `200`:
    ```json
    {
      "items": [
        { "id": "arnold-press", "name": "Arnold press", "body_part": "shoulders",
          "equipment": "dumbbell", "image": "arnold-press-peak.webp" }
      ],
      "total": 88, "limit": 30, "offset": 0
    }
    ```
    `name` è il nome italiano; `equipment` può essere `null`; `image` è la miniatura (`peak`, altrimenti
    `main`, altrimenti `start`; `null` se non c'è). Solo esercizi attivi. Un codice di filtro sconosciuto dà
    `items: []`, non un errore.
  - `422`: `limit`/`offset` fuori intervallo o `q` troppo lungo.

  `GET /api/exercises/filters`
  - `200`: `{ "body_parts": ["back", "chest", ...], "equipment": ["none", "barbell", ...] }` — valori presenti
    tra gli esercizi attivi, in ordine alfabetico di codice; `"none"` per primo se esistono esercizi senza
    attrezzatura.

  `GET /api/exercises/{id}`
  - `200`:
    ```json
    {
      "id": "arnold-press", "name": "Arnold press", "name_en": "Arnold Press",
      "category": "strength", "body_part": "shoulders", "equipment": "dumbbell",
      "difficulty": "intermediate", "force_type": "push", "mechanic": "compound",
      "is_unilateral": false, "is_bodyweight": false,
      "primary_muscles": ["anterior_deltoid", "lateral_deltoid"],
      "secondary_muscles": ["serratus_anterior", "trapezius", "triceps_brachii"],
      "images": { "start": "arnold-press-start.webp", "peak": "arnold-press-peak.webp", "main": null },
      "is_active": true
    }
    ```
  - `404`: esercizio inesistente.

- **Decisione 6 — Fallback per le rotte del frontend**: oggi `StaticFiles(html=True)` risponde `404` a un
  indirizzo come `/plan` se la pagina viene ricaricata. In `main.py` il mount diventa una sottoclasse di
  `StaticFiles` che, per una richiesta `GET` senza file corrispondente, restituisce `index.html` **solo se**
  il percorso non inizia con `/api/` e l'ultimo segmento non ha un'estensione (un'immagine mancante resta
  `404`).
  - Scartato l'hash routing nel frontend (`/#/plan`): nessuna modifica al backend, ma indirizzi non standard.

- **Impatto**:
  - File nuovi: `backend/app/exercises/{__init__,models,schemas,service,router,sync}.py`,
    `backend/app/exercises/names_it.json`, `backend/alembic/versions/0002_exercises.py`,
    `backend/tests/data/exercises_fixture.json` (pochi esercizi **inventati**, stessa struttura del dataset:
    nessun record reale nel repo), `backend/tests/test_exercises_{sync,api}.py`, `backend/tests/test_static.py`.
  - File modificati: `Dockerfile`, `frontend/package.json`, `frontend/package-lock.json`,
    `backend/app/main.py`, `backend/app/core/config.py`, `backend/alembic/env.py`, `README.md`,
    `brain/architettura.md`.
  - Schema (revisione `0002_exercises`):
    - `exercises`: `id` TEXT PK; `name_it` TEXT; `name_en` TEXT; `search_text` TEXT; `category` TEXT;
      `body_part` TEXT NULL (indice `ix_exercises_body_part`); `equipment` TEXT NULL (indice
      `ix_exercises_equipment`); `difficulty`, `force_type`, `mechanic` TEXT NULL; `met` FLOAT NULL;
      `is_unilateral`, `is_bodyweight` BOOLEAN; `primary_muscles`, `secondary_muscles` JSON; `image_start`,
      `image_peak`, `image_main` TEXT NULL; `is_active` BOOLEAN (default vero).
    - `exercise_catalog_state`: `id` INTEGER PK (sempre 1); `fingerprint` TEXT; `dataset_version` TEXT;
      `synced_at` `UTCDateTime`.
  - Nuove dipendenze: `@repdb/exercises@2026.11.1` (npm; solo dati e immagini, nessuna dipendenza, nessuno
    script di installazione, nessun binario: nessun problema ARM64). Nessuna nuova dipendenza Python.
  - Rischi:
    - l'immagine Docker cresce di circa 2,6 MB (JSON) in questa issue e di circa 23 MB con le immagini (FE);
    - la build dello stage `dev` ora richiede anche `npm ci` (già in cache per il container frontend);
    - dopo aver aggiunto la dipendenza, il container dev del frontend va ricreato con il volume
      (`up -d --build -V frontend`) e, se si usa `npm` in locale, serve `npm install`;
    - licenza: il repo pubblico contiene solo nomi italiani per `id`, non il dataset.
- **Decisioni registrate**: D-016 (`brain/decisioni.md`)

## Passi

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.

**Chi scrive (D-017, dal 2026-11-22)**: i passi 1 e 2 li ha scritti Claude. I passi 3, 5 e 6 li scrive
l'utente (codice, test e modifiche al `Dockerfile`); il piano qui sotto resta come guida, non come vincolo. Il
passo 4 (nomi in italiano) resta a Claude.

Comandi in dev: `./script/start-dev.sh`; test con
`docker compose -f docker-compose.dev.yaml exec app python -m pytest -v`.

### Passo 1 — Dataset nell'immagine e crediti

- **Stato**: fatto (2026-11-21)
- **Obiettivo**: le immagini Docker `dev` e `prod` contengono `exercises.json` della versione fissata; il repo
  dichiara l'attribuzione.
- **Lavoro**:
  - `frontend/package.json` + lock: `@repdb/exercises` a `2026.11.1` esatta.
  - `Dockerfile`: copia di `exercises.json` e `package.json` del pacchetto in `/backend/dataset/`.
  - `core/config.py`: `exercises_dataset_dir` da `EXERCISES_DATASET_DIR`.
  - `README.md`: riga "Exercise data by [RepDB](https://repdb.co)" con rimando alla licenza del pacchetto.
- **Definition of done**:
  - [x] `docker compose -f docker-compose.dev.yaml exec app python -c "import json; print(json.load(open('/backend/dataset/exercises.json'))['count'])"` stampa `708`.
  - [x] `docker build --target prod .` termina senza errori.
  - [x] In `frontend/package.json` la versione è `"2026.11.1"` senza `^` o `~`.
  - [x] `git ls-files | grep -E "exercises\.json|\.webp$"` non restituisce nulla.
  - [x] Il `README.md` mostra il link a RepDB.
  - [x] Test backend verdi; in `frontend/` `npm run lint` e `npm run build` senza errori.

### Passo 2 — Modello e migrazione

- **Stato**: fatto (2026-11-22)
- **Obiettivo**: le tabelle `exercises` e `exercise_catalog_state` esistono, create da Alembic.
- **Lavoro**:
  - `exercises/models.py` (`Exercise`, `ExerciseCatalogState`); import in `alembic/env.py`.
  - revisione `0002_exercises` (autogenerate + revisione manuale).
  - `brain/architettura.md`: sezione "allenamento (ALL-001)" nel modello dati.
- **Definition of done**:
  - [x] `alembic upgrade head` su DB vuoto crea le due tabelle con gli indici `ix_exercises_body_part` e
        `ix_exercises_equipment` (test).
  - [x] `alembic upgrade head` su un DB fermo alla revisione `0001` con un utente esistente mantiene l'utente
        e crea le tabelle (test).
  - [x] `alembic downgrade 0001` rimuove le due tabelle (test).
  - [x] `alembic check` non rileva differenze tra modelli e migrazioni.
  - [x] Test backend verdi.

### Passo 3 — Caricamento automatico all'avvio

- **Stato**: da fare
- **Obiettivo**: avviando il container il DB contiene il catalogo, per ora con i nomi inglesi come ripiego.
- **Lavoro**:
  - `exercises/sync.py`: lettura e validazione del dataset, normalizzazione per `search_text`, upsert,
    `is_active`, impronta, opzione `--check`; `names_it.json` inizialmente vuoto (`{}`).
  - `Dockerfile`: caricamento nel `CMD` di `dev` e `prod` (non bloccante) e verifica in build nello stage
    `backend`.
  - Test su `tests/data/exercises_fixture.json`.
- **Definition of done**:
  - [ ] Dopo `./script/start-dev.sh` su DB vuoto:
        `docker compose -f docker-compose.dev.yaml exec app python -c "from sqlalchemy import text; from app.core.db import get_engine; print(get_engine().connect().execute(text('select count(*) from exercises')).scalar())"` stampa `708`.
  - [ ] Riavviando il container (`docker compose -f docker-compose.dev.yaml restart app`) i log dicono che il
        catalogo è già aggiornato e il conteggio resta `708`.
  - [ ] Test: due caricamenti di fila non creano duplicati e il secondo non scrive nulla (impronta uguale).
  - [ ] Test: cambiando un record del dataset il caricamento aggiorna la riga esistente.
  - [ ] Test: un esercizio nel DB ma assente dal dataset resta nel DB con `is_active = false`.
  - [ ] Test: un esercizio senza nome italiano ha `name_it` uguale al nome inglese.
  - [ ] Test: un dataset con un record non valido non modifica il DB (transazione annullata).
  - [ ] Con `EXERCISES_DATASET_DIR` puntata a una cartella inesistente il container parte comunque e
        `GET /api/auth/me` risponde (errore del caricamento nei log).
  - [ ] `docker build --target prod .` esegue la verifica in build e termina senza errori.
  - [ ] Test backend verdi.

### Passo 4 — Nomi in italiano

- **Stato**: da fare
- **Obiettivo**: tutti gli esercizi hanno un nome italiano rivisto dall'utente.
- **Lavoro**:
  - `names_it.json` con i 708 nomi: traduzione prodotta da Claude in sessione dal nome inglese (nessun servizio
    esterno, nessuna dipendenza), con i termini d'uso in palestra (es. "panca piana", "stacco da terra") e i
    nomi che in italiano restano in inglese ("squat", "plank").
  - Per la revisione: tabella `id` / inglese / italiano generata fuori dal repo (cartella temporanea), da
    scorrere e correggere; le correzioni si riportano nel file.
- **Definition of done**:
  - [ ] `docker compose -f docker-compose.dev.yaml exec app python -m app.exercises.sync --check` riporta 708
        esercizi e 0 senza nome italiano.
  - [ ] `names_it.json` non contiene `id` estranei al dataset (riportato dallo stesso comando).
  - [ ] Dopo il riavvio del container, la query
        `select count(*) from exercises where name_it = name_en` restituisce solo gli esercizi il cui nome
        resta volutamente inglese (elenco riportato all'utente).
  - [ ] L'utente ha scorso la tabella di revisione e confermato i nomi.
  - [ ] Test backend verdi.

### Passo 5 — API del catalogo

- **Stato**: da fare
- **Obiettivo**: elenco con ricerca, filtri e paginazione, filtri disponibili e dettaglio, come da contratto.
- **Lavoro**:
  - `exercises/schemas.py`, `service.py`, `router.py`; router registrato in `main.py` sotto `/api/exercises`
    prima del mount statico; `/filters` dichiarato prima di `/{id}`.
  - Test API con il catalogo di prova caricato da fixture.
- **Definition of done**:
  - [ ] Test: senza cookie i tre endpoint rispondono `401`.
  - [ ] Test: `q=panca`, `q=PANCA` e una query con accenti diversi dal nome salvato danno lo stesso risultato;
        una query di due parole trova solo gli esercizi che le contengono entrambe.
  - [ ] Test: `body_part` + `equipment` insieme restituiscono solo esercizi con entrambi i valori;
        `equipment=none` solo esercizi senza attrezzatura.
  - [ ] Test: `limit=2&offset=2` restituisce la seconda pagina e `total` è il totale dei risultati; `limit=0`
        e `limit=101` danno `422`.
  - [ ] Test: un esercizio non attivo non compare in elenco e filtri, ma il dettaglio risponde `200`.
  - [ ] Test: `GET /api/exercises/inesistente` dà `404`.
  - [ ] Test: le risposte non contengono `met` né `search_text`.
  - [ ] In dev, da `http://localhost:8000/docs` dopo il login: `GET /api/exercises?q=panca` restituisce esercizi
        con "panca" nel nome e `total` > 0; `GET /api/exercises/filters` restituisce 9 parti del corpo e 65
        valori di attrezzatura (64 + `none`).
  - [ ] Test backend verdi.

### Passo 6 — Fallback per le rotte del frontend

- **Stato**: da fare
- **Obiettivo**: in produzione un indirizzo del frontend (es. `/plan`) aperto direttamente carica l'app.
- **Lavoro**:
  - `main.py`: sottoclasse di `StaticFiles` con il fallback su `index.html` e funzione di mount riusabile nei
    test; `tests/test_static.py` con una cartella statica temporanea.
- **Definition of done**:
  - [ ] Test: `GET /plan` e `GET /plan/exercises/abc` restituiscono `200` con il contenuto di `index.html`.
  - [ ] Test: `GET /api/inesistente` resta `404` JSON; `GET /exercise-images/manca.webp` resta `404`.
  - [ ] Test: un file statico esistente viene servito normalmente.
  - [ ] Con l'immagine prod locale (`docker build --target prod -t fitter-prova .` e
        `docker run --rm -p 8001:8000 -e COOKIE_SECURE=false -v <cartella temporanea>:/data fitter-prova`)
        `http://localhost:8001/plan` mostra l'app (login o home), non un 404.
  - [ ] Test backend verdi.

## Note di implementazione

Scostamenti dal piano, problemi incontrati, esito delle verifiche di ogni passo.

### Passo 1 (fatto 2026-11-21, confermato dall'utente)

- **Scostamento**: il `README.md` alla radice del repo non esisteva (il piano lo dava tra i file modificati): è
  stato **creato**, con una breve descrizione del progetto e la sezione "Crediti".
- `Settings.exercises_dataset_dir` ha un valore di default nel dataclass (`/backend/dataset`), così i test che
  costruiscono `Settings(...)` a mano restano validi.
- Il pacchetto non ha dipendenze né script di installazione (verificato con `npm view`); `exercises.json` sta
  nella radice del pacchetto e ha le chiavi `name`, `homepage`, `license`, `schema_version` (3), `count`,
  `note`, `exercises`. La versione si legge dal `package.json` del pacchetto, non dal JSON.
- Sul PC di sviluppo `npm run lint` fuori dal container fallisce: un criterio di Controllo applicazioni di
  Windows blocca il binario nativo di oxlint. Non dipende da questa issue; il lint è stato eseguito nel
  container `frontend`.
- Esito delle verifiche:
  - conteggio nel container dev: `708`; `/backend/dataset/` contiene `exercises.json` (2,6 MB) e
    `package.json` (versione `2026.11.1`);
  - `docker build --target prod .`: terminato senza errori; anche l'immagine prod contiene il dataset (`708`);
  - `frontend/package.json`: `"@repdb/exercises": "2026.11.1"`;
  - `git ls-files | grep -E "exercises\.json|\.webp$"`: nessun risultato;
  - test backend: 61 superati; frontend: lint 0 errori (nel container), `npm run build` senza errori.

### Passo 2 (fatto 2026-11-22, confermato dall'utente)

- **Scostamento**: i test della migrazione stanno in un file nuovo non elencato nell'Impatto,
  `backend/tests/test_exercises_migration.py` (i file `test_exercises_{sync,api}.py` arrivano con i passi 3 e 5).
- `is_active` ha il valore predefinito solo lato Python (`default=True` nel modello), senza `server_default`
  nel DB: le righe le scrive solo il caricamento, tramite l'ORM.
- `exercise_catalog_state.id` è dichiarato con `autoincrement=False`: la riga è sempre quella con `id = 1`.
- La revisione è stata generata con `alembic revision --autogenerate --rev-id 0002 -m "exercises"` su un DB
  temporaneo fermo alla `0001`, poi riordinata a mano (stile della `0001`, commenti); nessuna operazione
  aggiunta o tolta rispetto a quelle generate.
- Il DB di sviluppo (`./data`) resta alla `0001` finché il container `app` non viene riavviato (le migrazioni
  girano all'avvio).
- Esito delle verifiche:
  - `test_upgrade_head_creates_catalog_tables_and_indexes`: tabelle e indici `ix_exercises_body_part`,
    `ix_exercises_equipment` creati su DB vuoto;
  - `test_upgrade_from_0001_keeps_existing_user`: utente creato alla `0001` ancora presente dopo l'upgrade;
  - `test_downgrade_to_0001_removes_catalog_tables`: le due tabelle spariscono, `users` e `sessions` restano;
  - `alembic check` (DB temporaneo migrato a `head`): `No new upgrade operations detected.`; lo stesso
    controllo è coperto dal test esistente `test_models_match_migrations`;
  - test backend: 65 superati (61 + 4 nuovi).

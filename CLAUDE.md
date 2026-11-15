# CLAUDE.md

Guida per Claude Code (e per chiunque lavori al progetto).

## Il progetto

**Fitter**: web app (PWA) personale per
1. **Allenamento in palestra**: schede, esercizi, sessioni, serie/ripetizioni/carichi, progressi.
2. **Tracciamento calorie**: alimenti, pasti, diario giornaliero, obiettivi calorici e macro.

Viene hostata su un **Raspberry Pi** (architettura ARM, risorse limitate).

## Documentazione delle feature: cartella `brain/`

`brain/` è la fonte di verità su *cosa* costruire e *perché*. Prima di implementare qualcosa:
1. Leggi `brain/README.md` (indice e convenzioni).
2. Leggi il file della feature in `brain/features/` e le decisioni in `brain/decisioni.md`.
3. Se la feature non è documentata, proponi di crearne il file partendo da `brain/_template-feature.md` prima di scrivere codice.

Dopo aver implementato: aggiorna lo **stato** nel file della feature e in `brain/backlog.md`.
Ogni scelta architetturale non banale va registrata in `brain/decisioni.md`.

## Piano tecnico obbligatorio prima delle decisioni tecniche

Quando implementi una feature e stai per prendere una **decisione tecnica**, **fermati e proponi un piano tecnico all'utente prima di scrivere codice**. Rientrano tra le decisioni tecniche, per esempio:
- scegliere o aggiungere una libreria/dipendenza;
- creare o modificare tabelle, colonne, indici, vincoli (quindi ogni nuova migrazione Alembic);
- definire come implementare un flusso (es. login, sincronizzazione con API esterna, calcolo dei macro);
- definire o cambiare endpoint, formati di request/response, struttura dei moduli;
- qualunque scelta con più alternative ragionevoli o difficile da annullare.

Il piano va **documentato nel file della feature**, nella sezione `## Piano tecnico` (vedi `brain/_template-feature.md`), e deve contenere:
1. **Contesto**: cosa va deciso e perché.
2. **Alternative** considerate, con pro e contro.
3. **Proposta**: la soluzione raccomandata e il motivo.
4. **Impatto**: file/moduli toccati, modifiche allo schema DB (tabelle/colonne, migrazione), nuove dipendenze, rischi.
5. **Passi di implementazione** in ordine.

Flusso:
1. Scrivi il piano nel file della feature con stato `proposto`.
2. Presentalo all'utente in modo sintetico e **attendi l'approvazione esplicita**. Non implementare prima.
3. Se l'utente chiede modifiche, aggiorna il piano e ripresentalo.
4. Una volta approvato, segna il piano come `approvato` (con data) e registra le decisioni rilevanti in `brain/decisioni.md` (nuova voce `D-xxx`).
5. Se durante l'implementazione il piano va cambiato, fermati, aggiorna il piano e chiedi di nuovo l'approvazione.

Le decisioni già registrate in `brain/decisioni.md` non vanno riproposte: si applicano e basta. Le scelte banali (nomi di variabili locali, refactoring interni senza effetti esterni) non richiedono un piano.

## Stack

| Livello   | Tecnologia                                              |
|-----------|---------------------------------------------------------|
| Backend   | Python 3.14, FastAPI, Uvicorn (`backend/app/`)          |
| Database  | **SQLite** (vincolo: niente server DB sul Raspberry Pi) |
| ORM / migrazioni | SQLAlchemy 2.x (stile tipizzato) + Alembic       |
| Frontend  | React 19, TypeScript, Vite, `vite-plugin-pwa` (`frontend/`) |
| UI        | **HeroUI** + Tailwind CSS                               |
| Lint FE   | oxlint                                                  |
| Deploy    | Docker multi-stage (`Dockerfile`), docker compose       |

## Struttura

```
backend/app/main.py      # entrypoint FastAPI; in prod serve anche il frontend da /backend/static
backend/requirements.txt
frontend/                # app React/Vite (PWA)
Dockerfile               # stage: frontend, frontend-dev, frontend-build, backend, dev, prod
docker-compose.yaml      # prod: un solo container, volume ./data -> /data, porta 127.0.0.1:8000
docker-compose.dev.yaml  # dev: backend con --reload (8000) + Vite dev server (5173)
script/start-dev.sh      # avvia l'ambiente di sviluppo
.github/workflows/ci.yml # CI su ogni push/PR + rilascio immagine ARM64 su GHCR (D-008)
deploy/                  # deploy pull-based sul Raspberry Pi (script + timer systemd, vedi deploy/README.md)
brain/                   # documentazione feature e decisioni
```

Branch principale: **`main`**. Un push su `main` con `RELEASE_ENABLED=true` (variabile del repo GitHub) pubblica una nuova immagine, che il Pi installa entro 5 minuti: **`main` deve essere sempre rilasciabile** (CI verde).

## Comandi

```bash
# Sviluppo (backend :8000 con reload, frontend :5173)
./script/start-dev.sh            # = docker compose -f docker-compose.dev.yaml up -d --build

# Produzione (sul Raspberry Pi): automatico tramite deploy/deploy.sh (timer systemd)
# manuale: ./deploy/deploy.sh

# Frontend (dentro frontend/)
npm run lint
npm run build                    # tsc -b && vite build
```

File di ambiente: `.env` (prod) e `.env.dev` (dev) — non versionati.

## Regole e vincoli

### Database SQLite
- Il file del DB vive in **`/data`** nel container (montato da `./data` sull'host): mai salvarlo dentro l'immagine.
- Percorso configurabile via variabile d'ambiente (es. `DATABASE_URL`), con default su `/data`.
- Attivare `PRAGMA journal_mode=WAL` e `PRAGMA foreign_keys=ON` a ogni connessione.
- Uvicorn con **un solo worker**: SQLite gestisce male scritture concorrenti da più processi.
- Modelli con SQLAlchemy 2.x (`Mapped[...]`, `mapped_column`); ogni modifica allo schema = nuova revisione **Alembic** (autogenerate + revisione manuale), mai modifiche manuali al DB.
- Alembic con `render_as_batch=True` (limiti di `ALTER TABLE` in SQLite).
- Usare solo tipi/funzioni supportati da SQLite (niente feature specifiche di Postgres).

### Multi-utente
- L'app è multi-utente: ogni tabella con dati personali ha `user_id` e **ogni query è filtrata per l'utente autenticato**.
- Un endpoint non deve mai esporre dati di altri utenti; aggiungere test che lo verifichino.
- Autenticazione (D-006): cookie di sessione `HttpOnly` con sessioni nel DB; login con nickname + PIN di 4 cifre, salvato **solo come hash**. Il limite ai tentativi di login è obbligatorio (il PIN ha solo 10.000 combinazioni).

### Alimenti
- La ricerca usa API esterne + il DB interno (alimenti inseriti dagli utenti). Vedi D-005 in `brain/decisioni.md`.
- I valori nutrizionali usati nel diario si salvano in locale: il diario non dipende dalla disponibilità dell'API esterna.
- Le chiamate HTTP esterne stanno in un modulo client dedicato, con timeout e gestione errori.

### Raspberry Pi
- Risorse limitate: preferire dipendenze leggere, evitare librerie pesanti o servizi aggiuntivi (Redis, broker, ecc.) senza una decisione esplicita in `brain/decisioni.md`.
- Le immagini Docker devono funzionare su ARM64: evitare dipendenze senza wheel/binari ARM.
- Il servizio è esposto solo su `127.0.0.1`: l'accesso esterno passa da un reverse proxy.

### Backend
- API sotto il prefisso `/api/...` per non collidere con il frontend statico montato su `/`.
- I router delle API vanno registrati **prima** del mount `StaticFiles` in `main.py`.
- Validazione input/output con modelli Pydantic.
- Unità: pesi in **kg**, energia in **kcal**, macro in **grammi**; date/ore in UTC nel DB.

### Frontend
- È una PWA mobile-first: la UI va pensata per l'uso dal telefono in palestra.
- Componenti UI con **HeroUI** (D-007): usare prima i componenti HeroUI esistenti, styling con Tailwind e il tema HeroUI; niente altre librerie di componenti né CSS custom se non strettamente necessario.
- TypeScript strict, niente `any` senza motivo.
- Eseguire `npm run lint` e `npm run build` prima di considerare finito un lavoro sul frontend.

### Generale
- Lingua: documentazione e messaggi all'utente in **italiano**; codice (nomi di variabili, funzioni, tabelle) in **inglese**.
- Non fare commit senza richiesta esplicita.

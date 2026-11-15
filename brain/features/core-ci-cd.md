# CORE-003 — CI/CD: verifica automatica e rilascio sul Raspberry Pi

- **Area**: core
- **Stato**: in corso (manca la verifica su GitHub e sul Pi; entrypoint migrazioni dopo CORE-001)
- **Priorità**: alta
- **Dipende da**: —

## Obiettivo

A ogni push il codice viene verificato automaticamente (lint, build, test). Quando l'app sarà pubblicabile, il push sul branch principale avvia anche il rilascio: si costruisce l'immagine Docker e la si installa sul Raspberry Pi senza interventi manuali.

## User story

- Come sviluppatore voglio che ogni push e ogni PR vengano verificati, per accorgermi subito degli errori.
- Come sviluppatore voglio che un push sul branch principale aggiorni l'app sul Raspberry Pi, senza entrare via SSH e ricostruire a mano.

## Requisiti

- [ ] CI su ogni push e PR: lint + build del frontend, lint + test del backend, build dell'immagine Docker.
- [ ] Rilascio attivabile solo quando l'app è pubblicabile (interruttore esplicito).
- [ ] Immagine per **ARM64** (Raspberry Pi).
- [ ] Il deploy applica le migrazioni Alembic e non perde i dati in `/data`.
- [ ] Backup del file SQLite prima di ogni aggiornamento.
- [ ] Repo pubblica: nessun segreto nel codice o nei log, nessuna porta del Raspberry Pi esposta per il deploy.

## Fuori scope

- Ambienti di staging.
- Rollback automatico (resta manuale: si rilancia il tag dell'immagine precedente).

## Piano tecnico

- **Stato piano**: approvato (2026-11-14)
- **Contesto**: va deciso dove si costruisce l'immagine, dove la si salva e come arriva sul Raspberry Pi, tenendo conto che la repo è pubblica.

### 1. Piattaforma CI → GitHub Actions
Integrata con GitHub e gratuita per le repo pubbliche. Non ci sono alternative serie da valutare.

### 2. Build dell'immagine ARM64
- **A — Runner GitHub ARM nativo (`ubuntu-24.04-arm`)**: gratuito per le repo pubbliche, build veloce. *Contro*: nessuno rilevante.
- **B — Runner x86 + QEMU/buildx**: funziona ovunque. *Contro*: emulazione lenta (pip install / npm ci anche 5-10 volte più lenti).
- **C — Build sul Raspberry Pi**: *contro*: lenta, consuma le risorse del Pi in produzione.
- **Proposta: A.**

### 3. Registry delle immagini → GitHub Container Registry (GHCR)
`ghcr.io/<owner>/fitter`, gratuito, ci si autentica con il `GITHUB_TOKEN` del workflow (nessun segreto da creare). Tag: `latest` + SHA del commit (per il rollback).

### 4. Deploy sul Raspberry Pi
- **A — Pull dal Pi** (servizio systemd + timer sul Pi che ogni N minuti esegue `docker compose pull` e, se c'è un'immagine nuova, backup del DB + `up -d`).
  *Pro*: nessuna porta aperta, nessuna credenziale del Pi su GitHub, nessuna dipendenza esterna. *Contro*: ritardo di qualche minuto dopo il push.
- **B — Push via SSH da GitHub Actions**: *Pro*: deploy immediato. *Contro*: SSH del Pi esposto su internet (o serve una VPN tipo Tailscale) e una chiave privata nei segreti GitHub.
- **C — Runner self-hosted sul Pi**: *Contro*: **sconsigliato da GitHub per le repo pubbliche**, perché il codice di una PR esterna può finire in esecuzione sul Pi.
- **D — Watchtower o tool simili**: *Contro*: dipendenza esterna con accesso al socket Docker; il progetto originale non è più mantenuto attivamente.
- **Proposta: A** — è la più sicura con una repo pubblica e la più semplice da mantenere.

### 5. Attivazione del rilascio ("quando sarà pubblicabile")
- **A — Variabile di repository `RELEASE_ENABLED=true`**: finché è assente, i push su `main` eseguono solo la CI.
- **B — Rilascio solo su tag `v*`** (es. `v1.0.0`): rilascio esplicito e versionato, ma non avviene "al push".
- **Proposta: A** (rilascio al push su `main`, abilitato dalla variabile). Si può passare a B in futuro.

### 6. Migrazioni e dati
- All'avvio il container esegue `alembic upgrade head` prima di uvicorn (entrypoint).
- Lo script di deploy sul Pi copia `data/*.db` in `data/backups/` con timestamp prima dell'aggiornamento e conserva gli ultimi N backup.

- **Impatto**:
  - Nuovi file: `.github/workflows/ci.yml`, `.github/workflows/release.yml`, `deploy/` (script di deploy + unità systemd `.service`/`.timer`, istruzioni di installazione sul Pi).
  - `docker-compose.yaml` (prod): da `build:` a `image: ghcr.io/<owner>/fitter:latest`.
  - `Dockerfile`: entrypoint con le migrazioni (quando esisterà Alembic, CORE-001).
  - Requisito: sistema operativo **64-bit** sul Raspberry Pi.
  - Rischio: il pacchetto GHCR va reso pubblico (o il Pi va autenticato con un token in sola lettura).

- **Passi**:
  1. Workflow CI (lint/build/test) su push e PR.
  2. Workflow di release: build ARM64 → push su GHCR, condizionato da `RELEASE_ENABLED`.
  3. Modifica di `docker-compose.yaml` per usare l'immagine da GHCR.
  4. Script di deploy + timer systemd + guida di installazione sul Pi.
  5. Entrypoint con `alembic upgrade head` (dopo CORE-001).

- **Decisioni registrate**: D-008

## Criteri di accettazione

- [ ] Una PR con errori di lint/build fa fallire la CI.
- [ ] Con `RELEASE_ENABLED` assente, un push su `main` non pubblica immagini.
- [ ] Con `RELEASE_ENABLED=true`, un push su `main` pubblica `ghcr.io/.../fitter:latest` e `:<sha>` per arm64.
- [ ] Entro pochi minuti il Pi esegue la nuova versione, con il backup del DB creato e i dati preservati.

## Domande aperte

Nessuna. Risolte: branch principale `main`; OS Debian 13 (trixie) **arm64** (confermato 2026-11-15); controllo ogni 5 minuti; ultimi 10 backup.

## Note di implementazione

- Un solo workflow `ci.yml` (non due file separati): il job `image` dipende da `frontend` e `backend`, quindi il rilascio parte solo se la CI passa. Senza rilascio l'immagine viene comunque costruita (senza push) per verificare il `Dockerfile`.
- Verifica backend per ora minima (`compileall` + import di `app.main`, pytest se esiste `tests/`): linter e test backend vanno definiti con CORE-001.
- `deploy/deploy.sh` esegue anche `git merge --ff-only origin/main`, così le modifiche a `docker-compose.yaml` e agli script arrivano sul Pi.
- Backup del DB a container fermo (copia di `.db`, `-wal`, `-shm`) per garantire la consistenza.
- `.gitattributes` forza LF su script/YAML (il repo è sviluppato su Windows, gli script girano su Linux). `data/` aggiunta a `.gitignore`.
- Corretto `frontend/src/App.tsx`: gli import inutilizzati del template Vite facevano fallire `tsc -b` (e quindi la build Docker di produzione).
- **Da fare**: entrypoint con `alembic upgrade head` (dopo CORE-001).

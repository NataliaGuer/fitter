#!/usr/bin/env bash
# Deploy pull-based sul Raspberry Pi (CORE-003, D-008).
# Eseguito ogni 5 minuti dal timer systemd fitter-deploy.timer.
# Se su GHCR c'è un'immagine nuova: backup del DB SQLite, poi riavvio con la nuova immagine.
set -euo pipefail

APP_DIR="${APP_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
KEEP_BACKUPS="${KEEP_BACKUPS:-10}"
BRANCH="${BRANCH:-main}"
SERVICE=app

cd "$APP_DIR"
log() { echo "[deploy $(date -u +%FT%TZ)] $*"; }

# Aggiorna docker-compose.yaml e gli script di deploy dal branch principale
git fetch --quiet origin "$BRANCH"
git merge --ff-only --quiet "origin/$BRANCH"

image_ref="$(docker compose config --images | head -n 1)"
before="$(docker image inspect --format '{{.Id}}' "$image_ref" 2>/dev/null || true)"

docker compose pull --quiet "$SERVICE"
after="$(docker image inspect --format '{{.Id}}' "$image_ref")"

running="$(docker compose ps --status running --quiet "$SERVICE")"
if [[ "$before" == "$after" && -n "$running" ]]; then
  exit 0  # nessuna novità
fi

log "Nuova immagine: ${after}"

# Backup a container fermo, così il file SQLite (e il WAL) è consistente
if [[ -n "$running" ]]; then
  docker compose stop "$SERVICE"
fi

shopt -s nullglob
dbs=(data/*.db)
if (( ${#dbs[@]} > 0 )); then
  dest="data/backups/$(date -u +%Y%m%dT%H%M%SZ)"
  mkdir -p "$dest"
  for db in "${dbs[@]}"; do
    cp -p "$db" "$dest/"
    for extra in "$db-wal" "$db-shm"; do
      if [[ -f "$extra" ]]; then cp -p "$extra" "$dest/"; fi
    done
  done
  log "Backup DB in $dest"
  # Conserva solo gli ultimi KEEP_BACKUPS backup
  ls -1d data/backups/*/ | sort | head -n -"$KEEP_BACKUPS" | xargs -r rm -rf
fi

docker compose up -d "$SERVICE"
docker image prune -f >/dev/null
log "Deploy completato"

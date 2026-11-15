# Deploy sul Raspberry Pi

Il Pi **scarica** da solo le nuove versioni (nessuna porta aperta, nessuna credenziale del Pi su GitHub).
Flusso: push su `main` → GitHub Actions costruisce l'immagine ARM64 → GHCR → il timer sul Pi (ogni 5 min) la scarica, fa il backup del DB e riavvia.

Sul Pi **non si builda nulla**: l'immagine è costruita da GitHub Actions e il Pi la scarica soltanto.

**Ordine**: prima la configurazione su GitHub (sezione in fondo) e il primo rilascio, poi l'installazione sul Pi. Senza un'immagine su GHCR, `deploy.sh` fallisce al primo avvio.

## Prerequisiti

- Debian 13 **64-bit** (`dpkg --print-architecture` deve restituire `arm64`).
- Docker Engine + plugin `docker compose`, `git`.
- L'utente che esegue il deploy appartiene al gruppo `docker` (`sudo usermod -aG docker <utente>`).

## Installazione (una tantum)

```bash
sudo git clone https://github.com/<owner>/<repo>.git /opt/fitter
sudo chown -R <utente>:<utente> /opt/fitter
cd /opt/fitter
chmod +x deploy/deploy.sh

# Configurazione (mai committata)
cat > .env <<'EOF'
APP_IMAGE=ghcr.io/<owner>/<repo>
EOF
mkdir -p data

# Timer systemd (aggiorna User= in deploy/fitter-deploy.service se l'utente non è "pi")
sudo cp deploy/fitter-deploy.service deploy/fitter-deploy.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now fitter-deploy.timer

# Primo avvio manuale
./deploy/deploy.sh
```

`<owner>/<repo>` in minuscolo (GHCR richiede nomi minuscoli).

## Configurazione su GitHub (una tantum, da fare PRIMA dell'installazione sul Pi)

1. **Attivare il rilascio**: Settings → Secrets and variables → Actions → *Variables* → `RELEASE_ENABLED` = `true`.
   Finché non è impostata, la CI verifica il codice ma non pubblica immagini.
2. Dopo il primo rilascio, rendere **pubblico** il pacchetto su GHCR (profilo → Packages → app → Package settings → Change visibility), così il Pi lo scarica senza login.
   In alternativa: lasciarlo privato ed eseguire sul Pi `docker login ghcr.io` con un token con solo `read:packages`.

## Operazioni utili

```bash
systemctl list-timers fitter-deploy.timer   # prossimo controllo
journalctl -u fitter-deploy.service -n 50   # log dei deploy
docker compose logs -f app                        # log dell'app
```

**Rollback**: in `.env` non si cambia nulla; si esegue a mano
`docker pull ghcr.io/<owner>/<repo>:sha-<commit>` e
`docker tag ghcr.io/<owner>/<repo>:sha-<commit> ghcr.io/<owner>/<repo>:latest && docker compose up -d`.
Attenzione: al controllo successivo il timer riporta `latest` alla versione di GHCR. Per fermarlo: `sudo systemctl stop fitter-deploy.timer`.

**Ripristino DB**: fermare l'app (`docker compose stop app`) e copiare i file da `data/backups/<timestamp>/` in `data/`.

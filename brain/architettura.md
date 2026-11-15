# Architettura

## Panoramica

```
Browser / PWA (telefono)
        │  HTTPS (reverse proxy sul Raspberry Pi)
        ▼
127.0.0.1:8000 ── container "fitter"
                   ├── FastAPI  /api/*   → logica applicativa
                   ├── StaticFiles /     → build React (frontend/dist)
                   ├── SQLAlchemy + Alembic → SQLite /data/*.db (volume ./data)
                   └── client HTTP → API esterna alimenti
```

In sviluppo frontend (Vite, :5173) e backend (:8000) girano in due container separati.

## Moduli previsti

- **allenamento**: esercizi, schede, sessioni di allenamento, serie.
- **calorie**: alimenti, pasti, diario giornaliero, obiettivi.
- **core**: configurazione, accesso al DB, utenti e autenticazione (multi-utente).

## Modello dati

Date/ore in UTC con il tipo `UTCDateTime` (D-012); vincoli e indici con nomi standard (`pk_`, `uq_`, `fk_`, `ix_`).

### core (CORE-002)
- `users`: `id`, `nickname` (`COLLATE NOCASE`, unique), `pin_hash` (argon2id), `created_at`.
- `sessions`: `id`, `token_hash` (SHA-256 del token del cookie, unique), `user_id` → `users.id`
  (`ON DELETE CASCADE`), `created_at`, `last_seen_at`.

Ogni tabella futura con dati personali ha `user_id` e gli endpoint usano la dipendenza `CurrentUser`
(`backend/app/auth/deps.py`).

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

### allenamento (ALL-001)
Catalogo esercizi dal dataset RepDB (D-016): dati comuni a tutti gli utenti, in sola lettura dalle API, quindi
**senza `user_id`**. Revisione Alembic `0002`.
- `exercises`: `id` (TEXT, chiave = `id` del dataset, es. `arnold-press`), `name_it`, `name_en`, `search_text`
  (nomi italiano + inglese normalizzati per la ricerca), `category`, `body_part` (indice), `equipment` (indice,
  `NULL` = senza attrezzatura), `difficulty`, `force_type`, `mechanic`, `met`, `is_unilateral`, `is_bodyweight`,
  `primary_muscles` e `secondary_muscles` (JSON, liste di codici), `image_start`, `image_peak`, `image_main`
  (solo nome del file), `is_active` (`false` per gli esercizi spariti dal dataset: non si cancellano mai).
- `exercise_catalog_state`: una sola riga (`id` = 1) con `fingerprint` (impronta dell'ultimo caricamento),
  `dataset_version`, `synced_at`.

Ogni tabella futura con dati personali ha `user_id` e gli endpoint usano la dipendenza `CurrentUser`
(`backend/app/auth/deps.py`).

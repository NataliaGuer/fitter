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

Da definire man mano che le feature vengono documentate in `features/`.

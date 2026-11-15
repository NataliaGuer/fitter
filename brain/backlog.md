# Backlog

| ID | Feature | Area | Stato | Priorità | File |
|----|---------|------|-------|----------|------|
| CORE-001 | Setup DB SQLite, SQLAlchemy e Alembic | core | pronta | alta | — |
| CORE-002 | Utenti e autenticazione (nickname + PIN, cookie di sessione) | core | da definire | alta | `features/core-autenticazione.md` |
| CORE-003 | CI/CD: verifica automatica e rilascio sul Raspberry Pi | core | in corso | alta | `features/core-ci-cd.md` |
| CAL-001 | Catalogo alimenti: ricerca su API esterne + DB interno | calorie | da definire | alta | — |

## Aree

### Allenamento in palestra
Nessuna feature definita.

### Tracciamento calorie
- CAL-001 — Catalogo alimenti (D-005): ricerca su API esterne, inserimento manuale degli alimenti non trovati, copia locale dei valori nutrizionali.

### Core
- CORE-001 — Setup DB (D-001, D-003): prerequisito per tutto il resto.
- CORE-002 — Utenti e autenticazione (D-004, D-006): prerequisito per tutti i dati personali.
- CORE-003 — CI/CD con GitHub Actions e deploy sul Raspberry Pi (D-008): implementata, da verificare su GitHub e sul Pi.

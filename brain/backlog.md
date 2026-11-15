# Backlog

| ID | Feature | Area | Stato | Priorità | File |
|----|---------|------|-------|----------|------|
| CORE-001 | Setup DB SQLite, SQLAlchemy e Alembic | core | in corso | alta | incluso nel piano di `features/core-autenticazione.md` |
| CORE-002 | Utenti e autenticazione (nickname + PIN, sessione permanente) | core | in corso | alta | `features/core-autenticazione.md` |
| CORE-002-BE | ↳ Autenticazione — backend | core | in corso | alta | `features/core-autenticazione.md` |
| CORE-002-FE | ↳ Autenticazione — frontend | core | in corso | alta | `features/core-autenticazione.md` |
| CORE-003 | CI/CD: verifica automatica e rilascio sul Raspberry Pi | core | in corso | alta | `features/core-ci-cd.md` |
| CAL-001 | Catalogo alimenti: ricerca su API esterne + DB interno | calorie | da definire | alta | — |

## Issue

Le feature si implementano solo tramite issue (`issue/<feature>/`, skill `/feature-to-issue`).

| ID | Issue | Feature | Lato | Stato | File |
|----|-------|---------|------|-------|------|
| CORE-002-BE-01 | Setup DB e API di autenticazione (include CORE-001) | CORE-002 | backend | in corso (approvata 2026-11-15) | `issue/core-autenticazione/be-01-api-autenticazione.md` |
| CORE-002-FE-01 | Setup HeroUI, schermate di accesso e sessione | CORE-002 | frontend | bozza | `issue/core-autenticazione/fe-01-accesso-e-sessione.md` |

## Aree

### Allenamento in palestra
Nessuna feature definita.

### Tracciamento calorie
- CAL-001 — Catalogo alimenti (D-005): ricerca su API esterne, inserimento manuale degli alimenti non trovati, copia locale dei valori nutrizionali.

### Core
- CORE-001 — Setup DB (D-001, D-003): prerequisito per tutto il resto.
- CORE-002 — Utenti e autenticazione (D-004, D-006): prerequisito per tutti i dati personali. Divisa in backend (CORE-002-BE, include CORE-001) e frontend (CORE-002-FE).
- CORE-003 — CI/CD con GitHub Actions e deploy sul Raspberry Pi (D-008): implementata, da verificare su GitHub e sul Pi.

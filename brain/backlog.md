# Backlog

| ID | Feature | Area | Stato | Priorità | File |
|----|---------|------|-------|----------|------|
| CORE-001 | Setup DB SQLite, SQLAlchemy e Alembic | core | fatta | alta | incluso nel piano di `features/core-autenticazione.md` |
| CORE-002 | Utenti e autenticazione (nickname + PIN, sessione permanente) | core | fatta | alta | `features/core-autenticazione.md` |
| CORE-002-BE | ↳ Autenticazione — backend | core | fatta | alta | `features/core-autenticazione.md` |
| CORE-002-FE | ↳ Autenticazione — frontend | core | fatta | alta | `features/core-autenticazione.md` |
| CORE-003 | CI/CD: verifica automatica e rilascio sul Raspberry Pi | core | in corso | alta | `features/core-ci-cd.md` |
| CORE-004 | Home page a card e barra di navigazione | core | fatta | alta | `features/core-home.md` |
| CORE-005 | Restyling neobrutalista (palette, font, tema HeroUI) | core | fatta | media | `features/core-design-neobrutalista.md` |
| ALL-001 | Catalogo esercizi (dataset RepDB nel DB, nomi in italiano) | allenamento | in corso | alta | `features/allenamento-esercizi.md` |
| ALL-002 | Mappa muscolare con MuscleMap-ts nel dettaglio esercizio | allenamento | da definire | media | `features/allenamento-mappa-muscolare.md` |
| CAL-001 | Catalogo alimenti: ricerca su API esterne + DB interno | calorie | da definire | alta | — |

## Issue

Le feature si implementano solo tramite issue (`issue/<feature>/`, skill `/feature-to-issue`).

| ID | Issue | Feature | Lato | Stato | File |
|----|-------|---------|------|-------|------|
| CORE-002-BE-01 | Setup DB e API di autenticazione (include CORE-001) | CORE-002 | backend | fatta (2026-11-15) | `issue/core-autenticazione/be-01-api-autenticazione.md` |
| CORE-002-FE-01 | Setup HeroUI, schermate di accesso e sessione | CORE-002 | frontend | fatta (2026-11-15) | `issue/core-autenticazione/fe-01-accesso-e-sessione.md` |
| CORE-004-FE-01 | Home a card con calendario settimanale e barra di navigazione | CORE-004 | frontend | fatta (2026-11-17) | `issue/core-home/fe-01-home-e-navigazione.md` |
| CORE-005-FE-01 | Tema neobrutalista per HeroUI e restyling delle schermate | CORE-005 | frontend | fatta (2026-11-17) | `issue/core-design-neobrutalista/fe-01-tema-neobrutalista.md` |
| ALL-001-BE-01 | Catalogo esercizi: dataset RepDB nel DB e API | ALL-001 | backend | in corso (approvata 2026-11-21) | `issue/allenamento-esercizi/be-01-catalogo-esercizi.md` |
| ALL-001-FE-01 | Catalogo esercizi: router, schermata Esercizi e dettaglio | ALL-001 | frontend | bozza | `issue/allenamento-esercizi/fe-01-catalogo-esercizi.md` |

## Aree

### Allenamento in palestra
- ALL-001 — Catalogo esercizi: pacchetto npm `@repdb/exercises` (708 esercizi, immagini incluse) caricato in SQLite, nomi tradotti in italiano, ricerca e filtri; attribuzione RepDB.
- ALL-002 — Mappa muscolare: installazione di `MuscleMap-ts` (versione fissata) e figura con muscolo target e secondari nel dettaglio esercizio. Dipende da ALL-001.

### Tracciamento calorie
- CAL-001 — Catalogo alimenti (D-005): ricerca su API esterne, inserimento manuale degli alimenti non trovati, copia locale dei valori nutrizionali.

### Core
- CORE-001 — Setup DB (D-001, D-003): prerequisito per tutto il resto.
- CORE-002 — Utenti e autenticazione (D-004, D-006): prerequisito per tutti i dati personali. Divisa in backend (CORE-002-BE, include CORE-001) e frontend (CORE-002-FE).
- CORE-004 — Home a card (calendario settimanale scorrevole, calorie e statistiche segnaposto) e barra di navigazione floating in basso: fatta.
- CORE-005 — Restyling neobrutalista di tutte le schermate (vedi `DESIGN.md`), tema chiaro Coral & Cream e scuro Dark Brut con switch: fatta.
- CORE-003 — CI/CD con GitHub Actions e deploy sul Raspberry Pi (D-008): implementata, da verificare su GitHub e sul Pi.

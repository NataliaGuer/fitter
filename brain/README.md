# brain/

Qui documentiamo **cosa** costruire e **perché**, prima di scrivere codice.

## Contenuto

| File / cartella             | Scopo                                                        |
|-----------------------------|--------------------------------------------------------------|
| `backlog.md`                | Elenco di tutte le feature con stato e priorità              |
| `features/`                 | Un file per feature, creato da `_template-feature.md`        |
| `_template-feature.md`      | Modello da copiare per una nuova feature                     |
| `decisioni.md`              | Registro delle decisioni architetturali (cosa, perché, quando) |
| `architettura.md`           | Panoramica tecnica e modello dati man mano che prende forma  |

## Convenzioni

- **Nome file feature**: `features/<area>-<nome-breve>.md`, in kebab-case.
  Aree: `allenamento`, `calorie`, `core` (utenti, impostazioni, infrastruttura).
  Esempio: `features/allenamento-schede.md`, `features/calorie-diario-pasti.md`.
- **ID feature**: `<AREA>-<numero>` (es. `ALL-001`, `CAL-001`, `CORE-001`), riportato nel backlog.
- **Stati**: `idea` → `da definire` → `pronta` → `in corso` → `fatta`.
  Una feature è `pronta` solo quando requisiti e criteri di accettazione sono chiari.
- Ogni feature aggiornata va riflessa anche in `backlog.md`.

## Flusso

1. Aggiungi la feature in `backlog.md` (stato `idea`).
2. Copia `_template-feature.md` in `features/` e compilalo.
3. Quando è chiara, passa a `pronta`.
4. Prima di ogni decisione tecnica si scrive il **piano tecnico** nella sezione `## Piano tecnico` del file della feature e lo si fa approvare all'utente (vedi `CLAUDE.md`). Solo dopo l'approvazione si implementa.
5. A lavoro finito, stato `fatta` e note su eventuali scostamenti.

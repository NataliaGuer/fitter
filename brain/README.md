# brain/

Qui documentiamo **cosa** costruire e **perché** (feature) e **come** costruirlo (issue), prima di scrivere codice.

## Contenuto

| File / cartella             | Scopo                                                        |
|-----------------------------|--------------------------------------------------------------|
| `backlog.md`                | Elenco di feature e issue con stato e priorità               |
| `features/`                 | Un file per feature, creato da `_template-feature.md`        |
| `issue/`                    | Una cartella per feature, con un file per issue creato da `_template-issue.md` (skill `/feature-to-issue`) |
| `_template-feature.md`      | Modello da copiare per una nuova feature                     |
| `_template-issue.md`        | Modello per una nuova issue                                  |
| `decisioni.md`              | Registro delle decisioni architetturali (cosa, perché, quando) |
| `architettura.md`           | Panoramica tecnica e modello dati man mano che prende forma  |

## Convenzioni

### Feature
- **Nome file**: `features/<area>-<nome-breve>.md`, in kebab-case.
  Aree: `allenamento`, `calorie`, `core` (utenti, impostazioni, infrastruttura).
  Esempio: `features/allenamento-schede.md`, `features/calorie-diario-pasti.md`.
- **ID**: `<AREA>-<numero>` (es. `ALL-001`, `CAL-001`, `CORE-001`), riportato nel backlog.
- **Stati**: `idea` → `da definire` → `approvata` → `in corso` → `fatta`.
  - `approvata`: requisiti e criteri di accettazione chiari, nessuna domanda aperta; si può trasformare in issue.
  - `in corso`: le sue issue sono approvate e in implementazione.
  - `fatta`: tutte le sue issue sono fatte.

### Issue
- Ogni issue riguarda **solo il backend** (`BE`) o **solo il frontend** (`FE`) di una feature.
- **ID**: `<ID feature>-<BE|FE>-<nn>` (es. `CORE-002-BE-01`, `CORE-002-FE-01`).
- **Cartella**: una per feature, con lo stesso nome del file della feature senza `.md`:
  `features/core-autenticazione.md` → `issue/core-autenticazione/`.
- **Nome file**: `issue/<nome-file-feature>/<be|fe>-<nn>-<nome-breve>.md`
  (es. `issue/core-autenticazione/be-01-api-autenticazione.md`).
- **Stati**: `bozza` → `approvata (AAAA-MM-GG)` → `in corso` → `fatta`.
- Contiene il **piano tecnico** e i **passi** incrementali; ogni passo ha una **definition of done** (DoD).
- **Stati dei passi**: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.
  Un passo diventa `fatto` solo quando l'utente conferma che la DoD è soddisfatta.

Ogni feature o issue aggiornata va riflessa anche in `backlog.md`.

## Flusso

1. Aggiungi la feature in `backlog.md` (stato `idea`).
2. Copia `_template-feature.md` in `features/` e compilalo.
3. Quando requisiti e criteri sono chiari, passa a `approvata`.
4. Trasforma la feature in issue con la skill `/feature-to-issue`: una o più issue backend e/o frontend, con
   piano tecnico e passi con DoD, in stato `bozza`.
5. L'utente approva le issue (decisioni registrate in `decisioni.md`). **Solo le issue approvate si implementano**,
   mai direttamente le feature.
6. Implementazione un passo alla volta: a fine passo si verificano i punti della DoD e l'utente conferma la chiusura
   prima di passare al successivo (vedi `CLAUDE.md`).
7. A lavoro finito: issue `fatta`, poi feature `fatta`, con note su eventuali scostamenti.

# <ID-ISSUE> — <Titolo>

- **Feature**: <ID feature> (`features/<file>.md`)
- **Lato**: backend | frontend
- **Stato**: bozza | approvata (AAAA-MM-GG) | in corso | fatta
- **Dipende da**: <ID di altre issue, se presenti>

## Obiettivo

Cosa consegna questa issue, in 2-3 frasi. Solo la parte **backend** o solo la parte **frontend** della feature.

## Requisiti coperti

Requisiti e criteri di accettazione della feature che questa issue soddisfa (copiati o richiamati).

- [ ] ...

## Fuori scope

- Ciò che resta all'altra issue (l'altro lato o una issue successiva).

## Piano tecnico

- **Contesto**: cosa va deciso e perché.
- **Alternative**:
  - A — ... (pro / contro)
  - B — ... (pro / contro)
- **Proposta**: soluzione scelta e motivazione.
- **Contratto**: endpoint, formati di request/response, tipi condivisi con l'altro lato (per il frontend: l'API che consuma).
- **Impatto**:
  - File/moduli nuovi e modificati.
  - Schema DB e migrazioni (solo backend).
  - Nuove dipendenze.
  - Rischi.
- **Decisioni registrate**: D-xxx (compilato all'approvazione)

## Passi

Ogni passo è un'unità di lavoro incrementale: lascia `main` rilasciabile (CI verde) e si chiude solo quando
l'utente conferma che la definition of done è soddisfatta.

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.

### Passo 1 — <titolo>

- **Stato**: da fare
- **Obiettivo**: cosa esiste alla fine del passo.
- **Lavoro**:
  - file da creare/modificare e cosa fare.
- **Definition of done**:
  - [ ] verifica concreta e controllabile (comando + risultato atteso, test che passa, controllo manuale).
  - [ ] `npm run lint` e `npm run build` (frontend) / test backend verdi.

### Passo 2 — <titolo>

- ...

## Note di implementazione

Scostamenti dal piano, problemi incontrati, esito delle verifiche di ogni passo.

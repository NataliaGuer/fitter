---
name: feature-to-issue
description: Trasforma una feature documentata in brain/features/ in una o più issue in brain/issue/<feature>/ (ognuna solo backend o solo frontend), con piano tecnico dettagliato e passi incrementali, ciascuno con la propria definition of done. Da usare quando l'utente chiede di "trasformare/convertire una feature in issue", "creare le issue di una feature", o prima di iniziare a implementare una feature che non ha ancora issue.
argument-hint: <ID feature o file in brain/features/, es. CORE-002>
---

# Feature → issue

Le feature in `brain/features/` descrivono **cosa** costruire e **perché**. Non si implementano direttamente:
prima vanno trasformate in **issue** in `brain/issue/<feature>/` (una cartella per feature), che descrivono **come**, passo per passo.
Questa skill produce le issue; **non scrive codice**.

Argomento: `$ARGUMENTS` (ID della feature, es. `CORE-002`, oppure il percorso del file). Se manca, chiedi
all'utente quale feature trasformare elencando quelle in `brain/backlog.md` nello stato `approvata`.

## 1. Raccogli il contesto

Leggi, nell'ordine:
1. `brain/README.md` (convenzioni, stati, nomi dei file).
2. Il file della feature in `brain/features/`.
3. `brain/decisioni.md`: le decisioni registrate **si applicano e non si ripropongono** come alternative.
4. `brain/architettura.md` e `brain/backlog.md`.
5. Le issue già presenti nella cartella della feature in `brain/issue/` (per non duplicare lavoro e per la numerazione).
6. Il codice esistente toccato dalla feature (`backend/app/`, `frontend/src/`, `Dockerfile`, CI, ...): il piano
   deve partire da com'è davvero il codice oggi, non da com'era quando è stata scritta la feature.

## 2. Verifica che la feature sia pronta

Fermati e chiedi all'utente prima di procedere se:
- lo stato della feature non è `approvata`;
- ci sono **domande aperte** non risolte o requisiti/criteri di accettazione vaghi;
- esistono già issue per la stessa feature (chiedi se vanno sostituite, integrate o lasciate).

Se nel file della feature c'è già una sezione `## Piano tecnico` (feature scritte col flusso precedente), usala
come punto di partenza: le scelte già approvate lì restano valide, vanno solo dettagliate in passi con DoD.

## 3. Dividi in issue

- Ogni issue riguarda **solo il backend** oppure **solo il frontend**, mai entrambi.
  - Backend: `backend/`, modelli, migrazioni Alembic, API, test Python.
  - Frontend: `frontend/`, componenti, pagine, client API, configurazione Vite/PWA.
  - File infrastrutturali (`Dockerfile`, compose, CI, `deploy/`): vanno nell'issue del lato che ne ha bisogno;
    se servono a entrambi, nell'issue backend.
- Una feature con un solo lato produce una sola issue. Se un lato è grande (più di ~8 passi), dividilo in più
  issue dello stesso lato, ognuna consegnabile da sola.
- Il **contratto API** (endpoint, request/response, codici di errore) è la frontiera tra le issue: va scritto in
  modo identico nell'issue backend e richiamato nell'issue frontend, che dichiara `Dipende da` l'issue backend.
  Se il contratto non è già nella feature, va definito qui ed è una decisione tecnica da far approvare.

Naming (vedi `brain/README.md`):
- ID: `<ID feature>-<BE|FE>-<nn>`, es. `CORE-002-BE-01`, `CORE-002-FE-01`.
- Cartella: `brain/issue/<nome-file-feature>/`, cioè il nome del file della feature senza `.md`
  (`features/core-autenticazione.md` → `brain/issue/core-autenticazione/`). Creala se non esiste.
- File: `brain/issue/<nome-file-feature>/<be|fe>-<nn>-<nome-breve>.md`, es.
  `brain/issue/core-autenticazione/be-01-api-autenticazione.md`.

## 4. Scrivi ogni issue

Parti da `brain/_template-issue.md` e compila tutte le sezioni. Stato iniziale: `bozza`.

### Piano tecnico
Rispetta le regole di `CLAUDE.md` (stack, vincoli SQLite, multi-utente, Raspberry Pi/ARM64, HeroUI, unità).
Per ogni decisione tecnica non già coperta da `brain/decisioni.md` (librerie, schema DB, flussi, endpoint,
struttura dei moduli): contesto, alternative con pro/contro, proposta motivata. Nell'impatto elenca file
precisi, tabelle/colonne/indici e migrazioni, dipendenze con versione, rischi.

Per le nuove dipendenze verifica che esistano, che la versione indicata sia reale e che abbiano wheel/binari ARM64.

### Passi incrementali
- Ordina i passi in modo che ognuno costruisca sul precedente e **lasci `main` rilasciabile** (CI verde,
  app funzionante): `main` va in produzione automaticamente sul Raspberry Pi.
- Un passo = una unità di lavoro rivedibile in una sessione (indicativamente 3–8 passi per issue). Niente passi
  "contenitore" tipo "implementare tutto il backend", né micro-passi tipo "creare un file vuoto".
- I test non sono un passo finale a parte: ogni passo che aggiunge comportamento include i propri test.
- Per ogni passo: **Obiettivo**, **Lavoro** (file e modifiche concrete), **Definition of done**.

### Definition of done
È l'elenco di controlli con cui l'**utente** decide che il passo è concluso. Ogni voce deve essere:
- **verificabile** da qualcuno che non ha scritto il codice: un comando con il risultato atteso, un test
  nominato che passa, una richiesta HTTP con la risposta attesa, un controllo manuale descritto
  (es. "da telefono, aprendo l'app dopo il login si vede la home senza passare dal login");
- **binaria**: soddisfatta o no, senza giudizi tipo "codice pulito" o "funziona bene";
- **limitata al passo**: non deve dipendere da passi successivi.

Includi sempre, a seconda del lato:
- backend: test (`pytest`) verdi; per modifiche allo schema, `alembic upgrade head` su DB vuoto e su DB con la
  revisione precedente; per dati personali, un test che verifica che un utente non veda i dati di un altro;
- frontend: `npm run lint` e `npm run build` senza errori; per la UI, verifica in vista mobile.

## 5. Aggiorna `brain/`

- Nel file della feature, sezione `## Issue`: elenco delle issue create con ID, lato, file e stato.
- In `brain/backlog.md`, tabella **Issue**: una riga per issue (ID, titolo, feature, lato, stato, file).
- Non modificare lo stato della feature finché le issue non sono approvate.

## 6. Presenta e attendi l'approvazione

Presenta all'utente, in italiano e in modo sintetico: le issue create, per ognuna le decisioni tecniche proposte
(con l'alternativa scartata) e l'elenco dei passi con la loro DoD in una riga. **Attendi l'approvazione esplicita.**

- Se l'utente chiede modifiche: aggiorna le issue e ripresentale.
- All'approvazione: stato dell'issue `approvata (AAAA-MM-GG)`; registra le decisioni non banali in
  `brain/decisioni.md` (nuova voce `D-xxx`) e riportane l'ID nel campo **Decisioni registrate**; aggiorna
  backlog e sezione `## Issue` della feature; feature in stato `in corso`.

Non iniziare l'implementazione in questa skill: l'implementazione di un'issue approvata segue il flusso a passi
descritto in `CLAUDE.md`.

# ALL-001 — Catalogo esercizi

- **Area**: allenamento
- **Stato**: da definire
- **Priorità**: alta
- **Dipende da**: CORE-002 (utente autenticato)

## Obiettivo

Dare all'app un catalogo di esercizi già pronto, in italiano, da consultare e da usare come base per le future
schede e sessioni di allenamento. Il catalogo nasce dal pacchetto npm pubblico
[`@repdb/exercises`](https://www.npmjs.com/package/@repdb/exercises) (708 esercizi con dati e immagini WebP
512 px, nomi in inglese/tedesco/spagnolo), a cui l'app aggiunge i nomi in italiano. I dati vengono caricati nel
database; le immagini arrivano con il pacchetto e finiscono nell'immagine Docker: nessun media da copiare a mano
sul Pi e nessuna chiamata a servizi esterni a runtime.

## User story

- Come utente voglio cercare un esercizio per nome (es. "panca") per trovarlo velocemente in palestra.
- Come utente voglio filtrare gli esercizi per parte del corpo e per attrezzatura per scoprire alternative con
  quello che ho a disposizione.
- Come utente voglio vedere il dettaglio di un esercizio (immagini di inizio e fine movimento, muscoli principali
  e secondari) per capire come eseguirlo e cosa allena.

## Requisiti

- [ ] **Dataset dal pacchetto**: `@repdb/exercises` come dipendenza con **versione fissata** (il pacchetto esce
  quasi ogni mese: niente aggiornamenti involontari). Il file `exercises.json` e le immagini non vengono copiati
  nel repo `fitter`: si leggono dal pacchetto installato.
- [ ] **Italiano**: ogni esercizio ha un nome in italiano; anche i valori di parte del corpo (9), attrezzatura
  (64, più "nessuna"), difficoltà e muscoli sono mostrati in italiano. Le traduzioni si producono con traduzione
  automatica + revisione a mano e vivono nel progetto, separate dal dataset (solo le traduzioni, non una copia):
  - nomi degli esercizi: un file JSON `{ "<id>": "<nome italiano>" }` (es. `"arnold-press": "Arnold press"`);
  - etichette dei codici (parte del corpo, attrezzatura, difficoltà, muscoli): mappa nel frontend; le API
    restituiscono i codici del dataset.

  Se manca una traduzione si mostra il nome inglese. Quando una nuova versione del pacchetto aggiunge esercizi,
  quelli senza nome italiano vengono segnalati nei log dal caricamento.
- [ ] **Dataset nell'immagine**: nella build Docker lo stage backend copia `exercises.json` e il file dei nomi
  italiani dallo stage frontend, dove il pacchetto è già installato. La versione resta fissata in un solo posto
  (`frontend/package.json`) e vale sia in sviluppo sia in produzione.
- [ ] **Catalogo nel database**: gli esercizi stanno in una tabella del DB SQLite, caricata **automaticamente
  all'avvio del container**, dopo le migrazioni e prima di Uvicorn: nessun comando da lanciare a mano.
  - Se la versione del dataset è già nel DB il caricamento non fa nulla.
  - Altrimenti aggiunge gli esercizi nuovi e aggiorna quelli esistenti, senza duplicati (chiave: `id` del
    dataset, es. `arnold-press`).
  - Gli esercizi spariti dal dataset **non vengono cancellati** dal DB: routine e sessioni future che li usano
    devono restare valide.
- [ ] Gli esercizi del catalogo sono **comuni a tutti gli utenti** (non hanno `user_id`) e in sola lettura dall'app.
- [ ] **Ricerca** per nome italiano, senza distinzione tra maiuscole/minuscole e accenti.
- [ ] **Filtri** per parte del corpo e attrezzatura, combinabili con la ricerca. Gli esercizi a corpo libero
  (senza attrezzatura nel dataset) si filtrano con la voce "nessuna attrezzatura".
- [ ] Risultati **paginati** (il catalogo non si scarica tutto in una volta).
- [ ] **Dettaglio** esercizio: nome, parte del corpo, attrezzatura, difficoltà, muscoli principali, muscoli
  secondari e immagini. Gli esercizi dinamici hanno due immagini (`start` e `peak`), quelli statici (tenute,
  stretching) una sola (`main`).
- [ ] **Immagini** servite come **asset statici del frontend** (copiate dal pacchetto nella build, circa 23 MB,
  incluse nell'immagine Docker): niente CDN esterno, così funzionano anche senza internet dietro la VPN. Si
  caricano a richiesta: non entrano nel precache della PWA.
- [ ] **Navigazione**: il catalogo si apre dalla sezione **Plan** della barra. Per ora è una schermata di
  consultazione; in futuro servirà solo per scegliere gli esercizi quando si crea una routine di allenamento.
- [ ] **Attribuzione** richiesta dalla licenza: link visibile **"Exercise data by RepDB (repdb.co)"** nell'app
  (schermata del catalogo o crediti) e nel `README.md` del repo, definito una sola volta nel codice.
- [ ] **Licenza** (`LICENSE.md` del pacchetto): uso solo dentro l'app; il dataset, anche modificato o tradotto,
  non va ripubblicato come dataset o API; le immagini non vanno usate come input per modelli generativi.
- [ ] Le API sono accessibili solo agli utenti autenticati.

## Fuori scope

- Esercizi personalizzati creati dagli utenti.
- Descrizione, istruzioni passo passo e consigli (presenti nel dataset solo in EN/DE/ES: richiedono traduzione;
  eventualmente in una feature futura).
- Animazioni degli esercizi (solo nel bundle a pagamento di RepDB).
- Uso del valore MET per stimare le calorie bruciate (si salva nel DB, lo useranno feature future).
- Schede, sessioni, serie e carichi (feature successive che useranno questo catalogo).
- Modifica degli esercizi dall'app.
- Figura con i muscoli evidenziati (MuscleMap-ts): feature ALL-002 (`features/allenamento-mappa-muscolare.md`).

## Modello dati (bozza)

- `exercises`: `id` (testo, id del dataset, es. `"arnold-press"`, PK), `name_it`, `name_en`, `category`,
  `body_part`, `equipment` (nullable), `difficulty`, `force_type`, `mechanic`, `met`, `is_unilateral`,
  `is_bodyweight`, `primary_muscles` e `secondary_muscles` (liste: JSON o tabella collegata, da decidere
  nell'issue), `images`. Indici per i filtri. Nessun `user_id` (dati comuni).

## API (bozza)

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/exercises?q=&body_part=&equipment=&limit=&offset=` | Elenco paginato con ricerca e filtri |
| GET | `/api/exercises/{id}` | Dettaglio di un esercizio |
| GET | `/api/exercises/filters` | Valori disponibili per parte del corpo e attrezzatura |

## UI

Schermata "Esercizi" mobile-first: campo di ricerca in alto, filtri (parte del corpo, attrezzatura), lista con
miniatura e nome, scroll con caricamento progressivo. Tocco su un esercizio → dettaglio con immagini, dati e
muscoli.

```
┌──────────────────────────────┐
│ Esercizi                     │
│ [ 🔍 cerca...              ] │
│ [Parte del corpo ▾][Attrezzi ▾]│
│ ┌────┐ panca piana bilanciere│
│ │img │ petto · bilanciere    │
│ └────┘                       │
│ ┌────┐ croci con manubri     │
│ │img │ petto · manubrio      │
│ └────┘                       │
│ Exercise data by RepDB       │
└──────────────────────────────┘
```

## Criteri di accettazione

- [ ] Al primo avvio del container il DB contiene 708 esercizi (versione `2026.11.1` del pacchetto), senza
  comandi manuali; riavviando il container il numero non cambia e il caricamento non viene rieseguito.
- [ ] Un esercizio presente nel DB ma assente dal dataset resta nel DB dopo il caricamento.
- [ ] Tutti gli esercizi hanno un nome italiano; nessun valore dei filtri compare in inglese o come codice
  (es. `upper_legs`).
- [ ] Cercando "panca" compaiono gli esercizi con "panca" nel nome; "PANCA" e varianti accentate danno lo stesso
  risultato.
- [ ] Filtrando per "petto" + "manubrio" compaiono solo esercizi con entrambe le caratteristiche.
- [ ] Il dettaglio di un esercizio dinamico mostra le due immagini (inizio e picco), quello di un esercizio
  statico l'unica immagine; in entrambi si vedono muscoli principali e secondari.
- [ ] Le immagini si caricano dall'app (nessuna richiesta a domini esterni).
- [ ] Il link "Exercise data by RepDB (repdb.co)" è visibile nell'app e nel `README.md`.
- [ ] Senza login le API rispondono 401.
- [ ] Nel repo `fitter` non ci sono né `exercises.json` né le immagini del dataset.
- [ ] La versione del pacchetto è fissata e la build Docker ARM64 funziona senza credenziali aggiuntive.

## Domande aperte

- **Router**: la prima schermata oltre la home richiede il router (D-010 lo prevede con la prima feature a più
  pagine). Scelta della libreria nell'issue frontend.

## Issue

Compilato da `/feature-to-issue`. Il piano tecnico e i passi stanno nelle issue, non qui.

| ID | Lato | Stato | File |
|----|------|-------|------|
|    |      |       |      |

## Note

- 2026-11-19: scelto di copiare il JSON ridotto nel progetto e caricarlo nel DB invece di usare la libreria
  `@nataliaguer/exercises-it` (repo privato, URL di installazione errato nel README, JSON completo da 2,1 MB).
- 2026-11-21: **sostituito il dataset** con `@repdb/exercises` (annulla la nota precedente). Motivi: le immagini
  stanno nel pacchetto (niente 140 MB di media da copiare a mano sul Pi, niente segnaposto per i media mancanti),
  licenza chiara per l'uso in app con un solo link di credito, dati più ricchi (difficoltà, MET, muscoli
  strutturati). Rinunce accettate: niente GIF animate (due immagini fisse per esercizio), 708 esercizi invece di
  1324, nomi da tradurre in italiano.
- 2026-11-21: chiuse le domande aperte. Catalogo aperto dalla sezione Plan (in futuro servirà solo per creare
  le routine); nomi italiani con traduzione automatica + revisione; immagini come asset statici del frontend;
  qualità delle immagini (generate con AI) controllata e approvata dall'utente. Dataset copiato dallo stage
  frontend nella build Docker e caricato nel DB in automatico all'avvio del container (scartati: comando
  manuale, che sul Pi richiederebbe un passo a mano; catalogo solo in memoria senza tabella, che lascerebbe
  routine e sessioni senza chiave esterna e con riferimenti vuoti se un esercizio sparisce dal dataset).

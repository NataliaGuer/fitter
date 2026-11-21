# ALL-002 — Mappa muscolare (MuscleMap-ts)

- **Area**: allenamento
- **Stato**: da definire
- **Priorità**: media
- **Dipende da**: ALL-001 (catalogo esercizi: dettaglio e muscoli del dataset)

## Obiettivo

Aggiungere al frontend la libreria [`MuscleMap-ts`](https://github.com/NataliaGuer/MuscleMap-ts) (MIT, figura
umana in SVG con i muscoli evidenziabili, componenti React) e usarla per mostrare, nel dettaglio di un esercizio,
quali muscoli lavora. È anche la base per usi futuri (heatmap dei muscoli allenati nelle statistiche).

## User story

- Come utente voglio vedere su una figura i muscoli allenati da un esercizio, distinguendo il muscolo principale
  dai secondari, per capire a colpo d'occhio cosa sto allenando.
- Come utente voglio poter girare la figura (fronte/retro) per vedere i muscoli della schiena.

## Requisiti

- [ ] **Installazione** di `musclemap-ts` nel frontend. Non è pubblicata su npm: il modo di installarla (dipendenza
  git fissata a un commit/tag, pubblicazione su npm o GitHub Packages, ecc.) si decide nell'issue. In ogni caso:
  - versione **fissata** (niente aggiornamenti involontari);
  - `npm ci` funziona in locale, in CI e nella build Docker multi-arch (ARM64) senza credenziali aggiuntive
    (il repo è pubblico);
  - `npm run lint` e `npm run build` restano verdi, con i tipi della libreria (TypeScript strict).
- [ ] **Componente dell'app** che incapsula `BodyView` (es. `MuscleMapFigure`): prende i muscoli principali e i
  secondari, usa i colori del tema neobrutalista (chiaro/scuro, D-015) e si adatta alla larghezza del telefono.
- [ ] **Corrispondenza muscoli**: tabella nel codice dai codici muscolo del dataset RepDB (`primary_muscles` e
  `secondary_muscles`, es. `hip_flexors`, `gluteus_maximus`) agli id di MuscleMap (22 muscoli base + 14
  sottogruppi). I muscoli senza corrispondenza si ignorano sulla figura senza errori.
- [ ] **Dettaglio esercizio** (ALL-001): figura con i muscoli principali evidenziati con un colore forte e i
  secondari con uno più tenue; legenda "principali / secondari".
- [ ] **Fronte/retro**: scelta della vista, con default sulla vista in cui si trova il primo muscolo principale.
- [ ] Figura in sola visualizzazione: niente selezione, zoom o tooltip in questa feature.
- [ ] Il bundle resta contenuto: la libreria si carica solo nelle schermate che la usano.

## Fuori scope

- Heatmap dei muscoli allenati nella settimana/mese (feature statistiche futura).
- Selezione dei muscoli sulla figura per filtrare il catalogo.
- Scelta della figura maschile/femminile dalle impostazioni utente (per ora una figura fissa, da decidere).
- Modifiche al backend.

## Modello dati (bozza)

Nessuno: la corrispondenza muscoli è una tabella statica nel frontend.

## API (bozza)

Nessuna: usa i dati di `GET /api/exercises/{id}` (ALL-001).

## UI

```
┌──────────────────────────────┐
│ ← panca piana bilanciere     │
│ [ inizio ]   [ picco ]       │
│ Exercise data by RepDB       │
│ ┌──────────────────────────┐ │
│ │   [Fronte] [Retro]       │ │
│ │        ( figura )        │ │
│ │  ■ principale ▫ secondari│ │
│ └──────────────────────────┘ │
│ Principali: pettorali        │
│ Secondari: deltoidi, tricipiti│
└──────────────────────────────┘
```

## Criteri di accettazione

- [ ] `npm ci && npm run lint && npm run build` passano in locale e in CI; l'immagine Docker ARM64 si costruisce.
- [ ] La versione installata di `musclemap-ts` è fissata (stessa versione a ogni installazione).
- [ ] Nel dettaglio di "panca piana" il petto è evidenziato come principale, deltoidi e tricipiti come secondari.
- [ ] Per un esercizio con muscolo principale sulla schiena la figura si apre sulla vista posteriore.
- [ ] Un esercizio con muscoli senza corrispondenza (es. cardio) mostra la figura senza errori.
- [ ] La figura è leggibile in tema chiaro e scuro e a 375 px di larghezza non causa scroll orizzontale.
- [ ] La libreria non è inclusa nel bundle della home.

## Domande aperte

- **Installazione**: dipendenza git fissata a un commit (`github:NataliaGuer/MuscleMap-ts#<sha>`, che però
  compila la libreria con TypeScript 7 a ogni `npm ci`), oppure pubblicazione del pacchetto (npm / GitHub
  Packages) con `dist/` già compilata? Da decidere nell'issue.
- **Figura**: maschile, femminile, o scelta dall'utente (servirebbe un'impostazione nel profilo)?
- **Corrispondenze dubbie**: i muscoli del dataset RepDB senza un equivalente diretto in MuscleMap vanno
  associati al muscolo più vicino o ignorati? L'elenco dei codici muscolo va ricavato dal dataset nell'issue.

## Issue

Compilato da `/feature-to-issue`. Il piano tecnico e i passi stanno nelle issue, non qui.

| ID | Lato | Stato | File |
|----|------|-------|------|
|    |      |       |      |

## Note

Nessuna.

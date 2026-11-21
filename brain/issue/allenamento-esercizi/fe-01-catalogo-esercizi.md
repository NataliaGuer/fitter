# ALL-001-FE-01 — Catalogo esercizi: router, schermata Esercizi e dettaglio

- **Feature**: ALL-001 (`features/allenamento-esercizi.md`)
- **Lato**: frontend
- **Stato**: bozza
- **Dipende da**: ALL-001-BE-01 (API del catalogo e fallback per le rotte del frontend)

## Obiettivo

Introdurre il router e rendere navigabile la sezione Plan, che per ora mostra il catalogo esercizi: ricerca,
filtri, lista a caricamento progressivo e dettaglio con immagini e muscoli, tutto in italiano. Le immagini del
pacchetto `@repdb/exercises` diventano asset statici del frontend.

## Requisiti coperti

Da ALL-001:
- [ ] Etichette italiane di parte del corpo, attrezzatura, difficoltà e muscoli (mappa nel frontend).
- [ ] Ricerca, filtri combinabili, risultati paginati (lato interfaccia).
- [ ] Dettaglio esercizio con una o due immagini.
- [ ] Immagini come asset statici del frontend, caricate a richiesta, fuori dal precache della PWA, nessun CDN.
- [ ] Navigazione: catalogo aperto dalla sezione Plan.
- [ ] Link "Exercise data by RepDB (repdb.co)" visibile nell'app, definito una sola volta nel codice.
- [ ] Nel repo nessuna immagine del dataset.

## Fuori scope

- Figura dei muscoli (ALL-002): nel dettaglio i muscoli sono solo testo.
- Navigazione reale di Start, Stats e Calories (restano inerti).
- Selezione degli esercizi per una routine (feature futura): qui il catalogo è di sola consultazione.
- Immagini disponibili offline.

## Piano tecnico

Si applicano D-007, D-010, D-013, D-014, D-015: HeroUI v3 + Tailwind 4, wrapper `apiFetch`, messaggi d'errore
dallo status code, icone `@gravity-ui/icons`, stile dal tema. I componenti HeroUI e le API delle librerie
indicate vanno verificati sulla documentazione della versione installata al momento del passo.

- **Contesto**: `App.tsx` oggi sceglie tra login e `HomePage` senza router (D-010 rimandava il router alla
  prima feature a più pagine: è questa). `BottomNav` ha voci inerti. Le immagini stanno in
  `node_modules/@repdb/exercises/images/flat/` (dipendenza già aggiunta da ALL-001-BE-01) e vanno rese
  raggiungibili dal browser senza entrare nel repo.

- **Decisione 1 — Router**:
  - A — `react-router@8.5.2` in modalità dichiarativa (`BrowserRouter`, `Routes`): standard di fatto, rotte
    annidate con layout condiviso (serve subito, vedi Decisione 3). Peer `react >= 19.2.7`, soddisfatto.
    Contro: più pesante dell'alternativa.
  - B — `wouter@3.13.0`: molto piccolo / contro: rotte annidate e layout meno comodi, meno diffuso.
  - C — nessun router, schermata corrente in uno stato React: zero dipendenze / contro: il tasto "indietro"
    del telefono chiuderebbe l'app invece di tornare alla lista.
  - **Proposta**: A. Rotte: `/` home, `/plan` catalogo, `/plan/exercises/:id` dettaglio; ogni altro indirizzo
    riporta a `/`. L'`AuthProvider` continua a decidere tra login e app: le rotte esistono solo da autenticati.

- **Decisione 2 — Layout e barra**: nuova rotta-layout `AppLayout` con `BottomNav` e la pagina corrente.
  `BottomNav` ricava la voce attiva dall'indirizzo; Home e Plan navigano, le altre restano inerti. `HomePage`
  prende l'utente da `useAuth` invece che da una prop.

- **Decisione 3 — Dettaglio sopra la lista**: `/plan/exercises/:id` è una rotta figlia di `/plan`: la lista
  resta montata e il dettaglio si apre a tutto schermo sopra di essa (componente `Modal` di HeroUI); il tasto
  "indietro" lo chiude.
  - Scartata la pagina separata: tornando indietro la lista ripartirebbe dall'inizio, perdendo scorrimento e
    risultati già caricati (scomodo in palestra).
  - Ricerca e filtri stanno nei parametri dell'indirizzo (`/plan?q=panca&body_part=chest`), così sopravvivono a
    un ricaricamento della pagina.

- **Decisione 4 — Immagini come asset statici**:
  - A — `vite-plugin-static-copy@4.1.1` (devDependency, compatibile con Vite 8): in sviluppo serve i file da
    `node_modules`, in build li copia in `dist/exercise-images/`. Nulla viene scritto nella cartella dei
    sorgenti.
  - B — script `predev`/`prebuild` che copia le immagini in `public/exercise-images/` (in `.gitignore`):
    nessuna dipendenza / contro: 23 MB di immagini dentro l'albero del repo, protetti solo dal `.gitignore`.
  - C — plugin Vite scritto a mano in `vite.config.ts`: nessuna dipendenza / contro: codice nostro da mantenere.
  - **Proposta**: A. Indirizzo: `/exercise-images/<file>` (il backend restituisce solo il nome del file).
    `globPatterns` di Workbox non include `webp`: le immagini restano fuori dal precache, come richiesto.
    Immagine mancante (esercizio non più nel dataset): segnaposto al posto dell'immagine.

- **Decisione 5 — Etichette italiane**: file `src/exercises/labels.it.json` con quattro mappe codice → etichetta
  (`body_part` 9, `equipment` 64 + `none`, `difficulty` 3, `muscles` 32). Se un codice manca si mostra il codice
  reso leggibile (`upper_legs` → "upper legs").
  - Script `scripts/check-labels.mjs` (`npm run check:labels`): confronta i codici di
    `@repdb/exercises/exercises.json` con le mappe ed esce con errore se ne manca uno. Aggiunto al job
    `frontend` della CI: un aggiornamento del pacchetto con codici nuovi rompe la CI invece di mostrare codici
    in inglese.
  - JSON e non TypeScript perché lo script Node lo legga senza compilare.

- **Decisione 6 — Caricamento dei dati**: `apiFetch` (D-010) con un parametro `signal` in più, per annullare
  le richieste superate mentre si digita. Ricerca con attesa di 300 ms dopo l'ultimo tasto. Pagine da 30
  esercizi, caricate quando si arriva in fondo alla lista (`IntersectionObserver`), senza librerie.
  - Stati: caricamento (scheletri), nessun risultato ("Nessun esercizio trovato"), errore con "Riprova"
    (messaggi da `errorMessage`, D-013).

- **Contratto**: API di ALL-001-BE-01 — `GET /api/exercises` (`q`, `body_part`, `equipment`, `limit`,
  `offset` → `{ items, total, limit, offset }`), `GET /api/exercises/filters`
  (`{ body_parts, equipment }`, con `"none"` per "nessuna attrezzatura"), `GET /api/exercises/{id}`
  (dettaglio; `404` se inesistente). I tipi TypeScript in `src/api/exercises.ts` ricalcano quelle risposte.

- **Struttura dei moduli**:
  - `src/App.tsx` — rotte; `src/components/AppLayout.tsx`; `src/components/BottomNav.tsx` (navigazione).
  - `src/api/exercises.ts` — tipi e chiamate; `src/api/client.ts` — `signal`.
  - `src/exercises/labels.it.json`, `src/exercises/labels.ts` (funzioni `bodyPartLabel`, ecc.),
    `src/exercises/images.ts` (indirizzo dell'immagine), `src/exercises/attribution.ts` (testo e link RepDB).
  - `src/pages/ExercisesPage.tsx` (ricerca, filtri, lista), `src/pages/ExerciseDetail.tsx`;
    componenti in `src/components/exercises/` (riga della lista, immagine con segnaposto, attribuzione).

- **Impatto**:
  - Nuove dipendenze: `react-router@8.5.2`, `vite-plugin-static-copy@4.1.1` (dev). Solo JS, nessun problema
    ARM64.
  - File modificati: `frontend/package.json` + lock, `vite.config.ts`, `src/main.tsx`, `src/App.tsx`,
    `src/pages/HomePage.tsx`, `src/components/BottomNav.tsx`, `src/api/client.ts`, `.github/workflows/ci.yml`
    (una riga: `npm run check:labels`).
  - Nessuna modifica a `backend/`.
  - Rischi:
    - `dist/` e l'immagine Docker crescono di circa 23 MB;
    - 65 voci di attrezzatura in un menu su telefono: serve un controllo con ricerca o scorrimento comodo
      (scelta del componente HeroUI al passo 3);
    - il peso del bundle JS con il router si annota prima/dopo.
- **Decisioni registrate**: (compilato all'approvazione)

## Passi

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.
Verifiche manuali in dev (`./script/start-dev.sh`, `http://localhost:5173`), vista mobile = DevTools a 375 px.

### Passo 1 — Router e navigazione Home/Plan

- **Stato**: da fare
- **Obiettivo**: Home e Plan sono due indirizzi raggiungibili dalla barra; Plan mostra una pagina segnaposto.
- **Lavoro**:
  - installazione di `react-router`; rotte in `App.tsx`, `AppLayout`, `BottomNav` con navigazione e voce
    attiva dall'indirizzo; `HomePage` senza prop `user`; `ExercisesPage` segnaposto con titolo "Esercizi".
- **Definition of done**:
  - [ ] Toccando Plan l'indirizzo diventa `/plan`, si vede "Esercizi" e la voce Plan è evidenziata
        (`aria-current="page"`); toccando Home si torna a `/` con la home di prima.
  - [ ] Il tasto "indietro" del browser da `/plan` riporta alla home.
  - [ ] Ricaricando la pagina su `/plan` si resta su `/plan`; un indirizzo inesistente (`/xyz`) porta alla home.
  - [ ] Start, Stats e Calories non fanno nulla e non danno errori in console.
  - [ ] Da non autenticati, aprendo `/plan` si vede il login; dopo l'accesso si vede la pagina Esercizi.
  - [ ] Logout e cambio tema funzionano come prima.
  - [ ] `npm run lint` e `npm run build` senza errori; dimensione del bundle JS annotata (prima/dopo).

### Passo 2 — Immagini statiche ed etichette italiane

- **Stato**: da fare
- **Obiettivo**: le immagini del pacchetto sono servite dall'app e ogni codice del dataset ha un'etichetta
  italiana.
- **Lavoro**:
  - `vite-plugin-static-copy` in `vite.config.ts`; `src/exercises/images.ts`.
  - `labels.it.json`, `labels.ts`, `scripts/check-labels.mjs`, script `check:labels`, riga in `ci.yml`.
- **Definition of done**:
  - [ ] In dev `http://localhost:5173/exercise-images/arnold-press-peak.webp` mostra l'immagine.
  - [ ] Dopo `npm run build`, `dist/exercise-images/` contiene lo stesso numero di file `.webp` di
        `node_modules/@repdb/exercises/images/flat/`.
  - [ ] Dopo la build, `dist/sw.js` non contiene `exercise-images` (immagini fuori dal precache).
  - [ ] `npm run check:labels` termina con successo; togliendo una voce da `labels.it.json` termina con errore
        indicando il codice mancante.
  - [ ] `git status` non mostra immagini né cartelle di immagini da aggiungere.
  - [ ] `npm run lint` e `npm run build` senza errori.

### Passo 3 — Schermata Esercizi: ricerca, filtri e lista

- **Stato**: da fare
- **Obiettivo**: da Plan si cerca e si filtra il catalogo, con caricamento progressivo.
- **Lavoro**:
  - `src/api/exercises.ts`, `signal` in `apiFetch`; `ExercisesPage` con campo di ricerca, due filtri, lista
    (miniatura, nome, "parte del corpo · attrezzatura"), stati di caricamento/vuoto/errore, attribuzione RepDB
    in fondo; parametri nell'indirizzo.
- **Definition of done**:
  - [ ] Aprendo Plan si vedono i primi 30 esercizi in ordine alfabetico con miniatura e nome italiano;
        scorrendo in fondo se ne caricano altri, fino al totale.
  - [ ] Scrivendo "panca" la lista mostra solo esercizi con "panca" nel nome; "PANCA" dà lo stesso risultato;
        nella scheda Rete di DevTools parte una sola richiesta dopo aver finito di digitare.
  - [ ] Scegliendo "petto" e "manubrio" la lista contiene solo esercizi con entrambe le caratteristiche;
        "nessuna attrezzatura" mostra solo esercizi a corpo libero; i filtri si possono azzerare.
  - [ ] Nei due filtri e nella lista non compare nessun codice o termine inglese (es. `upper_legs`).
  - [ ] Una ricerca senza risultati mostra "Nessun esercizio trovato"; con il backend fermo compare l'errore con
        "Riprova", che funziona quando il backend riparte.
  - [ ] Ricaricando la pagina con ricerca e filtri attivi, questi restano impostati.
  - [ ] Il link "Exercise data by RepDB (repdb.co)" è visibile e apre `https://repdb.co`.
  - [ ] Nella scheda Rete non ci sono richieste a domini esterni.
  - [ ] In vista mobile: nessuno scroll orizzontale, l'ultimo esercizio è interamente visibile sopra la barra;
        tema chiaro e scuro.
  - [ ] `npm run lint` e `npm run build` senza errori; nessun `any` in `src/`.

### Passo 4 — Dettaglio esercizio

- **Stato**: da fare
- **Obiettivo**: toccando un esercizio si apre il dettaglio sopra la lista.
- **Lavoro**:
  - rotta figlia `/plan/exercises/:id`, `ExerciseDetail` con nome, immagini (inizio e picco, oppure quella
    unica), parte del corpo, attrezzatura, difficoltà, muscoli principali e secondari, attribuzione; stato di
    caricamento, esercizio inesistente, errore.
- **Definition of done**:
  - [ ] Toccando "Arnold press" si apre il dettaglio con due immagini (inizio e picco), spalle, manubrio,
        difficoltà e muscoli principali e secondari in italiano.
  - [ ] Un esercizio statico (es. `90-90-hold`) mostra una sola immagine.
  - [ ] Il tasto "indietro" (del browser e nell'interfaccia) chiude il dettaglio e la lista è nella stessa
        posizione di scorrimento, con ricerca e filtri invariati.
  - [ ] Aprendo direttamente `/plan/exercises/arnold-press` si vede il dettaglio; con un `id` inesistente
        compare "Esercizio non trovato" senza errori in console.
  - [ ] Se l'immagine non si carica (verifica bloccando la richiesta in DevTools) compare un segnaposto.
  - [ ] L'attribuzione RepDB è visibile anche nel dettaglio.
  - [ ] In vista mobile il dettaglio è leggibile a 375 px senza scroll orizzontale, in tema chiaro e scuro.
  - [ ] Con l'immagine prod locale (`docker build --target prod -t fitter-prova .`, avviata su una porta
        libera con un `/data` temporaneo): ricaricando `/plan` si resta sul catalogo e miniature e immagini
        del dettaglio si vedono.
  - [ ] `npm run lint`, `npm run check:labels` e `npm run build` senza errori; nessun `any` in `src/`.

## Note di implementazione

Scostamenti dal piano, problemi incontrati, esito delle verifiche di ogni passo.

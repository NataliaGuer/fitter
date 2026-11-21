# CORE-004-FE-01 — Home a card con calendario settimanale e barra di navigazione

- **Feature**: CORE-004 (`features/core-home.md`)
- **Lato**: frontend
- **Stato**: fatta (2026-11-17; approvata 2026-11-17, passo 3 aggiunto e approvato il 2026-11-17)
- **Dipende da**: CORE-002-FE-01 (fatta)

## Obiettivo

Sostituire la home segnaposto con una dashboard a card: calendario della settimana corrente (completo), card
Calorie e Statistiche segnaposto, e una barra di navigazione in basso con 5 voci (Start in evidenza) che per ora
non navigano. Nessuna modifica a `backend/`.

## Requisiti coperti

Tutti i requisiti e i criteri di accettazione di CORE-004.

## Fuori scope

- Router e navigazione reale (D-010).
- Animazione di transizione tra le settimane durante lo swipe.
- Dati delle routine nel calendario, contenuto delle card Calorie/Statistiche.

## Piano tecnico

Si applicano D-007, D-010, D-013: HeroUI v3 + Tailwind 4, niente router, nessun CSS custom se evitabile.

- **Contesto**: `HomePage.tsx` oggi è una `Card` centrata con saluto e "Esci". Servono: icone (nessuna libreria di
  icone installata), calcolo della settimana corrente, un layout con barra fissa in basso. HeroUI v3 non ha un
  componente "bottom navigation" né una "week strip": vanno composti con `Button`/`Card` e Tailwind.

- **Decisione 1 — Icone**:
  - A — `@gravity-ui/icons@2.23.1`: è il set usato negli esempi della documentazione HeroUI v3; componenti React
    singoli (tree-shaking), solo JS, peer `react: *`. Pro: coerenza visiva con HeroUI / contro: una dipendenza in più.
  - B — `lucide-react@1.74.0`: set molto ampio e diffuso. Pro: più icone / contro: stile meno allineato a HeroUI.
  - C — SVG inline scritti a mano. Pro: zero dipendenze / contro: icone da disegnare e mantenere, servirà presto
    in tutta l'app.
  - **Proposta**: A. Icone previste: `House` (Home), `ListCheck` (Plan), `Play` (Start), `ChartColumn` (Stats),
    `Flame` o simile (Calories), `ArrowRightFromSquare` (logout). Nomi esatti verificati all'installazione.
- **Decisione 2 — Calcolo della settimana**: `@internationalized/date` (già installato come peer di HeroUI):
  `today(getLocalTimeZone())`, `startOfWeek(oggi, 'it-IT')` (lunedì) e `add({ days: i })` per i 7 giorni; nomi
  di giorno e mese con `Intl.DateTimeFormat('it-IT')`. Scartati: `Date` nativo a mano (errori sui fusi/ora legale),
  librerie tipo `date-fns` (dipendenza inutile). Il calendario non si aggiorna da solo a mezzanotte: si ricalcola
  a ogni apertura/render dell'app (accettabile per ora).
- **Decisione 3 — Layout e barra** (aggiornata il 2026-11-17, vedi note del passo 1): `HomePage` diventa una pagina a colonna (`max-w-md mx-auto`, padding) con
  header (saluto + pulsante icona "Esci") e card impilate; la barra è un `<nav>` floating (`fixed`, staccato dai bordi,
  `rounded-full`, ombra) con 5 `Button` `variant="ghost"` `isIconOnly` (solo icona, nome in `aria-label`),
  distanziato dal fondo anche di `env(safe-area-inset-bottom)` per gli iPhone. Il contenuto ha un padding
  inferiore maggiore dell'altezza della barra. Start: `Button isIconOnly` rotondo (`rounded-full`, 56 px),
  `variant="primary"`, con ombra, centrato nella colonna centrale di una griglia a 5 colonne uguali. Voce attiva (Home) con colore `accent`/primario;
  `aria-current="page"` sulla voce attiva. Le voci hanno `onPress` vuoto.
  Scartato: `Tabs` HeroUI come barra (semantica di pannelli, poco adatto a un pulsante centrale diverso).
- **Struttura dei moduli**:
  - `src/components/BottomNav.tsx` — barra con le 5 voci (prop `active`).
  - `src/components/home/WeekCalendarCard.tsx` — card calendario; logica dei giorni in
    `src/components/home/week.ts` (`currentWeek(): CalendarDate[]`), separata per poterla riusare con le routine.
  - `src/components/home/PlaceholderCard.tsx` — card con titolo, icona e "In arrivo".
  - `src/pages/HomePage.tsx` — riscritta: header, card, `BottomNav`.
- **Contratto**: nessuna API nuova; usa solo `logout` già esistente.
- **Impatto**:
  - Nuova dipendenza: `@gravity-ui/icons@2.23.1` (solo JS, nessun problema ARM64).
  - File nuovi come sopra; modificato `src/pages/HomePage.tsx`; `index.html`: `viewport-fit=cover` nel meta
    viewport (necessario per `safe-area-inset`).
  - Nessuna modifica al DB o al backend.
  - Rischi: peso del bundle (si annota prima/dopo); `CenteredScreen` resta per login/offline.
- **Decisioni registrate**: D-014 (icone, calcolo della settimana, barra di navigazione).

## Passi

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.
Verifiche manuali in dev (`./script/start-dev.sh`, `http://localhost:5173`), vista mobile = DevTools a 375 px.

### Passo 1 — Layout della home e barra di navigazione

- **Stato**: fatto (2026-11-17)
- **Obiettivo**: la home ha header con saluto e logout, tre card segnaposto e la barra in basso con Start in
  evidenza.
- **Lavoro**:
  - installazione di `@gravity-ui/icons`; `viewport-fit=cover` in `index.html`.
  - `BottomNav.tsx`, `PlaceholderCard.tsx`; `HomePage.tsx` riscritta (anche il calendario per ora è un
    `PlaceholderCard`).
- **Definition of done**:
  - [x] Da autenticati si vedono header "Ciao, <nickname>" con pulsante di logout, tre card (Questa settimana,
        Calorie, Statistiche) e la barra floating con le icone di Home, Plan, Start, Stats, Calories, senza
        etichette (ogni pulsante ha `aria-label`).
  - [x] Start è un pulsante rotondo più grande, colore primario, centrato orizzontalmente nella barra; Home è
        evidenziata come attiva.
  - [x] Toccando le voci non succede nulla (nessun errore in console).
  - [x] Il logout porta alla schermata di accesso; con backend fermo mostra l'errore e si resta nella home.
  - [x] In vista mobile: nessuno scroll orizzontale, la barra resta in basso staccata dai bordi e scorrendo l'ultima card è
        interamente visibile sopra la barra; funziona in tema chiaro e scuro.
  - [x] `npm run lint` e `npm run build` senza errori; dimensione del bundle annotata.

### Passo 2 — Card calendario settimanale

- **Stato**: fatto (2026-11-17)
- **Obiettivo**: la prima card mostra la settimana corrente con oggi evidenziato.
- **Lavoro**:
  - `week.ts` (`currentWeek`), `WeekCalendarCard.tsx`; in `HomePage` al posto del segnaposto.
  - griglia a 7 colonne: giorno abbreviato (`lun`, `mar`, …) e numero; oggi in cerchio con colore primario;
    titolo centrato (mese e anno tolti su richiesta, vedi note); ogni giorno è un elemento con spazio previsto per un futuro indicatore di routine.
- **Definition of done**:
  - [x] La card mostra 7 giorni da lunedì a domenica della settimana corrente, con numeri corretti (oggi
        2026-11-17 → lun 16 … dom 22) e oggi evidenziato.
  - [x] Cambiando la data del sistema (o il fuso in DevTools → Sensors) a una domenica e a un lunedì, la settimana
        mostrata è quella giusta.
  - [x] Il titolo "Questa settimana" è centrato; card e barra hanno angoli da 12 px.
  - [x] Il giorno di oggi ha `aria-current="date"`.
  - [x] In vista mobile i 7 giorni stanno su una riga senza scroll orizzontale.
  - [x] `npm run lint` e `npm run build` senza errori; nessun `any` in `src/`.

### Passo 3 — Scorrimento delle settimane

- **Stato**: fatto (2026-11-17; aggiunto su richiesta dell'utente e approvato il 2026-11-17)
- **Obiettivo**: nella card del calendario si passa alla settimana precedente/successiva con swipe o frecce.
- **Piano**:
  - *Stato*: `weekOffset: number` (settimane rispetto a quella corrente, 0 = corrente) in `WeekCalendarCard`; giorni
    = `weekOf(today.add({ weeks: weekOffset }))`. Nessun limite avanti/indietro. Oggi resta evidenziato solo se è
    nella settimana mostrata. All'apertura dell'app si riparte sempre dalla settimana corrente (stato non salvato).
  - *Frecce*: due `Button` HeroUI `isIconOnly` `ghost` con `ChevronLeft`/`ChevronRight` di `@gravity-ui/icons`
    ai lati del titolo (`aria-label` "Settimana precedente"/"Settimana successiva").
  - *Swipe*: `onTouchStart`/`onTouchEnd` di React sulla riga dei giorni: si cambia settimana se lo spostamento
    orizzontale supera 50 px ed è maggiore di quello verticale (lo scroll verticale della pagina resta libero).
    Swipe verso sinistra = settimana successiva. Nessuna libreria di gesture.
    Scartati: scroll orizzontale con CSS `scroll-snap` (va gestito il riposizionamento infinito delle settimane,
    più complesso); librerie di gesture (dipendenza per un solo gesto).
  - *Titolo*: "Questa settimana" con `weekOffset = 0`, altrimenti l'intervallo con `Intl.DateTimeFormat('it-IT')`:
    "9 – 15 nov", "30 nov – 6 dic"; **mai l'anno** (decisione dell'utente, 2026-11-17), anche a cavallo di due
    anni ("28 dic – 3 gen"). Funzione `weekLabel(days)` in `week.ts`.
  - Nessuna nuova dipendenza; file toccati: `week.ts`, `WeekCalendarCard.tsx`.
- **Definition of done**:
  - [x] Le frecce mostrano la settimana precedente/successiva; dalla corrente, "‹" porta a lun 9 … dom 15 con
        titolo "9 – 15 nov" e nessun giorno evidenziato; tornando indietro con "›" il titolo è di nuovo
        "Questa settimana" con oggi evidenziato.
  - [x] Da telefono (o DevTools con emulazione touch) lo swipe a sinistra/destra sui giorni cambia settimana;
        uno scroll verticale della pagina che parte dalla card non cambia settimana.
  - [x] Il titolo è corretto anche a cavallo di due mesi ("30 nov – 6 dic") e di due anni
        ("28 dic – 3 gen", senza anno), verificato con uno script su date fisse.
  - [x] Il titolo resta centrato e in vista mobile frecce, titolo e 7 giorni stanno senza scroll orizzontale.
  - [x] `npm run lint` e `npm run build` senza errori; nessun `any` in `src/`.

## Note di implementazione

### Passo 1 (2026-11-17)
- Dipendenza installata: `@gravity-ui/icons@2.23.1`. Icone: `House`, `ListCheck`, `PlayFill` (Start), `ChartColumn`,
  `Flame`, `Calendar`, `ArrowRightFromSquare` (logout).
- File creati: `src/components/BottomNav.tsx`, `src/components/home/PlaceholderCard.tsx`. Modificati:
  `src/pages/HomePage.tsx` (riscritta), `index.html` (`viewport-fit=cover`).
- Barra: `<nav>` fisso con `bg-surface` e bordo `border-separator`, griglia a 5 colonne; voci `Button` `ghost`
  con icona sopra l'etichetta, attiva in `text-accent` con `aria-current="page"`. Start: `Button` `primary`
  `isIconOnly` rotondo da 64 px, sollevato (`-mt-6`), con ombra e anello del colore di sfondo che lo stacca dalla
  barra; etichetta "Start" sotto in grassetto.
- Logout: pulsante icona in alto a destra (`aria-label="Esci"`), stesso comportamento di prima in caso di errore.
- Bundle: JS `423.33 kB` (gzip `131.31 kB`, +7 kB rispetto a CORE-002-FE-01), CSS `470.99 kB` (gzip `43.47 kB`),
  precache `874.81 KiB`.
- `npm audit` segnala 15 vulnerabilità in dipendenze già presenti (catena di `vite` / `vite-plugin-pwa`,
  `serialize-javascript`), non introdotte da questo passo: fuori scope, da valutare a parte.
- Esito verifiche locali: lint e build senza errori; container dev del frontend ricostruito (`up -d --build -V
  frontend`). Le verifiche nel browser della DoD sono da fare a mano.
- **Modifiche richieste in verifica (2026-11-17)**: barra **floating** (`fixed` a `1rem` dal fondo + safe area,
  `inset-x-4`, `rounded-full`, bordo e ombra); **solo icone** (`isIconOnly` con `aria-label`); Start **centrato**:
  griglia a 5 colonne uguali con `place-items-center` (prima la colonna di Start conteneva anche l'etichetta e il
  pulsante risultava spostato), pulsante da 56 px dentro la barra, non più sollevato. Bundle JS `423.13 kB`
  (gzip `131.24 kB`). Lint e build senza errori.
- **Icone più grandi (2026-11-17, su richiesta)**: voci `size="lg"` con icone da 28 px; Start da 64 px con icona da
  32 px. La barra (circa 82 px + 16 px dal fondo) resta sotto il padding inferiore della pagina (112 px). Lint e build
  senza errori.
- **Icone davvero più grandi (2026-11-17)**: HeroUI forza la dimensione di ogni `svg` dentro un `Button`
  (`size-5`, `sm:size-4` in `button.css`), quindi `width`/`height` sulle icone erano ignorati. Ora le icone usano
  `size-7!` (28 px) e Start `size-8!` (32 px), con `!important` di Tailwind 4; voci da 48 px (`size-12`), Start da
  64 px. Regola da seguire per ogni icona dentro un `Button` che non debba avere la dimensione standard. Lint e build
  senza errori.
- **Barra più bassa, Start che sporge (2026-11-17, su richiesta)**: annullato l'ingrandimento delle icone (tornano
  alla dimensione standard di HeroUI). Barra alta 48 px (`h-12`, senza padding verticale); Start resta da 64 px e
  sporge di 8 px sopra e sotto la barra (`grid-rows-1`: riga da 48 px, pulsante centrato verticalmente). Lint e
  build senza errori.

### Passo 2 (2026-11-17)
- File creati: `src/components/home/week.ts`, `src/components/home/WeekCalendarCard.tsx`. Modificato:
  `src/pages/HomePage.tsx` (la card calendario sostituisce il segnaposto).
- `week.ts`: `weekOf(data)` (lunedì → domenica, `startOfWeek(..., 'it-IT', 'mon')` con lunedì esplicito, così non
  dipende dai dati di locale del browser), `currentWeek()` su `today(getLocalTimeZone())`, `weekdayName`,
  `monthName`, `weekTitle`. I nomi si formattano con `Intl.DateTimeFormat('it-IT')` su mezzanotte UTC, così il
  giorno non slitta col fuso. `weekOf` riceve la data di riferimento per poterla provare e riusare con le routine.
- Card: intestazione "Questa settimana" con mese e anno (iniziali maiuscole), griglia a 7 colonne (`<ol>`) con
  giorno abbreviato e numero; oggi in cerchio `bg-accent` con `aria-current="date"`; sotto ogni giorno uno spazio
  vuoto riservato al futuro indicatore della routine.
- Verifica della logica con uno script Node su date fisse: 2026-11-17, 2026-11-16 (lunedì) e 2026-11-22
  (domenica) → lun 16 … dom 22, "novembre 2026"; 2026-12-01 → lun 30 … dom 6, "novembre – dicembre 2026";
  2026-12-31 → lun 28 … dom 3, "dicembre 2026 – gennaio 2027"; 2026-03-29 (cambio dell'ora legale) → lun 23 …
  dom 29.
- Bundle: JS `438.92 kB` (gzip `136.51 kB`, +5 kB compressi: `@internationalized/date` ora entra nel bundle).
- Esito verifiche locali: lint e build senza errori; nessun `any` in `src/`. Le verifiche nel browser della DoD
  sono da fare a mano.

### Passo 3 (2026-11-17)
- Modificati: `src/components/home/week.ts` (`weekLabel`), `src/components/home/WeekCalendarCard.tsx`.
- Header della card: freccia ‹, titolo centrato (`aria-live="polite"`, così lo screen reader annuncia la nuova
  settimana), freccia ›; frecce `Button` `ghost` `size="sm"` con `ChevronLeft`/`ChevronRight`.
- Swipe su `<ol>` dei giorni: soglia 50 px e spostamento orizzontale maggiore di quello verticale.
- Verifica di `weekLabel` con uno script Node (riferimento 2026-11-17): -1 → "9 – 15 nov", 0 → "16 – 22 nov"
  (in UI "Questa settimana"), +2 → "30 nov – 6 dic", +6 → "28 dic – 3 gen", -46 → "29 dic – 4 gen", +49 →
  "25 – 31 ott". Nessun anno.
- Bundle: JS `439.44 kB` (gzip `136.65 kB`).
- Esito verifiche locali: lint e build senza errori; nessun `any` in `src/`. Le verifiche nel browser e da
  telefono della DoD sono da fare a mano.

# CORE-005-FE-01 — Tema neobrutalista per HeroUI e restyling delle schermate

- **Feature**: CORE-005 (`features/core-design-neobrutalista.md`)
- **Lato**: frontend
- **Stato**: fatta (2026-11-17; approvata 2026-11-17)
- **Dipende da**: CORE-002-FE-01, CORE-004-FE-01 (fatte)

## Obiettivo

Applicare lo stile neobrutalista di `brain/DESIGN.md` a tutta l'app: un tema HeroUI personalizzato (colori, bordi,
raggi, ombre) in versione chiara (Coral & Cream) e scura (Dark Brut) con scelta dell'utente, il font DM Sans incluso
nell'app e la rifinitura delle schermate esistenti.
Nessuna modifica a `backend/`.

## Requisiti coperti

Tutti i requisiti e i criteri di accettazione di CORE-005.

## Fuori scope

- Salvataggio del tema sul profilo (backend); pagina impostazioni; nuove schermate; icone della PWA.

## Piano tecnico

Si applicano D-007, D-010 (il tema segue il sistema solo finché l'utente non sceglie), D-013, D-014.

- **Contesto**: oggi l'app usa il tema predefinito di HeroUI v3 (grigi, blu, bordi a 1 px quasi invisibili, ombre
  sfumate, raggi fino a 32 px) e segue il tema del sistema con lo script inline in `index.html`. HeroUI v3 si
  personalizza ridefinendo le sue variabili CSS (`--background`, `--surface`, `--accent`, `--border`,
  `--border-width`, `--radius`, `--surface-shadow`, `--field-border`, …), quindi la maggior parte dello stile
  arriva a tutti i componenti senza toccarli uno per uno.

- **Decisione 1 — Come applicare lo stile**:
  - A — **Tema HeroUI tramite variabili CSS** in un file `src/theme.css` + pochi token Tailwind (`@theme`) e
    utility (`@utility`) per ciò che HeroUI non copre (ombra piena, effetto pressione). Pro: un solo punto di
    verità, i componenti HeroUI restano quelli; le nuove schermate ereditano lo stile / contro: un file CSS nostro
    (piccolo) da mantenere quando si aggiorna HeroUI.
  - B — Classi Tailwind sui singoli componenti (`border-2 shadow-[4px_4px_0_#111] …` ovunque). Pro: niente CSS
    nostro / contro: ripetizioni, facile dimenticare un componente, gli interni di HeroUI (campi, tab) non si
    raggiungono.
  - C — Libreria di componenti neobrutalista (es. neobrutalism.com). Contro: è su shadcn/Radix, contraria a D-007.
  - **Proposta**: A. È il "tema HeroUI" previsto da D-007; il CSS custom resta confinato a `theme.css`.
- **Decisione 2 — Font**:
  - A — `@fontsource-variable/dm-sans@5.3.0` (licenza OFL-1.1): font variabile servito dall'app stessa e messo
    nella cache della PWA. Pro: funziona offline e senza richieste a Google, un solo file per tutti i pesi /
    contro: ~40–50 kB in più (scaricati una volta).
  - B — Google Fonts via `<link>`. Contro: non funziona offline, richiesta esterna a ogni nuovo dispositivo.
  - **Proposta**: A. In `vite.config.ts` si aggiunge `woff2` ai `workbox.globPatterns` per metterlo in precache.
- **Decisione 3 — Cambio di tema** (richiesta dell'utente, 2026-11-17):
  - *Dove si salva la scelta*:
    - A — `localStorage` del dispositivo (chiave `fitter-theme`: `light` | `dark`; assente = segue il sistema).
      Pro: nessuna modifica al backend, il tema è applicato prima del primo render anche offline e prima del
      login / contro: la scelta non passa da un dispositivo all'altro.
    - B — preferenza sul profilo utente nel DB. Contro: richiede un'issue backend (colonna, migrazione, endpoint) e
      il tema si conosce solo dopo `/api/auth/me` (lampo del tema sbagliato all'avvio).
    - **Proposta**: A; B si potrà aggiungere in futuro sopra A.
  - *Come si applica*: lo script inline di `index.html` resta e si estende: legge `fitter-theme`, altrimenti usa
    `prefers-color-scheme`; imposta su `<html>` classe `light`/`dark`, `data-theme`, `color-scheme` e il
    `<meta name="theme-color">` (crema `#FAFADF` / `#111111`); segue i cambi del sistema solo se non c'è una scelta.
    `localStorage` letto e scritto dentro `try/catch` (in navigazione privata può non essere disponibile: si segue
    il sistema).
  - *Lato React*: `src/theme/useTheme.ts` con `theme` (`light` | `dark`) e `toggleTheme()`, che scrive
    `localStorage` e aggiorna `<html>` con `applyTheme` di `src/theme/theme.ts`. Le poche righe che applicano il
    tema sono duplicate nello script inline, che deve girare prima del bundle per evitare il lampo del tema
    sbagliato. Nessun context: lo stato vive in `<html>` e il pulsante è uno solo.
  - *Controllo*: uno **switch** (`Switch` di HeroUI, richiesta dell'utente del 2026-11-17 al posto del pulsante
    icona) nell'header della home accanto al logout, con icone `Sun`/`Moon` (`@gravity-ui/icons`); acceso = tema
    scuro; etichetta accessibile "Tema scuro".
  - Manifest: `theme_color`/`background_color` `#FAFADF` (valori statici; la barra del browser segue il meta).
- **Dettagli del tema** (`src/theme.css`, importato dopo `@heroui/styles`; le stesse variabili sono definite per
  `.light`/`[data-theme="light"]` con Coral & Cream e per `.dark`/`[data-theme="dark"]` con Dark Brut):
  - Dark Brut: `--background: #111111`, `--surface`/`--overlay`/`--field-background` `#1C1C1C`, `--foreground` e
    bordi/ombre `#FFFFFF`, `--muted: #BBBBBB`, `--accent: #FFE566` con `--accent-foreground: #111111`; il corallo
    resta come accento secondario. Il nero sul giallo ha contrasto ~16:1.
  - Coral & Cream, variabili HeroUI: `--background: #FAFADF`, `--foreground: #111111`, `--surface`/`--overlay`/`--field-background`
    `#FFFFFF`, `--muted: #555555`, `--accent: #E8635A`, `--accent-foreground: #111111` (il bianco sul
    corallo ha contrasto ~3,3:1, sotto la soglia WCAG di 4,5:1; il nero ~5,7:1), `--border` e `--separator`
    `#111111`, `--border-width: 2px`, `--field-border: #111111`, `--radius: 0.625rem` (10 px), `--surface-shadow`
    `4px 4px 0 0 #111111`, `--overlay-shadow` `6px 6px 0 0 #111111`, `--field-shadow` `3px 3px 0 0 #111111`;
    `--danger` corallo più scuro per distinguerlo dal primario.
  - le ombre usano una variabile `--brut-ink` (`#111111` in chiaro, `#FFFFFF` in scuro), così `shadow-brut` vale per
    entrambi i temi.
  - token Tailwind: colori `brut-violet`, `brut-mint`, `brut-yellow`, `brut-pink`, `brut-lavender`; ombre
    `shadow-brut-sm|brut|brut-lg`; font `font-sans` = DM Sans.
  - utility `press`: `transition` breve, hover `translate(2px,2px)` + ombra ridotta, active/`[data-pressed]`
    `translate(4px,4px)` + ombra nulla; disattivata con `prefers-reduced-motion`. Applicata ai `Button` con ombra.
  - componente `src/components/Sparkle.tsx`: stellina SVG a 4 punte (colore come prop) per le decorazioni.
- **Rifinitura delle schermate**:
  - home: titoli in minuscolo; card calendario con ombra, card segnaposto solo bordo (ombre selettive); icone delle
    card in cerchio colorato (menta, giallo, lavanda) con bordo; oggi nel calendario in cerchio corallo con bordo;
    barra di navigazione bianca con bordo e ombra, voce attiva con sfondo giallo (lavanda nel tema scuro, dove il
    giallo è il primario); Start cerchio corallo con bordo,
    ombra ed effetto pressione, sporgente come oggi; una stellina accanto al saluto.
  - accesso: card con ombra grande, tab e campi con bordo, pulsante principale corallo con effetto pressione,
    titolo in minuscolo, una stellina decorativa; caricamento e offline con lo stesso stile.
- **Contratto**: nessuna API.
- **Impatto**:
  - Nuova dipendenza: `@fontsource-variable/dm-sans@5.3.0` (solo file di font, nessun problema ARM64).
  - Nuovi file: `src/theme.css`, `src/theme/{theme,useTheme}.ts`, `src/components/Sparkle.tsx`. Modificati: `src/index.css`, `src/main.tsx` (import
    del font), `index.html`, `vite.config.ts`, `src/components/BottomNav.tsx`, `src/components/home/*`,
    `src/pages/*`, `src/components/{CenteredScreen,PinInput}.tsx` se serve.
  - Nessuna modifica al DB o al backend.
  - Rischi: le variabili interne di HeroUI possono cambiare tra versioni (si annotano quelle usate); peso del font.
- **Decisioni registrate**: D-015 (tema HeroUI neobrutalista, font, cambio di tema).

## Passi

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.
Verifiche manuali in dev (`http://localhost:5173`), vista mobile = DevTools a 375 px.

### Passo 1 — Tema di base: palette chiara e scura, font, bordi, ombre

- **Stato**: fatto (2026-11-17)
- **Obiettivo**: tutta l'app prende palette, font, bordi, raggi e ombre neobrutaliste senza toccare i componenti.
- **Lavoro**:
  - installazione del font, `src/theme.css` con variabili HeroUI, token e utility `press`; import in `index.css`
    e `main.tsx`.
  - Dark Brut per `.dark`; script di `index.html` esteso (`fitter-theme` in `localStorage`, altrimenti sistema;
    `theme-color`); `src/theme/theme.ts` (`applyTheme`, lettura/scrittura della scelta); `vite.config.ts` (colori
    del manifest, `woff2` in precache). Il pulsante arriva nel passo 2.
- **Definition of done**:
  - [x] Sfondo crema `#FAFADF`, card bianche con bordo nero da 2 px e ombra piena, testi in DM Sans (in DevTools →
        Computed, `font-family` del body = DM Sans Variable) su tutte le schermate.
  - [x] Con DevTools → Rendering → `prefers-color-scheme: dark` l'app passa a Dark Brut (sfondo `#111111`, bordi e
        ombre bianchi, primario giallo) e il `<meta name="theme-color">` vale `#111111`; tornando a `light`, Coral &
        Cream.
  - [x] Con `localStorage.setItem('fitter-theme', 'dark')` dalla console e ricarica, l'app è scura anche con il
        sistema in chiaro, senza lampo di tema chiaro; con `removeItem` torna a seguire il sistema.
  - [x] In DevTools → Network nessuna richiesta verso domini esterni; dopo `npm run build`, `dist/sw.js` elenca il
        file `.woff2` del font.
  - [x] Testo e icone sul colore primario (corallo in chiaro, giallo in scuro) sono neri `#111111`: il controllo
        di contrasto di DevTools indica almeno 4.5:1; anche il testo secondario sullo sfondo supera 4.5:1 in
        entrambi i temi.
  - [x] `npm run lint` e `npm run build` senza errori; dimensione del bundle annotata.
        _CI non verificata: nessun push al momento della chiusura; passo chiuso su conferma dell'utente._

### Passo 2 — Home: card, calendario e barra di navigazione

- **Stato**: fatto (2026-11-17)
- **Obiettivo**: la home rispecchia lo stile in ogni dettaglio.
- **Lavoro**: `Sparkle.tsx`, `useTheme.ts`; `HomePage` (con switch del tema), `WeekCalendarCard`,
  `PlaceholderCard`, `BottomNav` come descritto in *Rifinitura delle schermate*.
- **Definition of done**:
  - [x] Titoli in minuscolo; card calendario con ombra, card Calorie/Statistiche solo bordo; icone delle card in
        cerchio colorato con bordo.
  - [x] Oggi nel calendario in cerchio corallo con bordo; frecce e swipe funzionano come prima.
  - [x] Barra bianca con bordo e ombra, voce attiva con sfondo giallo; Start cerchio corallo con bordo e ombra
        che sporge sopra e sotto la barra e, toccato, si "abbassa" perdendo l'ombra.
  - [x] Una sola stellina decorativa nella home, che non copre testo o pulsanti.
  - [x] Lo switch del tema nell'header (icone sole/luna) cambia tema all'istante; ricaricando la pagina il tema scelto resta.
  - [x] Tutti i punti sopra valgono in entrambi i temi (in scuro: oggi e Start gialli, bordi e ombre bianchi).
  - [x] In vista mobile nessuno scroll orizzontale; l'ultima card resta visibile sopra la barra.
  - [x] `npm run lint` e `npm run build` senza errori.
        _CI non verificata: nessun push al momento della chiusura; passo chiuso su conferma dell'utente._

### Passo 3 — Accesso, caricamento e offline

- **Stato**: fatto (2026-11-17)
- **Obiettivo**: le schermate fuori dalla home hanno lo stesso stile.
- **Lavoro**: `AuthPage`, `PinInput`, `LoadingScreen`, `OfflineScreen`.
- **Definition of done**:
  - [x] Schermata di accesso: card con ombra grande, tab e campi (nickname e caselle del PIN) con bordo nero,
        pulsante principale corallo con effetto pressione, titolo in minuscolo, una stellina decorativa.
  - [x] Gli errori (es. "Nickname o PIN non corretti") restano ben visibili e distinguibili dal colore primario.
  - [x] Caricamento e offline ("Riprova") con lo stesso stile.
  - [x] Le schermate di accesso, caricamento e offline usano il tema scelto nella home (dopo il logout resta lo
        stesso tema).
  - [x] Login, registrazione e "Riprova" funzionano come prima.
  - [x] Con `prefers-reduced-motion: reduce` (DevTools → Rendering) i pulsanti non si spostano.
  - [x] `npm run lint` e `npm run build` senza errori; dimensione del bundle annotata e confrontata con il passo 1.
        _CI non verificata: nessun push al momento della chiusura; passo chiuso su conferma dell'utente._

## Note di implementazione

### Passo 1 (2026-11-17)
- Dipendenza: `@fontsource-variable/dm-sans@5.3.0`, importato solo l'asse dei pesi (`wght.css`): due file `woff2`
  (latin 36,9 kB, latin-ext 18,2 kB) messi in precache (`globPatterns` con `woff2`; aggiunto anche `svg`).
- File creati: `src/theme.css`, `src/theme/theme.ts` (`storedTheme`, `saveTheme`, `systemTheme`, `currentTheme`,
  `applyTheme`; usato dal pulsante nel passo 2). Modificati: `src/index.css` (import del font e del tema dopo
  HeroUI), `index.html` (script del tema esteso + `<meta name="theme-color">`), `vite.config.ts`.
- Ordine dei livelli CSS di HeroUI: `theme, base, components, utilities`; le variabili di HeroUI stanno nel livello
  `theme`, quindi le nostre (in `base`) vincono senza `!important`; gli override di `.card` e dei pulsanti stanno in
  `components` dopo quelli di HeroUI; le classi Tailwind nei componenti continuano a vincere su tutto.
- Variabili HeroUI ridefinite e classi toccate: elencate in testa a `src/theme.css` (da ricontrollare quando si
  aggiorna HeroUI).
- Ombre e bordi usano `--brut-ink` (`#111111` in chiaro, `#FFFFFF` in scuro). `--radius: 0.5rem`: card 12 px
  (`--radius-xl`), pulsanti 8 px, campi 6 px.
- Pulsanti `primary`, `secondary`, `tertiary`, `outline`, `danger`: bordo, ombra da 3 px ed effetto pressione
  (`press-brut`: hover 1 px, pressione 3 px e ombra nulla; fermo con `prefers-reduced-motion`). I `ghost` (icone
  della barra, frecce del calendario, logout) restano senza bordo.
- **Contrasti** (WCAG, calcolati): nero su corallo 5,72 · nero su giallo 14,97 · `#555` su crema 7,03 / su bianco
  7,46 · `#BBB` su `#111` 9,84 / su `#1C1C1C` 8,88 · bianco su `danger` chiaro `#B3261E` 6,54 · nero su `danger`
  scuro `#FF6B6B` 6,80. **Attenzione**: il corallo usato come colore del testo (`text-accent`) su bianco vale solo
  3,30, sufficiente per icone ma non per testo piccolo: oggi lo usa l'etichetta del giorno corrente nel calendario,
  da sistemare nel passo 2 (oggi in cerchio corallo con testo nero).
- Bundle: JS `439.44 kB` (gzip `136.65 kB`, invariato), CSS `474.38 kB` (gzip `44.36 kB`, +0,9 kB), font
  `55 kB`, precache `964.85 KiB` (+90 KiB).
- Esito verifiche locali: lint e build senza errori; `dist/sw.js` contiene i due `.woff2`; CSS generato con
  `--accent:#e8635a` (chiaro) e `#ffe566` (scuro); container dev ricostruito (`up -d --build -V frontend`). Le
  verifiche nel browser della DoD sono da fare a mano.

### Passo 2 (2026-11-17)
- File creati: `src/theme/useTheme.ts`, `src/components/{ThemeSwitch,Sparkle,IconCircle}.tsx`. Modificati:
  `src/pages/HomePage.tsx`, `src/components/BottomNav.tsx`, `src/components/home/{WeekCalendarCard,PlaceholderCard}.tsx`,
  `src/theme.css`.
- **Switch del tema** (richiesta dell'utente: switch invece del pulsante icona): `Switch` HeroUI `size="lg"`, acceso
  = scuro, icona `Sun`/`Moon` nel pallino, `aria-label="Tema scuro"`. `useTheme` legge il tema da `<html>` con
  `useSyncExternalStore` + `MutationObserver` su `data-theme`, così lo switch resta allineato anche quando lo script
  inline segue il sistema; il cambio salva la scelta e chiama `applyTheme`.
- `theme.css`: token `brut-black` (nero fisso per testo/icone su colori pastello) e `brut-highlight` (giallo in
  chiaro, lavanda in scuro, dove il giallo è il primario) al posto della variante `dark:`; switch con bordo e
  pallino senza ombra sfumata.
- Home: "ciao, <nickname>" in minuscolo (`text-3xl font-extrabold`) con una stellina gialla ruotata accanto; a
  destra switch del tema e logout. Card calendario con ombra (quella del tema), titolo "questa settimana"; oggi in
  cerchio `bg-accent` con bordo, testo nero e ombra piccola; l'etichetta del giorno corrente è `text-foreground`
  in grassetto (non più corallo su bianco: risolto il contrasto 3,30 segnalato nel passo 1). Card "calorie" e
  "statistiche" piatte (`shadow-none`), icona in `IconCircle` (rosa, menta) e "in arrivo".
- Barra: bordo 2 px e `shadow-brut`; voce attiva con bordo e `bg-brut-highlight`, icona nera (contrasto nero su
  giallo 14,97, su lavanda ~11); Start `primary` rotondo con bordo, ombra ed effetto pressione del tema.
- Bundle: JS `449.69 kB` (gzip `139.42 kB`, +2,8 kB per `Switch`), CSS `475.91 kB` (gzip `44.63 kB`).
- Esito verifiche locali: lint e build senza errori; nessun `any` né colori esadecimali nei componenti. Le
  verifiche nel browser della DoD sono da fare a mano.

### Passo 3 (2026-11-17)
- Modificati: `src/pages/{AuthPage,OfflineScreen}.tsx`, `src/components/PinInput.tsx`, `src/theme.css`.
  `LoadingScreen` invariata: lo spinner prende già il colore primario dal tema.
- Accesso: card con `shadow-brut-lg`, titolo "fitter" in minuscolo (`text-4xl font-extrabold`) con una stellina
  rosa accanto; pulsante "Accedi"/"Registrati" `primary` (corallo / giallo) con effetto pressione del tema.
- Campi: tolto `variant="secondary"` da nickname e PIN (era servito in CORE-002-FE-01 perché i campi non si
  distinguevano dalla card): ora il bordo nero li separa, quindi sono bianchi (`#1C1C1C` in scuro) con bordo e
  ombra piccola; in focus il bordo diventa del colore primario (`--field-border-focus`).
- `theme.css`: `.alert` con bordo, raggio 8 px e ombra piccola (gli errori restano rossi `danger`, distinti dal
  corallo: `#B3261E` in chiaro, `#FF6B6B` in scuro); tab con bordo sul contenitore, tab selezionata con bordo e
  colore `--segment` = `brut-highlight` (giallo / lavanda) e testo nero.
- Offline: card con ombra grande, titolo "server non raggiungibile" in minuscolo, "Riprova" `primary`.
- **Bundle, confronto con il passo 1**:

  | | Passo 1 | Passo 3 |
  |---|---|---|
  | JS | `439.44 kB` (gzip `136.65 kB`) | `449.92 kB` (gzip `139.44 kB`) |
  | CSS | `474.38 kB` (gzip `44.36 kB`) | `477.02 kB` (gzip `44.75 kB`) |
  | Precache PWA | `964.85 KiB` | `977.66 KiB` |

  L'aumento del JS viene dallo `Switch` di HeroUI (passo 2).
- Esito verifiche locali: lint e build senza errori. Le verifiche nel browser della DoD sono da fare a mano.

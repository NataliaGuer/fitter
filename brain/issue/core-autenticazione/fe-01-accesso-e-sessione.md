# CORE-002-FE-01 — Setup HeroUI, schermate di accesso e sessione

- **Feature**: CORE-002 (`features/core-autenticazione.md`)
- **Lato**: frontend
- **Stato**: fatta (2026-11-15; approvata 2026-11-15)
- **Dipende da**: CORE-002-BE-01 (API `/api/auth/*`)

## Obiettivo

Preparare il frontend per le prime schermate reali (HeroUI v3 + Tailwind 4, pulizia del boilerplate Vite) e
implementare l'accesso: all'apertura l'app verifica la sessione e mostra la home oppure la schermata di accesso
(Accedi / Registrati con nickname e PIN a 4 cifre). Nessuna modifica a `backend/`.

## Requisiti coperti

Dalla sezione *Requisiti → Frontend* della feature:
- [x] Setup HeroUI + Tailwind e pulizia del boilerplate Vite.
- [x] All'avvio verifica della sessione (`/api/auth/me`): home se valida, altrimenti accesso.
- [x] Schermata di accesso con modalità "Accedi" / "Registrati".
- [x] Nickname + PIN a 4 caselle con tastierino numerico; in registrazione il PIN si inserisce una sola volta
  (non è oscurato, niente campo di conferma: decisione dell'utente, 2026-11-15).
- [x] Messaggi di errore chiari: credenziali errate, nickname già usato, input non valido.
- [x] Pulsante di logout nella home segnaposto.
- [x] Backend non raggiungibile: messaggio con "Riprova", mai ritorno al login.

Criterio di accettazione della feature verificato qui end-to-end: chiudendo e riaprendo l'app l'utente è ancora
autenticato.

## Fuori scope

- Qualsiasi modifica alle API o al backend (`CORE-002-BE-01`).
- Router e navigazione tra più pagine (D-010: con la prima feature a più pagine).
- Selettore manuale del tema (segue il sistema).
- Icone/manifest definitivi della PWA.

## Piano tecnico

Le scelte di fondo sono già decise e **non si ripropongono** (D-007, D-010): HeroUI v3 + Tailwind 4, nessun
router, `AuthProvider` con React context, wrapper su `fetch`, proxy Vite per `/api`, service worker che non
intercetta `/api`, tema che segue il sistema, offline senza logout. I dettagli rimanenti sono decisi sotto
(D-013).

- **Contesto**: `frontend/` è il boilerplate Vite: `App.tsx` vuoto, `App.css` e `index.css` con lo stile del
  template, asset di esempio in `src/assets/` (`hero.png`, `react.svg`, `vite.svg`). `vite.config.ts` ha già
  `vite-plugin-pwa` ma né proxy né regola per `/api`. Nessuna dipendenza UI.

- **Decisioni** (prese il 2026-11-15, D-013; solo dettagli non coperti da D-010):
  - *Validazione degli input lato client*: controlli semplici nel componente prima di inviare: lunghezza e
    caratteri del nickname con la stessa regex del backend (`^[A-Za-z0-9_.-]{3,30}$`), PIN di 4 cifre. Il `422` del backend resta come ulteriore protezione. Errori immediati e in italiano, nessuna
    dipendenza; la regola del nickname è duplicata tra frontend e backend.
    Scartato: libreria di form (es. react-hook-form + zod), due dipendenze per un solo form.
  - *Messaggi d'errore*: mappa status → messaggio in italiano nel frontend: `401` "Nickname o PIN non corretti",
    `409` "Nickname già in uso", `422` "Dati non validi", errore di rete "Server non raggiungibile". Il testo è
    sotto il controllo della UI e il backend resta in inglese.
    Scartato: mostrare il `detail` del backend (testi tecnici e in inglese).

- **Dettagli**:
  - `src/api/client.ts`: `apiFetch<T>(path, options)` su `fetch` con `credentials: 'same-origin'`, JSON in/out;
    lancia `ApiError` (con `status`) per risposte non 2xx e `NetworkError` se la richiesta non arriva al server.
  - `src/api/auth.ts`: `register`, `login`, `logout`, `me`, tipizzate con `User = { id: number; nickname: string }`.
  - `src/auth/AuthProvider.tsx` + `useAuth.ts`: stato `loading | authenticated(user) | anonymous | offline`,
    azioni `login`, `register`, `logout`, `retry`. All'avvio `me()`: `200` → authenticated, `401` → anonymous,
    `NetworkError` o `5xx` → offline.
  - `AuthPage`: `Tabs` HeroUI "Accedi" / "Registrati", `TextField`/`Input` per il nickname
    (`autocapitalize="none"`, `autocomplete="username"`), `InputOTP` a 4 caselle per il PIN
    (`inputMode="numeric"`), un solo `InputOTP` anche in registrazione, `Button` a tutta larghezza con stato
    di caricamento, `Alert` per gli errori.
  - Logout: se la chiamata non arriva al server la sessione resta valida, quindi si mostra l'errore e si resta
    nella home (non si passa ad `anonymous`).
  - Proxy Vite: `server.proxy['/api'] = { target: process.env.API_PROXY_TARGET ?? 'http://localhost:8000' }`;
    in `docker-compose.dev.yaml` il servizio `frontend` riceve `API_PROXY_TARGET=http://app:8000`.
  - PWA: `workbox.navigateFallbackDenylist: [/^\/api\//]`.
  - Tema: classi Tailwind/HeroUI con variante dark guidata da `prefers-color-scheme`.

- **Contratto** (da `CORE-002-BE-01`, non modificabile da questa issue):

  | Metodo | Endpoint | Request (JSON) | Risposta |
  |--------|----------|----------------|----------|
  | POST | `/api/auth/register` | `{"nickname": str, "pin": str}` | `201 {"id": int, "nickname": str}` + cookie · `409` nickname già usato · `422` input non valido |
  | POST | `/api/auth/login` | `{"nickname": str, "pin": str}` | `200 {"id": int, "nickname": str}` + cookie · `401` credenziali errate · `422` input non valido |
  | POST | `/api/auth/logout` | — | `204`, cookie cancellato; idempotente (anche senza cookie) |
  | GET  | `/api/auth/me` | — | `200 {"id": int, "nickname": str}` + cookie rinnovato · `401` |

  Il frontend usa solo lo status code; il cookie `fitter_session` è `HttpOnly` e non viene mai letto da JS.

- **Impatto**:
  - Nuove dipendenze (versioni verificate su npm il 2026-11-15): `@heroui/react@3.2.7`, `@heroui/styles@3.2.7`,
    `tailwindcss@4.3.5`, `@tailwindcss/vite@4.3.5` (compatibile con Vite 8) e le peer dependency di HeroUI:
    `react-aria`, `react-aria-components`, `@react-aria/ssr`, `@react-aria/utils`, `@internationalized/date`.
    Solo JavaScript: nessun problema ARM64 (la build gira comunque su runner ARM in CI).
  - Nuovi file: `src/api/{client,auth}.ts`, `src/auth/{AuthProvider.tsx,useAuth.ts}`,
    `src/pages/{AuthPage,HomePage,LoadingScreen,OfflineScreen}.tsx`.
  - Modificati: `vite.config.ts` (plugin Tailwind, proxy, regola PWA), `src/index.css` (sostituito da import di
    Tailwind e HeroUI), `src/App.tsx`, `src/main.tsx`, `docker-compose.dev.yaml` (`API_PROXY_TARGET` nel servizio
    `frontend`).
  - Rimossi: `src/App.css`, `src/assets/{hero.png,react.svg,vite.svg}`.
  - Nessuna modifica al DB.
  - Rischi: peso del bundle (si annota la dimensione dopo il passo 1 e la si confronta alla fine); esempi online di
    HeroUI spesso riferiti alla v2 (API diverse): fare riferimento alla documentazione v3.

- **Decisioni registrate**: D-010 (già esistente), D-013 (validazione client, messaggi d'errore).

## Passi

Ogni passo è un'unità di lavoro incrementale: lascia `main` rilasciabile (CI verde) e si chiude solo quando
l'utente conferma che la definition of done è soddisfatta.

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.

Tutti i passi richiedono che `CORE-002-BE-01` sia `fatta`. Verifiche manuali nell'ambiente dev
(`./script/start-dev.sh`, app su `http://localhost:5173`), "vista mobile" = DevTools del browser con un dispositivo
di 375 px di larghezza.

### Passo 1 — Setup Tailwind 4 + HeroUI v3 e pulizia del boilerplate

- **Stato**: fatto (2026-11-15)
- **Obiettivo**: il frontend usa HeroUI e Tailwind, senza più nulla del template Vite.
- **Lavoro**:
  - installazione delle dipendenze; plugin `@tailwindcss/vite` in `vite.config.ts`.
  - `src/index.css` con import di Tailwind e degli stili HeroUI.
  - rimozione di `App.css` e degli asset di esempio; `App.tsx` mostra una schermata segnaposto "Fitter" con un
    componente HeroUI (es. `Card`).
- **Definition of done**:
  - [x] `npm run lint` e `npm run build` senza errori; la dimensione del bundle JS stampata dalla build è annotata
        nelle *Note di implementazione*.
  - [x] `npm ls @heroui/react tailwindcss` mostra `3.2.7` e `4.3.5`, senza peer dependency mancanti.
  - [x] `src/App.css`, `src/assets/hero.png`, `react.svg`, `vite.svg` non esistono più e nessun file in `src/` li
        importa.
  - [x] Su `http://localhost:5173` si vede la schermata segnaposto con il componente HeroUI; cambiando il tema del
        sistema (o emulandolo in DevTools) passa da chiaro a scuro.
  - [ ] CI verde.
        _Non verificata: nessun push al momento della chiusura; passo chiuso su conferma dell'utente._

### Passo 2 — Proxy `/api` e service worker

- **Stato**: fatto (2026-11-15)
- **Obiettivo**: in sviluppo il frontend parla con il backend sulla stessa origine; in prod il service worker non
  serve mai `/api` dalla cache.
- **Lavoro**:
  - `vite.config.ts`: `server.proxy` per `/api` con `API_PROXY_TARGET`; `workbox.navigateFallbackDenylist`.
  - `docker-compose.dev.yaml`: `API_PROXY_TARGET=http://app:8000` nel servizio `frontend`.
- **Definition of done**:
  - [x] Con l'ambiente dev avviato, `curl -i http://localhost:5173/api/auth/me` risponde `401` (risposta del
        backend arrivata tramite il proxy).
  - [x] Dopo `npm run build`, il file `dist/sw.js` contiene la regola `/^\/api\//` nel `NavigationRoute`
        (verificabile con una ricerca testuale di `api` in `dist/sw.js`).
  - [x] `npm run lint` e `npm run build` senza errori; CI verde.

### Passo 3 — Client API e `AuthProvider`

- **Stato**: fatto (2026-11-15)
- **Obiettivo**: l'app sa all'avvio se l'utente è autenticato, anonimo o offline, e lo mostra.
- **Lavoro**:
  - `src/api/client.ts`, `src/api/auth.ts`.
  - `src/auth/AuthProvider.tsx`, `src/auth/useAuth.ts`.
  - `LoadingScreen` (spinner HeroUI) e `OfflineScreen` ("Server non raggiungibile" + pulsante "Riprova").
  - `App.tsx`: in base allo stato mostra caricamento, offline, oppure due segnaposto testuali "Accesso" /
    "Ciao, <nickname>" (sostituiti nei passi 4 e 5).
- **Definition of done**:
  - [x] Senza cookie, aprendo l'app si vede brevemente il caricamento e poi il segnaposto "Accesso".
  - [x] Registrando un utente dalla console del browser (così il cookie finisce nel browser) con `fetch('/api/auth/register', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({nickname:'prova2', pin:'1234'})})`,
        poi ricaricando la pagina si vede "Ciao, prova2".
  - [x] Fermato il backend (`docker compose -f docker-compose.dev.yaml stop app`) e ricaricata la pagina, si vede
        la schermata offline con "Riprova", non il segnaposto "Accesso"; riavviato il backend, "Riprova" porta a
        "Ciao, prova2".
  - [x] In `src/` non compaiono `any` espliciti (`grep -rn ": any" src` senza risultati).
  - [x] `npm run lint` e `npm run build` senza errori; CI verde.

### Passo 4 — Schermata di accesso (Accedi / Registrati)

- **Stato**: fatto (2026-11-15)
- **Obiettivo**: l'utente può registrarsi e accedere dall'app, con messaggi d'errore in italiano.
- **Lavoro**:
  - `src/pages/AuthPage.tsx` con `Tabs`, campo nickname, `InputOTP` per il PIN,
    validazione client, mappa degli errori per status, pulsante con stato di caricamento.
  - `App.tsx`: `AuthPage` al posto del segnaposto "Accesso".
- **Definition of done**:
  - [x] Registrazione di un nuovo nickname con un PIN di 4 cifre → si arriva a "Ciao, <nickname>".
  - [x] Registrazione di un nickname esistente scritto con maiuscole diverse → messaggio "Nickname già in uso".
  - [x] Accedi con PIN errato e con nickname inesistente → in entrambi i casi "Nickname o PIN non corretti".
  - [x] Nickname di 2 caratteri o con spazi, PIN incompleto → messaggio d'errore mostrato
        senza che parta la richiesta (tab *Network* di DevTools vuota).
  - [x] In vista mobile: nessuno scroll orizzontale, pulsante a tutta larghezza, il campo PIN ha
        `inputmode="numeric"` (visibile ispezionando l'elemento) e da telefono apre il tastierino numerico.
  - [x] `npm run lint` e `npm run build` senza errori; CI verde.

### Passo 5 — Home segnaposto, logout e persistenza della sessione

- **Stato**: fatto (2026-11-15)
- **Obiettivo**: la home mostra l'utente e permette di uscire; la sessione sopravvive alla chiusura dell'app.
- **Lavoro**:
  - `src/pages/HomePage.tsx`: "Ciao, <nickname>" + pulsante "Esci" (errore mostrato se il logout non arriva al
    server).
  - `App.tsx`: `HomePage` al posto del segnaposto.
- **Definition of done**:
  - [x] Dopo l'accesso, chiudendo del tutto il browser e riaprendo `http://localhost:5173` si vede direttamente la
        home, senza passare dall'accesso.
  - [x] "Esci" → schermata di accesso; ricaricando la pagina si resta sull'accesso.
  - [x] Con sessione valida e backend fermo, ricaricando la pagina si vede la schermata offline e non l'accesso;
        con il backend fermo, "Esci" mostra un errore e si resta nella home.
  - [x] La dimensione del bundle JS dopo la build è annotata nelle *Note di implementazione* accanto a quella del
        passo 1.
  - [x] `npm run lint` e `npm run build` senza errori; CI verde.
  - [ ] Se il rilascio è attivo (`RELEASE_ENABLED=true`): da telefono, tramite VPN, registrazione e accesso
        funzionano e l'app installata come PWA riaperta il giorno dopo mostra la home. Se il rilascio non è
        attivo, la voce si segna come non applicabile.
        _Non verificata: passo chiuso su conferma dell'utente._

## Note di implementazione

### Passo 1 (2026-11-15)
- Dipendenze installate: `@heroui/react@3.2.7`, `@heroui/styles@3.2.7`, `react-aria@3.53.1`,
  `react-aria-components@1.22.1`, `@react-aria/ssr`, `@react-aria/utils`, `@internationalized/date`; di sviluppo
  `tailwindcss@4.3.5`, `@tailwindcss/vite@4.3.5`. `npm audit`: 0 vulnerabilità.
- `src/index.css`: solo `@import "tailwindcss"` + `@import "@heroui/styles"` (ordine richiesto da HeroUI).
- **Tema che segue il sistema**: HeroUI v3 attiva il tema scuro solo con la classe `dark` e `data-theme="dark"`
  su `<html>`, senza seguire `prefers-color-scheme` da solo. Un piccolo script inline in `index.html` imposta
  classe/attributo prima del primo render (niente lampo di tema chiaro) e li aggiorna quando cambia il tema del
  sistema. Nessuna dipendenza aggiunta (niente `next-themes` o simili).
- `<body>` con le classi `bg-background text-foreground` del tema HeroUI.
- Rimossi `src/App.css`, `src/assets/{hero.png,react.svg,vite.svg}` (cartella `src/assets/` eliminata).
  `App.tsx` mostra una `Card` HeroUI segnaposto.
- **Dimensione del bundle (passo 1)**: JS `263.30 kB` (gzip `82.27 kB`), CSS `468.52 kB` (gzip `42.92 kB`),
  precache PWA `716.10 KiB`. Il CSS è grande perché `@heroui/styles` include gli stili di tutti i componenti:
  se servirà, si possono importare solo quelli usati (vedi README di `@heroui/styles`).
- Container dev del frontend ricostruito con `up -d --build -V frontend` (`-V` rinnova il volume anonimo di
  `node_modules`, altrimenti restano le dipendenze vecchie).

### Passo 2 (2026-11-15)
- `vite.config.ts`: `server.proxy['/api']` verso `API_PROXY_TARGET` (default `http://localhost:8000`, per chi
  avvia Vite fuori da Docker); `workbox.navigateFallbackDenylist: [/^\/api\//]`.
- `docker-compose.dev.yaml`: `API_PROXY_TARGET=http://app:8000` nel servizio `frontend`.
- Esito verifiche locali: `curl -i http://localhost:5173/api/auth/me` → `401 {"detail":"Not authenticated"}`
  (risposta del backend tramite il proxy); anche `POST /api/auth/logout` passa (`204`); `dist/sw.js` contiene
  `denylist:[/^\/api\//]`; lint e build senza errori, bundle invariato.

### Passo 3 (2026-11-15)
- File creati: `src/api/{client,auth}.ts`, `src/auth/{context.ts,AuthProvider.tsx,useAuth.ts}`,
  `src/components/CenteredScreen.tsx`, `src/pages/{LoadingScreen,OfflineScreen}.tsx`. Modificati: `src/App.tsx`
  (sceglie la schermata in base allo stato, con segnaposto "Accesso" / "Ciao, <nickname>"), `src/main.tsx`
  (`<AuthProvider>` intorno ad `<App>`).
- Contesto, provider e hook in tre file separati (`context.ts`, `AuthProvider.tsx`, `useAuth.ts`), così ogni
  file `.tsx` esporta solo componenti (requisito del fast refresh di Vite).
- Stato `offline` per errori di rete **e** per qualunque risposta di `/me` diversa da `200`/`401` (5xx compresi):
  con il backend fermo il proxy di Vite risponde `502`, in prod il reverse proxy risponde `502`/`504`.
- `retry` riporta lo stato a `loading` e ripete `/me`; l'effetto ignora le risposte arrivate dopo lo smontaggio
  (in sviluppo `StrictMode` esegue l'effetto due volte: due chiamate a `/me`, innocue).
- `login`/`register`/`logout` del contesto propagano `ApiError`/`NetworkError`: i messaggi li mostra la UI
  (passi 4 e 5).
- Bundle: JS `306.03 kB` (gzip `96.66 kB`, +43 kB per `Button` e `Spinner` di HeroUI/React Aria), CSS invariato.
- Esito verifiche locali: lint e build senza errori; nessun `any` in `src/`; backend fermo → `/api/auth/me` via
  proxy `502`, riavviato → `401`. Le verifiche nel browser della DoD sono da fare a mano (nessun browser
  disponibile qui).

### Passo 4 (2026-11-15)
- File creati: `src/pages/AuthPage.tsx`, `src/components/PinInput.tsx`, `src/auth/validation.ts`,
  `src/api/errors.ts`. Modificato: `src/App.tsx` (`AuthPage` al posto del segnaposto "Accesso").
- `AuthPage`: `Tabs` HeroUI "Accedi" / "Registrati"; ogni tab ha il proprio form, quindi cambiando tab i campi
  ripartono vuoti. Componenti HeroUI: `Card`, `Tabs`, `Form`, `TextField` + `Label`/`Input`/`FieldError`,
  `InputOTP`, `Alert`, `Button` (`isPending` durante la richiesta).
- `PinInput`: `InputOTP` a 4 caselle con `inputMode="numeric"` e `pattern` solo cifre (le lettere non si possono
  digitare); `autoComplete` `current-password` in accesso e `new-password` in registrazione, così il browser può
  proporre di salvare il PIN invece di suggerire codici SMS (default di `input-otp`: `one-time-code`).
- Validazione al submit (`validation.ts`, stesse regole del backend): con errori i messaggi compaiono sotto i campi
  e la richiesta non parte.
- `errors.ts`: messaggi in italiano per status (D-013): `401` in accesso "Nickname o PIN non corretti", `409` in
  registrazione "Nickname già in uso", `422` "Dati non validi", errore di rete o `5xx` "Server non raggiungibile",
  altro "Si è verificato un errore, riprova".
- Bundle: JS `416.30 kB` (gzip `129.12 kB`, +110 kB per Tabs, TextField, Form, InputOTP, Alert), CSS invariato.
- Campi (nickname e PIN) con `variant="secondary"` di HeroUI, su richiesta dell'utente: con la variante di default
  lo sfondo dei campi ha lo stesso colore della `Card` (bianco su bianco nel tema chiaro, grigio scuro su grigio
  scuro in quello scuro) e i campi non si distinguono. `secondary` usa il colore `--default`: più chiaro della card
  nel tema scuro, grigio leggero in quello chiaro. Nessun CSS custom. Regola da seguire per i campi dentro una card.
- **Tolto il campo "Conferma PIN"** dalla registrazione, su decisione dell'utente: il PIN non è oscurato e l'utente
  lo vede mentre lo digita, quindi la conferma non serve. Aggiornati requisito e sezione UI della feature, requisiti,
  dettagli e DoD di questa issue; rimossa `pinConfirmError` da `validation.ts`.
- Caselle del PIN centrate (`className="justify-center"` su `InputOTP`), su richiesta dell'utente; etichetta e
  messaggio d'errore restano allineati a sinistra come il campo nickname.
- Esito verifiche locali: lint e build senza errori. Le verifiche nel browser e da telefono della DoD sono da fare
  a mano (nessun browser disponibile qui).

### Passo 5 (2026-11-15)
- File creato: `src/pages/HomePage.tsx` ("Ciao, <nickname>" + pulsante "Esci"). Modificato: `src/App.tsx` (rimosso
  il componente segnaposto: ora ogni stato ha la sua schermata).
- Logout: durante la richiesta il pulsante mostra il caricamento; se la richiesta non arriva al server compare un
  `Alert` ("Server non raggiungibile") e si resta nella home, perché la sessione è ancora valida.
- **Dimensione del bundle, confronto con il passo 1**:

  | | Passo 1 | Passo 5 |
  |---|---|---|
  | JS | `263.30 kB` (gzip `82.27 kB`) | `416.54 kB` (gzip `129.08 kB`) |
  | CSS | `468.52 kB` (gzip `42.92 kB`) | `468.78 kB` (gzip `42.97 kB`) |
  | Precache PWA | `716.10 KiB` | `866.00 KiB` |

  L'aumento del JS viene dai componenti HeroUI/React Aria usati (Tabs, TextField, Form, InputOTP, Alert, Button,
  Spinner). Circa 170 kB compressi in tutto, scaricati una volta e poi serviti dalla cache della PWA: accettabile.
  Possibile ottimizzazione futura: importare in CSS solo i componenti usati (vedi README di `@heroui/styles`).
- Esito verifiche locali: lint e build senza errori. Le verifiche nel browser della DoD sono da fare a mano
  (nessun browser disponibile qui); la verifica da telefono tramite VPN richiede il rilascio.

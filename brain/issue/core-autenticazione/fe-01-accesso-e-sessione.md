# CORE-002-FE-01 — Setup HeroUI, schermate di accesso e sessione

- **Feature**: CORE-002 (`features/core-autenticazione.md`)
- **Lato**: frontend
- **Stato**: bozza
- **Dipende da**: CORE-002-BE-01 (API `/api/auth/*`)

## Obiettivo

Preparare il frontend per le prime schermate reali (HeroUI v3 + Tailwind 4, pulizia del boilerplate Vite) e
implementare l'accesso: all'apertura l'app verifica la sessione e mostra la home oppure la schermata di accesso
(Accedi / Registrati con nickname e PIN a 4 cifre). Nessuna modifica a `backend/`.

## Requisiti coperti

Dalla sezione *Requisiti → Frontend* della feature:
- [ ] Setup HeroUI + Tailwind e pulizia del boilerplate Vite.
- [ ] All'avvio verifica della sessione (`/api/auth/me`): home se valida, altrimenti accesso.
- [ ] Schermata di accesso con modalità "Accedi" / "Registrati".
- [ ] Nickname + PIN a 4 caselle con tastierino numerico; in registrazione PIN ripetuto per conferma.
- [ ] Messaggi di errore chiari: credenziali errate, nickname già usato, input non valido.
- [ ] Pulsante di logout nella home segnaposto.
- [ ] Backend non raggiungibile: messaggio con "Riprova", mai ritorno al login.

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
intercetta `/api`, tema che segue il sistema, offline senza logout.

- **Contesto**: `frontend/` è il boilerplate Vite: `App.tsx` vuoto, `App.css` e `index.css` con lo stile del
  template, asset di esempio in `src/assets/` (`hero.png`, `react.svg`, `vite.svg`). `vite.config.ts` ha già
  `vite-plugin-pwa` ma né proxy né regola per `/api`. Nessuna dipendenza UI.

- **Alternative** (solo dettagli non coperti da D-010):
  - *Validazione degli input lato client*
    - A — controlli semplici nel componente (lunghezza e caratteri del nickname con la stessa regex del backend,
      PIN di 4 cifre, PIN e conferma uguali) prima di inviare; il `422` del backend resta come rete di sicurezza
      (pro: errori immediati e in italiano, nessuna dipendenza / contro: la regola del nickname è duplicata).
    - B — libreria di form (es. react-hook-form + zod) (contro: due dipendenze per un solo form).
  - *Messaggi d'errore*
    - A — mappa status → messaggio in italiano nel frontend (`401` "Nickname o PIN non corretti", `409` "Nickname
      già in uso", `422` "Dati non validi", errore di rete "Server non raggiungibile") (pro: il testo è sotto
      controllo della UI, il backend può restare in inglese / contro: nessuno rilevante).
    - B — mostrare il `detail` del backend (contro: testi tecnici e in inglese).
- **Proposta**: A in entrambi i casi.

- **Dettagli**:
  - `src/api/client.ts`: `apiFetch<T>(path, options)` su `fetch` con `credentials: 'same-origin'`, JSON in/out;
    lancia `ApiError` (con `status`) per risposte non 2xx e `NetworkError` se la richiesta non arriva al server.
  - `src/api/auth.ts`: `register`, `login`, `logout`, `me`, tipizzate con `User = { id: number; nickname: string }`.
  - `src/auth/AuthProvider.tsx` + `useAuth.ts`: stato `loading | authenticated(user) | anonymous | offline`,
    azioni `login`, `register`, `logout`, `retry`. All'avvio `me()`: `200` → authenticated, `401` → anonymous,
    `NetworkError` o `5xx` → offline.
  - `AuthPage`: `Tabs` HeroUI "Accedi" / "Registrati", `TextField`/`Input` per il nickname
    (`autocapitalize="none"`, `autocomplete="username"`), `InputOTP` a 4 caselle per il PIN
    (`inputMode="numeric"`), in registrazione secondo `InputOTP` di conferma, `Button` a tutta larghezza con stato
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

- **Decisioni registrate**: D-010 (già esistente); nuove da registrare all'approvazione (validazione client
  semplice, messaggi d'errore mappati per status).

## Passi

Ogni passo è un'unità di lavoro incrementale: lascia `main` rilasciabile (CI verde) e si chiude solo quando
l'utente conferma che la definition of done è soddisfatta.

Stati del passo: `da fare` → `in corso` → `in verifica` → `fatto (AAAA-MM-GG)`.

Tutti i passi richiedono che `CORE-002-BE-01` sia `fatta`. Verifiche manuali nell'ambiente dev
(`./script/start-dev.sh`, app su `http://localhost:5173`), "vista mobile" = DevTools del browser con un dispositivo
di 375 px di larghezza.

### Passo 1 — Setup Tailwind 4 + HeroUI v3 e pulizia del boilerplate

- **Stato**: da fare
- **Obiettivo**: il frontend usa HeroUI e Tailwind, senza più nulla del template Vite.
- **Lavoro**:
  - installazione delle dipendenze; plugin `@tailwindcss/vite` in `vite.config.ts`.
  - `src/index.css` con import di Tailwind e degli stili HeroUI.
  - rimozione di `App.css` e degli asset di esempio; `App.tsx` mostra una schermata segnaposto "Fitter" con un
    componente HeroUI (es. `Card`).
- **Definition of done**:
  - [ ] `npm run lint` e `npm run build` senza errori; la dimensione del bundle JS stampata dalla build è annotata
        nelle *Note di implementazione*.
  - [ ] `npm ls @heroui/react tailwindcss` mostra `3.2.7` e `4.3.5`, senza peer dependency mancanti.
  - [ ] `src/App.css`, `src/assets/hero.png`, `react.svg`, `vite.svg` non esistono più e nessun file in `src/` li
        importa.
  - [ ] Su `http://localhost:5173` si vede la schermata segnaposto con il componente HeroUI; cambiando il tema del
        sistema (o emulandolo in DevTools) passa da chiaro a scuro.
  - [ ] CI verde.

### Passo 2 — Proxy `/api` e service worker

- **Stato**: da fare
- **Obiettivo**: in sviluppo il frontend parla con il backend sulla stessa origine; in prod il service worker non
  serve mai `/api` dalla cache.
- **Lavoro**:
  - `vite.config.ts`: `server.proxy` per `/api` con `API_PROXY_TARGET`; `workbox.navigateFallbackDenylist`.
  - `docker-compose.dev.yaml`: `API_PROXY_TARGET=http://app:8000` nel servizio `frontend`.
- **Definition of done**:
  - [ ] Con l'ambiente dev avviato, `curl -i http://localhost:5173/api/auth/me` risponde `401` (risposta del
        backend arrivata tramite il proxy).
  - [ ] Dopo `npm run build`, il file `dist/sw.js` contiene la regola `/^\/api\//` nel `NavigationRoute`
        (verificabile con una ricerca testuale di `api` in `dist/sw.js`).
  - [ ] `npm run lint` e `npm run build` senza errori; CI verde.

### Passo 3 — Client API e `AuthProvider`

- **Stato**: da fare
- **Obiettivo**: l'app sa all'avvio se l'utente è autenticato, anonimo o offline, e lo mostra.
- **Lavoro**:
  - `src/api/client.ts`, `src/api/auth.ts`.
  - `src/auth/AuthProvider.tsx`, `src/auth/useAuth.ts`.
  - `LoadingScreen` (spinner HeroUI) e `OfflineScreen` ("Server non raggiungibile" + pulsante "Riprova").
  - `App.tsx`: in base allo stato mostra caricamento, offline, oppure due segnaposto testuali "Accesso" /
    "Ciao, <nickname>" (sostituiti nei passi 4 e 5).
- **Definition of done**:
  - [ ] Senza cookie, aprendo l'app si vede brevemente il caricamento e poi il segnaposto "Accesso".
  - [ ] Registrando un utente dalla console del browser (così il cookie finisce nel browser) con `fetch('/api/auth/register', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({nickname:'prova2', pin:'1234'})})`,
        poi ricaricando la pagina si vede "Ciao, prova2".
  - [ ] Fermato il backend (`docker compose -f docker-compose.dev.yaml stop app`) e ricaricata la pagina, si vede
        la schermata offline con "Riprova", non il segnaposto "Accesso"; riavviato il backend, "Riprova" porta a
        "Ciao, prova2".
  - [ ] In `src/` non compaiono `any` espliciti (`grep -rn ": any" src` senza risultati).
  - [ ] `npm run lint` e `npm run build` senza errori; CI verde.

### Passo 4 — Schermata di accesso (Accedi / Registrati)

- **Stato**: da fare
- **Obiettivo**: l'utente può registrarsi e accedere dall'app, con messaggi d'errore in italiano.
- **Lavoro**:
  - `src/pages/AuthPage.tsx` con `Tabs`, campo nickname, `InputOTP` per PIN (e conferma in registrazione),
    validazione client, mappa degli errori per status, pulsante con stato di caricamento.
  - `App.tsx`: `AuthPage` al posto del segnaposto "Accesso".
- **Definition of done**:
  - [ ] Registrazione di un nuovo nickname con PIN e conferma uguali → si arriva a "Ciao, <nickname>".
  - [ ] Registrazione di un nickname esistente scritto con maiuscole diverse → messaggio "Nickname già in uso".
  - [ ] Accedi con PIN errato e con nickname inesistente → in entrambi i casi "Nickname o PIN non corretti".
  - [ ] Nickname di 2 caratteri o con spazi, PIN incompleto, PIN e conferma diversi → messaggio d'errore mostrato
        senza che parta la richiesta (tab *Network* di DevTools vuota).
  - [ ] In vista mobile: nessuno scroll orizzontale, pulsante a tutta larghezza, il campo PIN ha
        `inputmode="numeric"` (visibile ispezionando l'elemento) e da telefono apre il tastierino numerico.
  - [ ] `npm run lint` e `npm run build` senza errori; CI verde.

### Passo 5 — Home segnaposto, logout e persistenza della sessione

- **Stato**: da fare
- **Obiettivo**: la home mostra l'utente e permette di uscire; la sessione sopravvive alla chiusura dell'app.
- **Lavoro**:
  - `src/pages/HomePage.tsx`: "Ciao, <nickname>" + pulsante "Esci" (errore mostrato se il logout non arriva al
    server).
  - `App.tsx`: `HomePage` al posto del segnaposto.
- **Definition of done**:
  - [ ] Dopo l'accesso, chiudendo del tutto il browser e riaprendo `http://localhost:5173` si vede direttamente la
        home, senza passare dall'accesso.
  - [ ] "Esci" → schermata di accesso; ricaricando la pagina si resta sull'accesso.
  - [ ] Con sessione valida e backend fermo, ricaricando la pagina si vede la schermata offline e non l'accesso;
        con il backend fermo, "Esci" mostra un errore e si resta nella home.
  - [ ] La dimensione del bundle JS dopo la build è annotata nelle *Note di implementazione* accanto a quella del
        passo 1.
  - [ ] `npm run lint` e `npm run build` senza errori; CI verde.
  - [ ] Se il rilascio è attivo (`RELEASE_ENABLED=true`): da telefono, tramite VPN, registrazione e accesso
        funzionano e l'app installata come PWA riaperta il giorno dopo mostra la home. Se il rilascio non è
        attivo, la voce si segna come non applicabile.

## Note di implementazione

Da compilare durante lo sviluppo.

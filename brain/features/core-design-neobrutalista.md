# CORE-005 — Restyling neobrutalista

- **Area**: core
- **Stato**: fatta (2026-11-17)
- **Priorità**: media
- **Dipende da**: CORE-002 (schermate di accesso), CORE-004 (home)

## Obiettivo

Dare all'app un'identità visiva riconoscibile in stile **neobrutalista** "morbido" (vedi `brain/DESIGN.md`): sfondo
crema, bordi neri spessi, ombre piene senza sfocatura, angoli arrotondati, accenti pastello, pulsanti che si
"premono". Riguarda tutte le schermate esistenti; le nuove schermate useranno lo stesso stile.

## User story

- Come utente voglio un'app con un aspetto allegro e deciso, leggibile al volo dal telefono in palestra.

## Requisiti

Scelte dell'utente (2026-11-17):
- [x] **Palette Coral & Cream**: sfondo `#FAFADF`, superfici `#FFFFFF`, bordi/ombre/testo `#111111`, testo
  secondario `#555555`, primario corallo `#E8635A`; accenti viola `#7B6CF6`, menta `#4ECDC4`, giallo `#FFE566`,
  rosa `#F9A8B8`, lavanda `#C4B5FD`.
- [x] **Tema chiaro e scuro, a scelta dell'utente** (richiesta del 2026-11-17):
  - chiaro = **Coral & Cream** (sopra);
  - scuro = **Dark Brut**: sfondo `#111111`, superfici `#1C1C1C`, bordi/ombre/testo `#FFFFFF`, testo secondario
    `#BBBBBB`, primario giallo `#FFE566`, secondario corallo `#E8635A`, stessi accenti pastello;
  - finché l'utente non sceglie, l'app segue il tema del sistema; uno switch (sole/luna) nell'header della home
    passa da un tema all'altro e la scelta resta salvata sul dispositivo.
- [x] **Font DM Sans** (titoli 700/800, testo 400/500), disponibile anche offline.
- [x] **Decorazioni minime**: al massimo uno o due elementi decorativi (stellina a 4 punte, blob) per schermata, in
  punti che non disturbano il contenuto.

Valori predefiniti dello stile (`brain/DESIGN.md`), modificabili in approvazione:
- [x] Bordi `2px solid #111` su card, pulsanti, campi, barra di navigazione.
- [x] Ombre piene `4px 4px 0 #111` (piccola `3px 3px`, grande `6px 6px`), mai sfocate; usate in modo selettivo
  (card principali con ombra, card secondarie solo bordo).
- [x] Angoli 10–12 px su card e contenitori, pillola sui badge, cerchio sulle icone in contenitore; mai 0 px.
- [x] Pulsanti con effetto pressione: al tocco/click si spostano di 4 px e l'ombra sparisce; in hover 2 px.
- [x] Titoli in minuscolo ("ciao, natalia", "questa settimana").
- [x] Animazioni solo "meccaniche" (pressione dei pulsanti), rispettando `prefers-reduced-motion`.

## Fuori scope

- Scelta del tema salvata sul profilo utente (sincronizzata tra dispositivi).
- Pagina delle impostazioni.
- Icone e manifest definitivi della PWA (oltre ai colori del manifest).
- Nuove schermate o funzionalità.

## Modello dati (bozza)

Nessuno.

## API (bozza)

Nessuna.

## UI

Schermate toccate: accesso (Accedi / Registrati), caricamento, offline, home (header, card calendario, card
segnaposto, barra di navigazione con Start).

## Criteri di accettazione

- [x] Tutte le schermate usano palette, font, bordi, ombre e raggi indicati sopra.
- [x] Lo switch del tema cambia tema; ricaricando l'app il tema scelto resta. Senza una scelta, l'app segue il
  tema del sistema.
- [x] Entrambi i temi rispettano lo stile (bordi, ombre piene, raggi) con la propria palette.
- [x] Il font si vede anche senza connessione a internet (nessuna richiesta a server esterni).
- [x] I pulsanti mostrano l'effetto pressione.
- [x] I testi restano leggibili (contrasto sufficiente) e in vista mobile non c'è scroll orizzontale.

## Domande aperte

Nessuna.

## Issue

| ID | Lato | Stato | File |
|----|------|-------|------|
| CORE-005-FE-01 | frontend | fatta (2026-11-17) | `issue/core-design-neobrutalista/fe-01-tema-neobrutalista.md` |

## Note

- 2026-11-17: il cambio di tema è uno **switch** (non un pulsante icona), su richiesta dell'utente; nel tema scuro
  la voce attiva della barra e la tab selezionata usano la lavanda, perché il giallo è il primario.

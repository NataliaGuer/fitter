# CORE-004 — Home page e navigazione

- **Area**: core
- **Stato**: fatta (2026-11-17)
- **Priorità**: alta
- **Dipende da**: CORE-002 (utente autenticato)

## Obiettivo

Dare all'app una home vera al posto del segnaposto: una dashboard a card che riassume la settimana di allenamento,
le calorie e le statistiche, e una barra di navigazione in basso verso le sezioni principali. Per ora solo la card
del calendario è completa; le altre e la navigazione sono segnaposto da riempire con le feature successive.

## User story

- Come utente voglio vedere a colpo d'occhio la settimana corrente, con il giorno di oggi evidenziato, per
  orientarmi (in futuro: che routine mi aspetta oggi).
- Come utente voglio una barra in basso con le sezioni dell'app, raggiungibile con il pollice, con "Start" ben in
  evidenza perché è l'azione principale in palestra.

## Requisiti

- [x] Home composta da card impilate (mobile-first), in quest'ordine:
  1. **Calendario settimanale**: i 7 giorni della settimana corrente (lunedì → domenica), con giorno della
     settimana abbreviato e numero del giorno; oggi evidenziato; titolo centrato,
     senza mese e anno.
     Struttura pronta per associare in futuro una routine a ogni giorno (per ora nessun dato).
     Si scorrono le settimane precedenti e successive con lo swipe orizzontale sui giorni e con due frecce ai lati
     del titolo. Titolo: "Questa settimana" per la settimana corrente, altrimenti l'intervallo senza anno (es. "9 – 15 nov").
  2. **Calorie**: segnaposto ("In arrivo").
  3. **Statistiche**: segnaposto ("In arrivo").
- [x] Barra di navigazione **floating** in basso (staccata dai bordi, angoli arrotondati) con 5 voci, solo icone
  (nome leggibile dagli screen reader): **Home**, **Plan**, **Start**, **Stats**, **Calories**. "Home" risulta attiva.
- [x] **Start** ha un'enfasi particolare: pulsante centrato nella barra, più grande, rotondo, con il colore primario
  del tema.
- [x] Per ora le voci della barra non fanno nulla (nessuna navigazione).
- [x] Il saluto "Ciao, <nickname>" e il logout restano disponibili nella home (in alto).
- [x] Settimana e "oggi" calcolati sul fuso orario del dispositivo.

## Fuori scope

- Associazione delle routine ai giorni (feature di allenamento futura).
- Contenuto reale delle card Calorie e Statistiche.
- Navigazione tra pagine e router (D-010: con la prima feature a più pagine).
- Nessuna modifica al backend.

## Modello dati (bozza)

Nessuno.

## API (bozza)

Nessuna.

## UI

```
┌──────────────────────────────┐
│ Ciao, natalia          [⎋]   │
│ ┌──────────────────────────┐ │
│ │ Questa settimana         │ │
│ │ novembre 2026            │ │
│ │ lun mar mer gio ven sab dom│
│ │ 16  (17) 18  19  20  21  22│
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ Calorie       In arrivo  │ │
│ └──────────────────────────┘ │
│ ┌──────────────────────────┐ │
│ │ Statistiche   In arrivo  │ │
│ └──────────────────────────┘ │
├──────────────────────────────┤
│   ( ⌂   ☰   (▶)   ▥   🔥 )   │
└──────────────────────────────┘
```

## Criteri di accettazione

- [x] Aprendo l'app autenticati si vede la home con le tre card e la barra in basso.
- [x] Il calendario mostra lun–dom della settimana corrente con oggi evidenziato.
- [x] In vista mobile (375 px) nessuno scroll orizzontale e la barra non copre l'ultima card.
- [x] "Start" è visivamente distinto dalle altre voci.
- [x] Il logout funziona ancora dalla home.

## Domande aperte

Nessuna.

## Issue

| ID | Lato | Stato | File |
|----|------|-------|------|
| CORE-004-FE-01 | frontend | fatta (2026-11-17) | `issue/core-home/fe-01-home-e-navigazione.md` |

## Note

- 2026-11-17, su richiesta dell'utente durante il passo 1: barra floating, solo icone senza etichette, Start
  centrato dentro la barra (non più sollevato).
- 2026-11-17, su richiesta dell'utente durante il passo 2: angoli meno arrotondati per card e barra; nel calendario
  titolo centrato, niente mese/anno e scorrimento delle settimane (prima fuori scope; swipe + frecce, titolo
  "Questa settimana" o intervallo).

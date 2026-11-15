# CORE-002 — Utenti e autenticazione

- **Area**: core
- **Stato**: da definire
- **Priorità**: alta
- **Dipende da**: CORE-001

## Obiettivo

Permettere a più persone di usare l'app, ognuna con i propri dati, con un accesso rapido dal telefono (nickname + PIN di 4 cifre). Vedi D-004 e D-006.

## User story

- Come nuovo utente voglio registrarmi scegliendo un nickname e un PIN, per iniziare subito a usare l'app.
- Come utente voglio accedere con nickname e PIN e restare connesso, per non dover rifare il login ogni volta in palestra.
- Come utente voglio poter uscire (logout).

## Requisiti

- [ ] Registrazione libera: nickname univoco (case-insensitive) e PIN di esattamente 4 cifre numeriche.
- [ ] PIN salvato solo come hash (argon2 o bcrypt).
- [ ] Login → crea una sessione nel DB e imposta un cookie `HttpOnly`, `SameSite=Lax`, `Secure` in prod.
- [ ] Logout → invalida la sessione lato server e cancella il cookie.
- [ ] Dipendenza FastAPI `current_user` per proteggere gli endpoint.
- [ ] **Anti forza bruta**: limite di tentativi falliti per nickname e per IP con blocco temporaneo.
- [ ] Messaggio di errore generico al login (non rivelare se il nickname esiste).

## Fuori scope

- Recupero del PIN dimenticato.
- Ruoli/amministrazione.

## Modello dati (bozza)

- `users`: `id`, `nickname` (unique), `pin_hash`, `created_at`
- `sessions`: `id` (token casuale; salvarne l'hash), `user_id` (FK), `created_at`, `expires_at`, `last_seen_at`
- `login_attempts` (o tabella equivalente per il rate limiting): `nickname`, `ip`, `attempted_at`, `success`

## API (bozza)

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| POST | `/api/auth/register` | Crea utente (nickname, pin) ed effettua il login |
| POST | `/api/auth/login` | Login, imposta il cookie di sessione |
| POST | `/api/auth/logout` | Invalida la sessione |
| GET  | `/api/auth/me` | Utente corrente (401 se non autenticato) |

## UI

- Schermata di accesso con due modalità: "Accedi" / "Registrati".
- Input del PIN con tastierino numerico (`inputmode="numeric"`) e 4 caselle.

## Criteri di accettazione

- [ ] Non si possono registrare due utenti con lo stesso nickname (nemmeno con maiuscole o minuscole diverse).
- [ ] Un PIN diverso da 4 cifre numeriche viene rifiutato.
- [ ] Dopo N tentativi falliti il login viene bloccato temporaneamente.
- [ ] Gli endpoint protetti rispondono 401 senza una sessione valida.
- [ ] Dopo il logout il vecchio cookie non dà più accesso.

## Domande aperte

- Durata della sessione (es. 30 giorni, rinnovata a ogni uso)?
- Soglie del blocco (es. 5 tentativi → blocco di 15 minuti)?
- Il proxy davanti al Raspberry Pi inoltra l'IP reale (`X-Forwarded-For`)? Serve per il limite per IP.
- Il PIN si può cambiare dalle impostazioni?

## Piano tecnico

- **Stato piano**: da redigere (prima dell'implementazione)

## Note di implementazione

Da compilare durante/dopo lo sviluppo.

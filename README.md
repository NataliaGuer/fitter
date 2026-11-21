# Fitter

Web app (PWA) personale per l'allenamento in palestra e il tracciamento delle calorie, pensata per girare su un
Raspberry Pi.

- Backend: Python, FastAPI, SQLite (`backend/`)
- Frontend: React, TypeScript, Vite, HeroUI (`frontend/`)
- Documentazione di feature, issue e decisioni: [`brain/`](brain/README.md)
- Deploy sul Raspberry Pi: [`deploy/`](deploy/README.md)

## Sviluppo

```bash
./script/start-dev.sh   # backend su :8000 (reload), frontend su :5173
```

## Crediti

Exercise data by [RepDB](https://repdb.co)

Il catalogo degli esercizi (dati e immagini) viene dal pacchetto npm
[`@repdb/exercises`](https://www.npmjs.com/package/@repdb/exercises), usato secondo la sua licenza (file
`LICENSE.md` del pacchetto). Il dataset non è contenuto in questo repo: viene installato come dipendenza e
copiato nell'immagine Docker durante la build.

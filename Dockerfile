# ---------- Frontend ----------
FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY ./frontend/package*.json /frontend/
RUN npm ci
COPY ./frontend /frontend

# per ambiente di sviluppo usiamo due container separati
FROM frontend AS frontend-dev
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

FROM frontend AS frontend-build
RUN npm run build

# ---------- Backend ----------
FROM python:3.14 AS backend
WORKDIR /backend
COPY ./backend/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt
COPY ./backend/alembic.ini /backend/alembic.ini
COPY ./backend/alembic /backend/alembic
COPY ./backend/app /backend/app

# Migrazioni applicate a ogni avvio del container (D-003, D-009)
FROM backend AS dev
COPY ./backend/requirements-dev.txt /backend/requirements-dev.txt
RUN pip install --no-cache-dir -r /backend/requirements-dev.txt
COPY ./backend/tests /backend/tests
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]

FROM backend AS prod
COPY --from=frontend-build /frontend/dist /backend/static
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]

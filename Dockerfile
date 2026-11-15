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
COPY ./backend/app /backend/app

FROM backend AS dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM backend AS prod
COPY --from=frontend-build /frontend/dist /backend/static
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

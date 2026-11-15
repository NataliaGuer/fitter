from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router

app = FastAPI(title="Fitter")

# API routers must be registered before the StaticFiles mount.
app.include_router(auth_router, prefix="/api/auth")

# In prod the frontend build is copied into /backend/static (see Dockerfile)
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")

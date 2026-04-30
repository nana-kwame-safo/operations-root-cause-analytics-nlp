"""FastAPI application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.constants import APP_FULL_NAME, APP_SUBTITLE
from app.core.config import get_settings

settings = get_settings()
app = FastAPI(
    title=APP_FULL_NAME,
    version=settings.app_version,
    description=(
        f"{APP_SUBTITLE}. Operations intelligence API for root cause analysis "
        "support with confidence-aware analyst review workflows."
    ),
)

app.include_router(router)

BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"
STATIC_DIR = BASE_DIR / "static"

if UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=str(UI_DIR)), name="ui")
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(UI_DIR / "index.html")

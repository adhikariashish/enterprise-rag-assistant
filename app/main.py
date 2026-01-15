# app/main.py
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.logging import setup_logging

settings = get_settings()

try:
    setup_logging(settings.app.log_level)
except Exception:
    logging.basicConfig(
        level=getattr(logging, settings.app.log_level.upper(), logging.INFO)
    )

logger = logging.getLogger("app.main")

app = FastAPI(title=settings.app.app_name, version="1.0.0")

# --- API routers ---
from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router

app.include_router(health_router)
app.include_router(chat_router)

# ---  UI (root/ui) ---
REPO_ROOT = Path(__file__).resolve().parents[1]   # app/ -> repo root
UI_DIR = REPO_ROOT / "ui"

app.mount("/ui", StaticFiles(directory=UI_DIR, html=True), name="ui")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/ui/")


@app.on_event("startup")
def _startup():
    logger.info(
        "App started: %s | log_level=%s | llm=%s | embedder=%s",
        settings.app.app_name,
        settings.app.log_level,
        settings.providers.llm,
        settings.providers.embedder,
    )

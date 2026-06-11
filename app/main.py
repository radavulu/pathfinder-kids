"""FastAPI app: serves the kid + parent web UIs and the JSON API."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import config, db
from .routes import register_routes

app = FastAPI(title="PathfinderKids", version="1.0.0")


@app.on_event("startup")
def _startup() -> None:
    config.ensure_data_dir()
    db.init_db()


register_routes(app)

# Mount static assets last so they don't shadow API routes.
app.mount("/static", StaticFiles(directory=str(config.WEB_DIR / "static")), name="static")

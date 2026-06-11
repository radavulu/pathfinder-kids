from fastapi import FastAPI

from . import children, health, kid, pages, parent


def register_routes(app: FastAPI) -> None:
    app.include_router(health.router)
    app.include_router(pages.router)
    app.include_router(children.router)
    app.include_router(kid.router)
    app.include_router(parent.router)

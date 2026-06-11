from fastapi import APIRouter
from fastapi.responses import FileResponse

from .. import config

router = APIRouter(tags=["pages"])


@router.get("/")
def index() -> FileResponse:
    return FileResponse(config.WEB_DIR / "index.html")


@router.get("/kid")
def kid_page() -> FileResponse:
    return FileResponse(config.WEB_DIR / "kid.html")


@router.get("/parent")
def parent_page() -> FileResponse:
    return FileResponse(config.WEB_DIR / "parent.html")

from fastapi import APIRouter

from .. import db
from ..services.children import child_public

router = APIRouter(prefix="/api", tags=["children"])


@router.get("/children")
def list_children() -> dict:
    conn = db.get_conn()
    try:
        rows = conn.execute("SELECT * FROM children ORDER BY id").fetchall()
        return {"children": [child_public(conn, r) for r in rows], "mascot": db.get_setting("mascot")}
    finally:
        conn.close()

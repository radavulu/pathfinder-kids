"""Child profile helpers."""
from __future__ import annotations

import sqlite3

from fastapi import HTTPException

from .. import curriculum, db, leveling, rewards


def child_or_404(conn: sqlite3.Connection, child_id: int):
    row = conn.execute("SELECT * FROM children WHERE id=?", (child_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Child not found")
    return row


def child_public(conn: sqlite3.Connection, row) -> dict:
    levels = {s: leveling.get_level(conn, row["id"], s) for s in curriculum.SUBJECTS}
    return {
        "id": row["id"],
        "name": row["name"],
        "age": row["age"],
        "palette": row["palette_name"],
        "theme": {
            "primary": row["color_primary"],
            "accent": row["color_accent"],
            "bg": row["color_bg"],
        },
        "stars": row["stars"],
        "streak": row["streak"],
        "levels": levels,
        "skills": {s: curriculum.skill_for(s, lv) for s, lv in levels.items()},
        "badges": rewards.list_badges(conn, row["id"]),
    }

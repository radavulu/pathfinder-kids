"""Parent-initiated reset of kid progress (for testing)."""
from __future__ import annotations

import sqlite3

from .. import content, curriculum, db, leveling


def _seed_levels_for_child(conn: sqlite3.Connection, child_id: int, name: str, age: int) -> None:
    profile = next((p for p in curriculum.NAMED_PROFILES if p["name"] == name), None)
    for subject in curriculum.SUBJECTS:
        if profile and "levels" in profile:
            level = profile["levels"].get(subject, curriculum.start_level(subject, age))
        else:
            level = curriculum.start_level(subject, age)
        leveling.set_level(conn, child_id, subject, level)


def reset_today(conn: sqlite3.Connection, child_id: int, *, regenerate: bool = True) -> dict:
    """Clear today's answers, sessions, and problems; optionally generate fresh sets."""
    day = db.today_str()

    def _clear() -> dict:
        answers = conn.execute(
            "DELETE FROM answers WHERE child_id=? AND day=?", (child_id, day),
        ).rowcount
        sessions = conn.execute(
            "DELETE FROM sessions WHERE child_id=? AND day=?", (child_id, day),
        ).rowcount
        problems = conn.execute(
            "DELETE FROM problems WHERE child_id=? AND day=?", (child_id, day),
        ).rowcount
        return {"answers": answers, "sessions": sessions, "problems": problems}

    removed = db.run_immediate(conn, _clear)
    regen = content.refresh_day(conn, child_id, day) if regenerate else None
    return {
        "scope": "today",
        "day": day,
        "removed": removed,
        "regenerated": regen,
    }


def reset_all(conn: sqlite3.Connection, child_id: int, *, regenerate: bool = True) -> dict:
    """Clear all progress for one child and restore default levels."""
    row = conn.execute("SELECT name, age FROM children WHERE id=?", (child_id,)).fetchone()
    if not row:
        raise ValueError("Child not found")
    profile = next((p for p in curriculum.NAMED_PROFILES if p["name"] == row["name"]), None)
    age = profile["age"] if profile else row["age"]

    def _clear() -> dict:
        if profile:
            conn.execute(
                "UPDATE children SET age=?, stars=0, streak=0, last_active=NULL WHERE id=?",
                (age, child_id),
            )
        else:
            conn.execute(
                "UPDATE children SET stars=0, streak=0, last_active=NULL WHERE id=?",
                (child_id,),
            )
        answers = conn.execute("DELETE FROM answers WHERE child_id=?", (child_id,)).rowcount
        sessions = conn.execute("DELETE FROM sessions WHERE child_id=?", (child_id,)).rowcount
        problems = conn.execute("DELETE FROM problems WHERE child_id=?", (child_id,)).rowcount
        badges = conn.execute("DELETE FROM badges WHERE child_id=?", (child_id,)).rowcount
        _seed_levels_for_child(conn, child_id, row["name"], age)
        return {
            "answers": answers,
            "sessions": sessions,
            "problems": problems,
            "badges": badges,
        }

    removed = db.run_immediate(conn, _clear)
    regen = content.refresh_day(conn, child_id, db.today_str()) if regenerate else None
    return {
        "scope": "all",
        "removed": removed,
        "regenerated": regen,
        "levels": {s: leveling.get_level(conn, child_id, s) for s in curriculum.SUBJECTS},
    }

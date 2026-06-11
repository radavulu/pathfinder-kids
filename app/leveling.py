"""Adaptive, forgiving leveling.

Per subject, independently: when a child finishes a subject for the day with
>= LEVEL_UP_THRESHOLD accuracy, they move up one rung. They are never moved down
(a weak day simply holds the level).
"""
from __future__ import annotations

import sqlite3

from . import curriculum

LEVEL_UP_THRESHOLD = 0.80


def session_stats(conn: sqlite3.Connection, child_id: int, subject: str, day: str) -> dict:
    rows = conn.execute(
        "SELECT correct FROM answers WHERE child_id = ? AND subject = ? AND day = ?",
        (child_id, subject, day),
    ).fetchall()
    total = len(rows)
    correct = sum(r["correct"] for r in rows)
    accuracy = (correct / total) if total else 0.0
    return {"total": total, "correct": correct, "accuracy": accuracy}


def get_level(conn: sqlite3.Connection, child_id: int, subject: str) -> int:
    row = conn.execute(
        "SELECT level FROM child_levels WHERE child_id = ? AND subject = ?",
        (child_id, subject),
    ).fetchone()
    return row["level"] if row else 1


def set_level(conn: sqlite3.Connection, child_id: int, subject: str, level: int) -> None:
    level = curriculum.clamp_level(subject, level)
    conn.execute(
        "INSERT INTO child_levels(child_id, subject, level) VALUES(?, ?, ?) "
        "ON CONFLICT(child_id, subject) DO UPDATE SET level = excluded.level",
        (child_id, subject, level),
    )


def adjust_level(conn: sqlite3.Connection, child_id: int, subject: str, delta: int) -> dict:
    """Move a child up or down one or more rungs (parent or kid-initiated)."""
    old = get_level(conn, child_id, subject)
    new = curriculum.clamp_level(subject, old + delta)
    if new != old:
        set_level(conn, child_id, subject, new)
    return {
        "subject": subject,
        "old_level": old,
        "new_level": new,
        "changed": new != old,
        "old_skill": curriculum.skill_for(subject, old),
        "new_skill": curriculum.skill_for(subject, new),
        "max_level": len(curriculum.LADDERS[subject]),
    }


def apply_leveling(conn: sqlite3.Connection, child_id: int, subject: str, day: str) -> dict:
    """Evaluate today's subject session and bump the level if earned. Never demotes."""
    stats = session_stats(conn, child_id, subject, day)
    old = get_level(conn, child_id, subject)
    new = old
    leveled_up = False
    if stats["total"] >= 3 and stats["accuracy"] >= LEVEL_UP_THRESHOLD:
        new = curriculum.clamp_level(subject, old + 1)
        if new != old:
            set_level(conn, child_id, subject, new)
            leveled_up = True
    return {
        "subject": subject,
        "old_level": old,
        "new_level": new,
        "leveled_up": leveled_up,
        "accuracy": round(stats["accuracy"], 3),
        "total": stats["total"],
        "correct": stats["correct"],
        "old_skill": curriculum.skill_for(subject, old),
        "new_skill": curriculum.skill_for(subject, new),
    }

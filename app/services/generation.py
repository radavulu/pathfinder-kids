"""Worksheet generation and level-adjustment orchestration."""
from __future__ import annotations

import sqlite3
import time

from .. import content, db, leveling
from .children import child_or_404


def target_child_ids(conn: sqlite3.Connection, child_id: int | None) -> list[int]:
    if child_id is not None:
        return [child_id]
    rows = conn.execute("SELECT id FROM children ORDER BY id").fetchall()
    return [r["id"] for r in rows]


def run_generation(
    conn: sqlite3.Connection,
    day: str,
    targets: list[int],
    *,
    refresh: bool,
) -> dict:
    t0 = time.time()
    results = {}
    for cid in targets:
        if refresh:
            results[cid] = content.refresh_day(conn, cid, day)
        else:
            results[cid] = content.prepare_day(conn, cid, day)
    conn.commit()
    return {
        "day": day,
        "refresh": refresh,
        "elapsed_seconds": round(time.time() - t0, 1),
        "results": results,
    }


def regenerate_after_level_change(
    conn: sqlite3.Connection,
    child_id: int,
    subject: str,
    result: dict,
) -> None:
    if result.get("changed"):
        result["regenerated"] = content.regenerate_subject_today(
            conn, child_id, subject, db.today_str(),
        )


def adjust_level(conn: sqlite3.Connection, child_id: int, subject: str, delta: int) -> dict:
    child_or_404(conn, child_id)
    result = leveling.adjust_level(conn, child_id, subject, delta)
    regenerate_after_level_change(conn, child_id, subject, result)
    conn.commit()
    return result

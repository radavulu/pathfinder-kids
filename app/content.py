"""Content lifecycle: generate (LM Studio), fall back to an offline starter bank,
store, and serve problems for a child's daily session.
"""
from __future__ import annotations

import json
import sqlite3

from . import curriculum, db, leveling, lmstudio
from .starter_bank import starter_batch


def _batch_size(conn: sqlite3.Connection | None = None) -> int:
    try:
        raw = db.get_setting("batch_size", conn=conn) or "20"
        return int(raw)
    except ValueError:
        return 20


def _first_fetch_size(subject: str, conn: sqlite3.Connection | None = None) -> int:
    """Small first batch for reading/logic so kids don't wait for 20 LM problems."""
    if subject == "math":
        return _batch_size(conn)
    return min(5, _batch_size(conn))


def _top_up_threshold() -> int:
    return 5


def _insert_problems(conn, child_id, day, subject, level, problems, *, commit: bool = True) -> int:
    for p in problems:
        conn.execute(
            """INSERT INTO problems(child_id, day, subject, level, ptype, prompt, options,
                                    answer, explanation, hint, skill, source)
               VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                child_id, day, subject, level, p["type"], p["prompt"],
                json.dumps(p["options"]) if p.get("options") else None,
                p["answer"], p["explanation"], p["hint"], p["skill"], p["source"],
            ),
        )
    if commit:
        conn.commit()
    return len(problems)


def generate_batch(conn, child_id: int, subject: str, day: str, count: int | None = None) -> dict:
    """Generate a batch for one subject. Tries LM Studio, falls back to the starter bank."""
    count = count or _batch_size(conn)
    level = leveling.get_level(conn, child_id, subject)
    seed = hash((child_id, subject, day, level)) & 0xFFFFFFFF

    # Math is generated deterministically so the answer keys are always correct
    # (no reliance on the model getting arithmetic right). Reading/Logic use LM Studio.
    if subject == "math":
        problems = starter_batch(subject, level, count, seed)
        source = "computed"
    else:
        source = "lmstudio"
        try:
            problems = lmstudio.generate_problems(subject, level, count)
        except Exception:  # noqa: BLE001 - offline / model error -> starter bank
            problems = starter_batch(subject, level, count, seed)
            source = "starter"
        if len(problems) < count:
            problems.extend(starter_batch(subject, level, count - len(problems), seed + 1))
            if source == "lmstudio":
                source = "lmstudio+starter"
    inserted = _insert_problems(conn, child_id, day, subject, level, problems)
    return {"subject": subject, "level": level, "inserted": inserted, "source": source}


def unserved_count(conn, child_id: int, subject: str, day: str) -> int:
    return conn.execute(
        "SELECT COUNT(*) AS c FROM problems WHERE child_id=? AND subject=? AND day=? AND served=0",
        (child_id, subject, day),
    ).fetchone()["c"]


def _stale_unserved_count(conn, child_id: int, subject: str, day: str) -> int:
    """Unserved problems generated at a different level than the child is on now."""
    level = leveling.get_level(conn, child_id, subject)
    return conn.execute(
        """SELECT COUNT(*) AS c FROM problems
           WHERE child_id=? AND subject=? AND day=? AND served=0 AND level != ?""",
        (child_id, subject, day, level),
    ).fetchone()["c"]


def sync_problems_to_level(conn, child_id: int, subject: str, day: str) -> dict | None:
    """Replace today's unserved queue when it no longer matches the child's level."""
    if _stale_unserved_count(conn, child_id, subject, day) <= 0:
        return None
    return regenerate_subject_today(conn, child_id, subject, day)


def ensure_set(conn, child_id: int, subject: str, day: str) -> str | None:
    """Make sure at least a few unserved problems exist for this subject/day. Returns source if generated."""
    sync_problems_to_level(conn, child_id, subject, day)
    if unserved_count(conn, child_id, subject, day) >= 1:
        return None
    return generate_batch(conn, child_id, subject, day, count=_first_fetch_size(subject, conn))["source"]


def _top_up_queue(conn, child_id: int, subject: str, day: str) -> None:
    """Background-fill the queue when running low (best-effort; ignores LM errors)."""
    have = unserved_count(conn, child_id, subject, day)
    target = _batch_size(conn)
    if have >= _top_up_threshold():
        return
    need = target - have
    if need <= 0:
        return
    try:
        generate_batch(conn, child_id, subject, day, count=need)
    except Exception:  # noqa: BLE001
        pass


def next_problem(conn, child_id: int, subject: str, day: str) -> dict | None:
    """Atomically claim the next unserved problem (safe for two browsers at once)."""
    for _ in range(8):
        ensure_set(conn, child_id, subject, day)
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute(
                """SELECT * FROM problems
                   WHERE child_id=? AND subject=? AND day=? AND served=0
                   ORDER BY id LIMIT 1""",
                (child_id, subject, day),
            ).fetchone()
            if not row:
                conn.execute("ROLLBACK")
                return None
            claimed = conn.execute(
                "UPDATE problems SET served=1 WHERE id=? AND served=0",
                (row["id"],),
            ).rowcount
            if not claimed:
                conn.execute("ROLLBACK")
                continue
            conn.commit()
            _top_up_queue(conn, child_id, subject, day)
            return {
                "problem_id": row["id"],
                "subject": subject,
                "type": row["ptype"],
                "prompt": row["prompt"],
                "options": json.loads(row["options"]) if row["options"] else None,
                "level": row["level"],
                "skill": row["skill"],
                "source": row["source"],
            }
        except sqlite3.OperationalError:
            conn.execute("ROLLBACK")
            continue
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return None


def _clear_unserved(conn, child_id: int, subject: str, day: str) -> int:
    return conn.execute(
        "DELETE FROM problems WHERE child_id=? AND subject=? AND day=? AND served=0",
        (child_id, subject, day),
    ).rowcount


def _refresh_subject(conn, child_id: int, subject: str, day: str) -> dict:
    removed = _clear_unserved(conn, child_id, subject, day)
    batch = generate_batch(conn, child_id, subject, day, count=_batch_size(conn))
    batch["removed_unserved"] = removed
    return batch


def prepare_day(conn, child_id: int, day: str) -> list[dict]:
    """Top up every subject to a full batch for the given day."""
    results = []
    target = _batch_size(conn)
    for subject in curriculum.SUBJECTS:
        have = unserved_count(conn, child_id, subject, day)
        if have >= target:
            level = leveling.get_level(conn, child_id, subject)
            results.append({"subject": subject, "inserted": 0, "source": "existing", "level": level})
        else:
            results.append(generate_batch(conn, child_id, subject, day, count=target - have))
    return results


def refresh_day(conn, child_id: int, day: str) -> list[dict]:
    """Replace today's unserved problems with fresh batches at current levels."""
    return [_refresh_subject(conn, child_id, subject, day) for subject in curriculum.SUBJECTS]


def regenerate_subject_today(conn, child_id: int, subject: str, day: str) -> dict:
    """Refresh one subject after difficulty is lowered; keeps served problems and history."""
    return _refresh_subject(conn, child_id, subject, day)

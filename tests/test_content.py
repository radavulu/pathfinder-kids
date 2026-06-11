"""Tests for content leveling sync and concurrent problem claims."""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path

import pytest

from app import content, curriculum, db, leveling


@pytest.fixture()
def mem_db(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db.config, "DB_PATH", db_path)
    monkeypatch.setattr(db.config, "DATA_DIR", tmp_path)

    def _fast_gen(subject: str, level: int, count: int):
        from app.starter_bank import starter_batch
        return starter_batch(subject, level, count, 99)

    monkeypatch.setattr("app.content.lmstudio.generate_problems", _fast_gen)
    db.init_db()
    conn = db.get_conn()
    row = conn.execute("SELECT id FROM children LIMIT 1").fetchone()
    yield conn, row["id"]
    conn.close()


def test_sync_refreshes_stale_reading_queue(mem_db):
    conn, child_id = mem_db
    day = db.today_str()
    conn.execute(
        """INSERT INTO problems(child_id, day, subject, level, ptype, prompt, options,
                               answer, explanation, hint, skill, source, served)
           VALUES(?, ?, 'reading', 2, 'multiple_choice', 'Q?', '["a","b"]', 'a', 'e', 'h', 'old', 'test', 0)""",
        (child_id, day),
    )
    conn.commit()
    leveling.set_level(conn, child_id, "reading", 8)
    conn.commit()
    regen = content.sync_problems_to_level(conn, child_id, "reading", day)
    assert regen is not None
    row = conn.execute(
        "SELECT level FROM problems WHERE child_id=? AND subject='reading' AND day=? AND served=0",
        (child_id, day),
    ).fetchone()
    assert row["level"] == 8


def test_concurrent_next_problem_claims(mem_db):
    conn, child_id = mem_db
    day = db.today_str()
    content.generate_batch(conn, child_id, "logic", day, count=10)
    ids: list[int] = []
    errors: list[Exception] = []

    def worker():
        c = db.get_conn()
        try:
            for _ in range(5):
                p = content.next_problem(c, child_id, "logic", day)
                if p:
                    ids.append(p["problem_id"])
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)
        finally:
            c.close()

    threads = [threading.Thread(target=worker) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)
    assert not errors
    assert len(ids) == len(set(ids)), "two sessions must not get the same problem"


def test_reset_today_clears_and_regenerates(mem_db):
    conn, child_id = mem_db
    day = db.today_str()
    content.generate_batch(conn, child_id, "math", day, count=5)
    conn.execute(
        """INSERT INTO answers(child_id, problem_id, day, subject, level, given, correct, attempts)
           SELECT ?, id, day, subject, level, '1', 1, 1 FROM problems WHERE child_id=? LIMIT 1""",
        (child_id, child_id),
    )
    conn.commit()
    from app.services import reset as reset_svc
    result = reset_svc.reset_today(conn, child_id, regenerate=True)
    assert result["removed"]["answers"] >= 1
    assert conn.execute("SELECT COUNT(*) c FROM answers WHERE child_id=? AND day=?", (child_id, day)).fetchone()["c"] == 0
    assert content.unserved_count(conn, child_id, "math", day) > 0


def test_reset_all_under_concurrent_claims(mem_db):
    conn, child_id = mem_db
    day = db.today_str()
    content.generate_batch(conn, child_id, "math", day, count=10)
    errors: list[Exception] = []
    reset_ok: list[dict] = []

    def kid_worker() -> None:
        c = db.get_conn()
        try:
            for _ in range(30):
                content.next_problem(c, child_id, "math", day)
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)
        finally:
            c.close()

    def reset_worker() -> None:
        c = db.get_conn()
        try:
            from app.services import reset as reset_svc
            reset_ok.append(reset_svc.reset_all(c, child_id, regenerate=True))
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)
        finally:
            c.close()

    threads = [threading.Thread(target=kid_worker), threading.Thread(target=reset_worker)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=90)
    assert not errors, errors
    assert reset_ok
    assert reset_ok[0]["scope"] == "all"

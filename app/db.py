"""SQLite storage: schema, connection helpers, and first-run seeding."""
from __future__ import annotations

import sqlite3
import time
from datetime import date
from typing import Any, Callable, TypeVar

from . import config, curriculum, theming

T = TypeVar("T")

SCHEMA = """
CREATE TABLE IF NOT EXISTS children (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    age           INTEGER NOT NULL,
    palette_name  TEXT NOT NULL,
    color_primary TEXT NOT NULL,
    color_accent  TEXT NOT NULL,
    color_bg      TEXT NOT NULL,
    stars         INTEGER NOT NULL DEFAULT 0,
    streak        INTEGER NOT NULL DEFAULT 0,
    last_active   TEXT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS child_levels (
    child_id INTEGER NOT NULL,
    subject  TEXT NOT NULL,
    level    INTEGER NOT NULL,
    UNIQUE(child_id, subject)
);

CREATE TABLE IF NOT EXISTS time_targets (
    child_id INTEGER NOT NULL,
    subject  TEXT NOT NULL,
    minutes  INTEGER NOT NULL,
    UNIQUE(child_id, subject)
);

CREATE TABLE IF NOT EXISTS problems (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id    INTEGER NOT NULL,
    day         TEXT NOT NULL,
    subject     TEXT NOT NULL,
    level       INTEGER NOT NULL,
    ptype       TEXT NOT NULL,
    prompt      TEXT NOT NULL,
    options     TEXT,                       -- JSON array for multiple choice
    answer      TEXT NOT NULL,
    explanation TEXT NOT NULL,
    hint        TEXT NOT NULL,
    skill       TEXT NOT NULL,
    source      TEXT NOT NULL DEFAULT 'lmstudio',
    served      INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS answers (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id   INTEGER NOT NULL,
    problem_id INTEGER NOT NULL,
    day        TEXT NOT NULL,
    subject    TEXT NOT NULL,
    level      INTEGER NOT NULL,
    given      TEXT,
    correct    INTEGER NOT NULL,
    attempts   INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS badges (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id   INTEGER NOT NULL,
    badge      TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(child_id, badge)
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id   INTEGER NOT NULL,
    day        TEXT NOT NULL,
    subject    TEXT NOT NULL,
    seconds    INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_problems_lookup ON problems(child_id, day, subject, served);
CREATE INDEX IF NOT EXISTS idx_answers_lookup  ON answers(child_id, day, subject);
CREATE INDEX IF NOT EXISTS idx_sessions_lookup ON sessions(child_id, day, subject);
"""


def get_conn() -> sqlite3.Connection:
    config.ensure_data_dir()
    conn = sqlite3.connect(
        config.DB_PATH,
        timeout=60.0,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 60000;")
    mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
    if str(mode).lower() != "wal":
        conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def _is_locked_error(exc: BaseException) -> bool:
    msg = str(exc).lower()
    return "database is locked" in msg or "database is busy" in msg


def run_immediate(conn: sqlite3.Connection, fn: Callable[[], T], *, attempts: int = 15) -> T:
    """Run *fn* inside BEGIN IMMEDIATE, retrying when another session holds the DB."""
    last_err: sqlite3.OperationalError | None = None
    for attempt in range(attempts):
        try:
            conn.execute("BEGIN IMMEDIATE")
            try:
                result = fn()
                conn.commit()
                return result
            except Exception:
                conn.rollback()
                raise
        except sqlite3.OperationalError as exc:
            last_err = exc
            if not _is_locked_error(exc):
                raise
            try:
                conn.rollback()
            except sqlite3.OperationalError:
                pass
            time.sleep(0.05 * (attempt + 1))
    assert last_err is not None
    raise last_err


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        _seed_settings(conn)
        _seed_children(conn)
        _sync_named_profiles(conn)
    finally:
        conn.close()


def _seed_settings(conn: sqlite3.Connection) -> None:
    defaults = {
        "lmstudio_url": config.DEFAULT_LMSTUDIO_URL,
        "lmstudio_model": config.DEFAULT_LMSTUDIO_MODEL,
        "batch_size": "20",
        "mascot": "Sparky the Star",
    }
    for key, value in defaults.items():
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO NOTHING",
            (key, value),
        )
    conn.commit()


def _seed_children(conn: sqlite3.Connection) -> None:
    existing = conn.execute("SELECT COUNT(*) AS c FROM children").fetchone()["c"]
    if existing:
        return
    for prof in curriculum.NAMED_PROFILES:
        name, age, seed_index = prof["name"], prof["age"], prof["seed_index"]
        theme = theming.theme_for(name, seed_index=seed_index)
        cur = conn.execute(
            """INSERT INTO children(name, age, palette_name, color_primary, color_accent, color_bg)
               VALUES(?, ?, ?, ?, ?, ?)""",
            (name, age, theme["name"], theme["primary"], theme["accent"], theme["bg"]),
        )
        child_id = cur.lastrowid
        for subject in curriculum.SUBJECTS:
            level = prof["levels"].get(subject, curriculum.start_level(subject, age))
            conn.execute(
                "INSERT INTO child_levels(child_id, subject, level) VALUES(?, ?, ?)",
                (child_id, subject, curriculum.clamp_level(subject, level)),
            )
            conn.execute(
                "INSERT INTO time_targets(child_id, subject, minutes) VALUES(?, ?, ?)",
                (child_id, subject, 15),
            )
    conn.commit()


def _sync_named_profiles(conn: sqlite3.Connection) -> None:
    """Keep seeded Nyra/Nivi ages and minimum math levels aligned with curriculum defaults."""
    for prof in curriculum.NAMED_PROFILES:
        row = conn.execute("SELECT id FROM children WHERE name=?", (prof["name"],)).fetchone()
        if not row:
            continue
        child_id = row["id"]
        conn.execute("UPDATE children SET age=? WHERE id=?", (prof["age"], child_id))
        target_math = curriculum.clamp_level("math", prof["levels"].get("math", 1))
        current = conn.execute(
            "SELECT level FROM child_levels WHERE child_id=? AND subject='math'",
            (child_id,),
        ).fetchone()
        if current and current["level"] < target_math:
            conn.execute(
                "UPDATE child_levels SET level=? WHERE child_id=? AND subject='math'",
                (target_math, child_id),
            )
    conn.commit()


# --- settings helpers ---

def get_setting(key: str, default: str | None = None, conn: sqlite3.Connection | None = None) -> str | None:
    if conn is not None:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
    c = get_conn()
    try:
        row = c.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        c.close()


def set_setting(key: str, value: str) -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()


def today_str() -> str:
    return date.today().isoformat()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    return dict(row) if row is not None else None

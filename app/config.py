"""Runtime configuration.

Progress is stored in SQLite under ./data next to the app by default.
Override with HOMEKUMON_DATA_DIR (see .env.example). Live LM Studio settings
live in the DB, not here.
"""
from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = PROJECT_ROOT / "web"

# --- LM Studio defaults (can be changed live in the Parent dashboard) ---
DEFAULT_LMSTUDIO_URL = os.environ.get("HOMEKUMON_LMSTUDIO_URL", "http://localhost:1234/v1")
DEFAULT_LMSTUDIO_MODEL = os.environ.get("HOMEKUMON_LMSTUDIO_MODEL", "")  # "" = auto-detect

HOST = os.environ.get("HOMEKUMON_HOST", "127.0.0.1")
DEFAULT_PORT = 8700
PORT = int(os.environ.get("HOMEKUMON_PORT", str(DEFAULT_PORT)))


def detect_data_dir() -> tuple[Path, str]:
    """Return (data_dir, source_label).

    Priority: HOMEKUMON_DATA_DIR env override > ./data next to the app.
    """
    override = os.environ.get("HOMEKUMON_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve(), "env override (HOMEKUMON_DATA_DIR)"
    local = (PROJECT_ROOT / "data").resolve()
    return local, "local app folder (./data)"


DATA_DIR, DATA_DIR_SOURCE = detect_data_dir()
DB_PATH = DATA_DIR / "homekumon.db"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

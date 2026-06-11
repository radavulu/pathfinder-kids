from datetime import date, timedelta

import sqlite3

from fastapi import APIRouter, HTTPException

from .. import config, content, curriculum, db, leveling, lmstudio, theming
from ..schemas import LevelAdjustIn, LMStudioIn, MascotIn, SettingsIn
from ..services.children import child_or_404, child_public
from ..services.generation import adjust_level, run_generation, target_child_ids
from ..services import reset as reset_svc

router = APIRouter(prefix="/api/parent", tags=["parent"])


@router.get("/overview")
def parent_overview() -> dict:
    conn = db.get_conn()
    try:
        day = db.today_str()
        rows = conn.execute("SELECT * FROM children ORDER BY id").fetchall()
        kids = []
        for r in rows:
            pub = child_public(conn, r)
            per_subject = []
            for s in curriculum.SUBJECTS:
                allt = conn.execute(
                    "SELECT COUNT(*) c, COALESCE(SUM(correct),0) ok FROM answers WHERE child_id=? AND subject=?",
                    (r["id"], s),
                ).fetchone()
                today = leveling.session_stats(conn, r["id"], s, day)
                tt = conn.execute(
                    "SELECT minutes FROM time_targets WHERE child_id=? AND subject=?",
                    (r["id"], s),
                ).fetchone()
                secs = conn.execute(
                    "SELECT COALESCE(SUM(seconds),0) s FROM sessions WHERE child_id=? AND subject=?",
                    (r["id"], s),
                ).fetchone()["s"]
                secs_today = conn.execute(
                    "SELECT COALESCE(SUM(seconds),0) s FROM sessions WHERE child_id=? AND subject=? AND day=?",
                    (r["id"], s, day),
                ).fetchone()["s"]
                per_subject.append({
                    "subject": s,
                    "label": curriculum.SUBJECTS[s]["label"],
                    "level": pub["levels"][s],
                    "skill": pub["skills"][s],
                    "max_level": len(curriculum.LADDERS[s]),
                    "minutes": tt["minutes"] if tt else 15,
                    "total_answered": allt["c"],
                    "total_correct": allt["ok"],
                    "accuracy": round((allt["ok"] / allt["c"]) if allt["c"] else 0.0, 3),
                    "today_answered": today["total"],
                    "minutes_spent_total": round(secs / 60),
                    "minutes_spent_today": round(secs_today / 60),
                })
            pub["subjects"] = per_subject
            kids.append(pub)
        return {
            "children": kids,
            "day": day,
            "mascot": db.get_setting("mascot"),
            "data_dir": str(config.DATA_DIR),
            "data_dir_source": config.DATA_DIR_SOURCE,
        }
    finally:
        conn.close()


@router.get("/{child_id}/history")
def parent_history(child_id: int, limit: int = 50) -> dict:
    conn = db.get_conn()
    try:
        child_or_404(conn, child_id)
        rows = conn.execute(
            """SELECT a.created_at, a.subject, a.given, a.correct, a.attempts, p.prompt, p.answer, p.skill
               FROM answers a JOIN problems p ON p.id = a.problem_id
               WHERE a.child_id=? ORDER BY a.id DESC LIMIT ?""",
            (child_id, limit),
        ).fetchall()
        return {"history": [dict(r) for r in rows]}
    finally:
        conn.close()


@router.post("/{child_id}/adjust-level")
def parent_adjust_level(child_id: int, body: LevelAdjustIn) -> dict:
    if body.subject not in curriculum.SUBJECTS:
        raise HTTPException(400, "Unknown subject")
    if body.delta == 0:
        raise HTTPException(400, "delta must be non-zero")
    conn = db.get_conn()
    try:
        return adjust_level(conn, child_id, body.subject, body.delta)
    finally:
        conn.close()


@router.post("/{child_id}/settings")
def parent_settings(child_id: int, body: SettingsIn) -> dict:
    conn = db.get_conn()
    try:
        child_or_404(conn, child_id)
        if body.name:
            theme = theming.theme_for(body.name, seed_index=0)
            conn.execute(
                "UPDATE children SET name=?, palette_name=?, color_primary=?, color_accent=?, color_bg=? WHERE id=?",
                (body.name.strip(), theme["name"], theme["primary"], theme["accent"], theme["bg"], child_id),
            )
        if body.palette:
            for pal in theming.PALETTES:
                if pal["name"].lower() == body.palette.lower():
                    conn.execute(
                        "UPDATE children SET palette_name=?, color_primary=?, color_accent=?, color_bg=? WHERE id=?",
                        (pal["name"], pal["primary"], pal["accent"], pal["bg"], child_id),
                    )
                    break
        if body.time_targets:
            for s, mins in body.time_targets.items():
                if s in curriculum.SUBJECTS:
                    conn.execute(
                        "INSERT INTO time_targets(child_id, subject, minutes) VALUES(?,?,?) "
                        "ON CONFLICT(child_id, subject) DO UPDATE SET minutes=excluded.minutes",
                        (child_id, s, int(mins)),
                    )
        if body.levels:
            for s, lv in body.levels.items():
                if s in curriculum.SUBJECTS:
                    old = leveling.get_level(conn, child_id, s)
                    new = curriculum.clamp_level(s, int(lv))
                    if new != old:
                        leveling.set_level(conn, child_id, s, new)
                        content.regenerate_subject_today(conn, child_id, s, db.today_str())
        conn.commit()
        return child_public(conn, child_or_404(conn, child_id))
    finally:
        conn.close()


@router.post("/prepare")
def parent_prepare(when: str = "today", child_id: int | None = None) -> dict:
    """Legacy endpoint — prefer POST /api/parent/generate."""
    conn = db.get_conn()
    try:
        day = db.today_str() if when == "today" else (date.today() + timedelta(days=1)).isoformat()
        targets = target_child_ids(conn, child_id)
        return run_generation(conn, day, targets, refresh=False)
    finally:
        conn.close()


@router.post("/generate")
def parent_generate(child_id: int | None = None, refresh: bool = True) -> dict:
    """Live-generate worksheets for today."""
    conn = db.get_conn()
    try:
        targets = target_child_ids(conn, child_id)
        return run_generation(conn, db.today_str(), targets, refresh=refresh)
    finally:
        conn.close()


@router.get("/lmstudio")
def parent_lmstudio() -> dict:
    url, model = lmstudio.get_config()
    return {"url": url, "model": model}


@router.post("/lmstudio")
def parent_set_lmstudio(body: LMStudioIn) -> dict:
    if body.url is not None:
        db.set_setting("lmstudio_url", body.url.strip())
    if body.model is not None:
        db.set_setting("lmstudio_model", body.model.strip())
    url, model = lmstudio.get_config()
    return {"url": url, "model": model}


@router.post("/lmstudio/test")
def parent_test_lmstudio() -> dict:
    return lmstudio.test_connection()


@router.get("/mascot")
def parent_get_mascot() -> dict:
    return {"mascot": db.get_setting("mascot")}


@router.post("/mascot")
def parent_set_mascot(body: MascotIn) -> dict:
    db.set_setting("mascot", body.name.strip() or "Sparky the Star")
    return {"mascot": db.get_setting("mascot")}


@router.post("/{child_id}/reset")
def parent_reset(child_id: int, scope: str = "today", regenerate: bool = True) -> dict:
    """Clear test progress. scope=today clears only today; scope=all clears everything."""
    if scope not in ("today", "all"):
        raise HTTPException(400, "scope must be 'today' or 'all'")
    conn = db.get_conn()
    try:
        child_or_404(conn, child_id)
        if scope == "today":
            result = reset_svc.reset_today(conn, child_id, regenerate=regenerate)
        else:
            result = reset_svc.reset_all(conn, child_id, regenerate=regenerate)
        result["child"] = child_public(conn, child_or_404(conn, child_id))
        return result
    except sqlite3.OperationalError as exc:
        if db._is_locked_error(exc):
            raise HTTPException(
                503,
                "Database is busy — close kid sessions and try again in a few seconds.",
            ) from exc
        raise
    finally:
        conn.close()


@router.get("/config")
def parent_config() -> dict:
    return {
        "data_dir": str(config.DATA_DIR),
        "data_dir_source": config.DATA_DIR_SOURCE,
        "db_path": str(config.DB_PATH),
    }

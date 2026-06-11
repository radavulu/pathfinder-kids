from fastapi import APIRouter, HTTPException

from .. import content, curriculum, db, leveling, rewards
from ..schemas import AnswerIn
from ..services.children import child_or_404, child_public
from ..services.generation import adjust_level
from ..services.grading import grade_answer

router = APIRouter(prefix="/api/kid", tags=["kid"])


@router.get("/{child_id}/today")
def kid_today(child_id: int) -> dict:
    conn = db.get_conn()
    try:
        row = child_or_404(conn, child_id)
        day = db.today_str()
        subjects = []
        for s, meta in curriculum.SUBJECTS.items():
            stats = leveling.session_stats(conn, child_id, s, day)
            level = leveling.get_level(conn, child_id, s)
            tt = conn.execute(
                "SELECT minutes FROM time_targets WHERE child_id=? AND subject=?",
                (child_id, s),
            ).fetchone()
            subjects.append({
                "subject": s,
                "label": meta["label"],
                "icon": meta["icon"],
                "input": meta["input"],
                "level": level,
                "skill": curriculum.skill_for(s, level),
                "minutes": tt["minutes"] if tt else 15,
                "answered": stats["total"],
                "correct": stats["correct"],
            })
        return {
            "child": child_public(conn, row),
            "day": day,
            "subjects": subjects,
            "mascot": db.get_setting("mascot"),
        }
    finally:
        conn.close()


@router.get("/{child_id}/next")
def kid_next(child_id: int, subject: str) -> dict:
    if subject not in curriculum.SUBJECTS:
        raise HTTPException(400, "Unknown subject")
    conn = db.get_conn()
    try:
        child_or_404(conn, child_id)
        day = db.today_str()
        rewards.touch_activity(conn, child_id, day)
        conn.commit()
        prob = content.next_problem(conn, child_id, subject, day)
        if not prob:
            raise HTTPException(503, "No problems available")
        return prob
    finally:
        conn.close()


@router.post("/{child_id}/answer")
def kid_answer(child_id: int, body: AnswerIn) -> dict:
    conn = db.get_conn()
    try:
        child_or_404(conn, child_id)
        problem = conn.execute(
            "SELECT * FROM problems WHERE id=? AND child_id=?",
            (body.problem_id, child_id),
        ).fetchone()
        if not problem:
            raise HTTPException(404, "Problem not found")
        return grade_answer(conn, child_id, problem, body.answer, body.attempt)
    finally:
        conn.close()


@router.post("/{child_id}/finish")
def kid_finish(child_id: int, subject: str, seconds: int = 0) -> dict:
    if subject not in curriculum.SUBJECTS:
        raise HTTPException(400, "Unknown subject")
    conn = db.get_conn()
    try:
        child_or_404(conn, child_id)
        day = db.today_str()
        if seconds and seconds > 0:
            conn.execute(
                "INSERT INTO sessions(child_id, day, subject, seconds) VALUES(?, ?, ?, ?)",
                (child_id, day, subject, int(seconds)),
            )
        result = leveling.apply_leveling(conn, child_id, subject, day)
        if result.get("leveled_up"):
            result["regenerated"] = content.regenerate_subject_today(conn, child_id, subject, day)
        conn.commit()
        result["stars"] = conn.execute("SELECT stars FROM children WHERE id=?", (child_id,)).fetchone()["stars"]
        result["badges"] = rewards.list_badges(conn, child_id)
        return result
    finally:
        conn.close()


@router.post("/{child_id}/adjust-level")
def kid_adjust_level(child_id: int, subject: str, delta: int = -1) -> dict:
    if subject not in curriculum.SUBJECTS:
        raise HTTPException(400, "Unknown subject")
    if delta > 0:
        raise HTTPException(400, "Kids can only request easier work from here")
    conn = db.get_conn()
    try:
        return adjust_level(conn, child_id, subject, delta)
    finally:
        conn.close()

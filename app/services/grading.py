"""Answer checking and kid feedback responses."""
from __future__ import annotations

import json
import random
import sqlite3

from .. import lmstudio, rewards, validation

PRAISE = [
    "Great job!", "Nice work!", "You got it!", "Awesome!",
    "Way to go!", "Brilliant!", "Superstar!",
]
NUDGE = [
    "So close — try again!", "Almost! Give it another go.",
    "Good try — have one more go!", "You can do this — try again!",
]


def is_correct(problem, answer: str) -> bool:
    options = json.loads(problem["options"]) if problem["options"] else None
    ptype = problem["ptype"]
    if ptype == "numeric":
        return validation.check_numeric(answer, problem["answer"])
    if ptype == "quotient_remainder":
        return validation.check_quotient_remainder(answer, problem["answer"])
    if ptype == "multiple_choice":
        return validation.check_multiple_choice(answer, problem["answer"], options)
    try:
        correct, _ = lmstudio.judge_short(problem["prompt"], problem["answer"], answer)
        return correct
    except Exception:  # noqa: BLE001
        return validation.check_short_fallback(answer, problem["answer"])


def grade_answer(
    conn: sqlite3.Connection,
    child_id: int,
    problem,
    answer: str,
    attempt: int,
) -> dict:
    correct = is_correct(problem, answer)
    already = conn.execute(
        "SELECT id FROM answers WHERE child_id=? AND problem_id=?",
        (child_id, problem["id"]),
    ).fetchone()

    if correct:
        if not already:
            conn.execute(
                """INSERT INTO answers(child_id, problem_id, day, subject, level, given, correct, attempts)
                   VALUES(?, ?, ?, ?, ?, ?, 1, ?)""",
                (child_id, problem["id"], problem["day"], problem["subject"], problem["level"], answer, attempt),
            )
            total_stars, new_badges = rewards.award_star(conn, child_id)
            conn.commit()
        else:
            total_stars = conn.execute("SELECT stars FROM children WHERE id=?", (child_id,)).fetchone()["stars"]
            new_badges = []
        return {
            "correct": True,
            "reveal": True,
            "praise": random.choice(PRAISE),
            "explanation": problem["explanation"],
            "stars": total_stars,
            "stars_awarded": 0 if already else 1,
            "new_badges": new_badges,
        }

    if attempt < 2:
        return {"correct": False, "reveal": False, "hint": problem["hint"], "nudge": random.choice(NUDGE)}

    if not already:
        conn.execute(
            """INSERT INTO answers(child_id, problem_id, day, subject, level, given, correct, attempts)
               VALUES(?, ?, ?, ?, ?, ?, 0, ?)""",
            (child_id, problem["id"], problem["day"], problem["subject"], problem["level"], answer, attempt),
        )
        conn.commit()
    return {
        "correct": False,
        "reveal": True,
        "correct_answer": problem["answer"],
        "explanation": problem["explanation"],
        "stars": conn.execute("SELECT stars FROM children WHERE id=?", (child_id,)).fetchone()["stars"],
    }

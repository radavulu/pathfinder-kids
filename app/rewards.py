"""Stars, daily streaks, and badge milestones."""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta

# Star-count milestones -> badge name.
STAR_BADGES = [
    (10, "Bronze Star"),
    (50, "Silver Star"),
    (100, "Gold Star"),
]
# Streak milestones (consecutive days) -> badge name.
STREAK_BADGES = [
    (3, "3-Day Streak"),
    (7, "1-Week Streak"),
    (30, "1-Month Streak"),
]


def touch_activity(conn: sqlite3.Connection, child_id: int, today: str) -> int:
    """Update the child's daily streak on their first activity of the day. Returns new streak."""
    row = conn.execute(
        "SELECT streak, last_active FROM children WHERE id = ?", (child_id,)
    ).fetchone()
    streak = row["streak"] or 0
    last = row["last_active"]
    if last == today:
        return streak  # already counted today
    yesterday = (date.fromisoformat(today) - timedelta(days=1)).isoformat()
    if last == yesterday:
        streak += 1
    else:
        streak = 1
    conn.execute(
        "UPDATE children SET streak = ?, last_active = ? WHERE id = ?",
        (streak, today, child_id),
    )
    _award_streak_badges(conn, child_id, streak)
    return streak


def award_star(conn: sqlite3.Connection, child_id: int) -> tuple[int, list[str]]:
    """Add one star for a correct answer. Returns (total_stars, newly_earned_badges)."""
    conn.execute("UPDATE children SET stars = stars + 1 WHERE id = ?", (child_id,))
    total = conn.execute("SELECT stars FROM children WHERE id = ?", (child_id,)).fetchone()["stars"]
    new_badges = []
    for threshold, badge in STAR_BADGES:
        if total == threshold:
            if _grant_badge(conn, child_id, badge):
                new_badges.append(badge)
    return total, new_badges


def _award_streak_badges(conn: sqlite3.Connection, child_id: int, streak: int) -> list[str]:
    new = []
    for threshold, badge in STREAK_BADGES:
        if streak == threshold and _grant_badge(conn, child_id, badge):
            new.append(badge)
    return new


def _grant_badge(conn: sqlite3.Connection, child_id: int, badge: str) -> bool:
    cur = conn.execute(
        "INSERT OR IGNORE INTO badges(child_id, badge) VALUES(?, ?)", (child_id, badge)
    )
    return cur.rowcount > 0


def list_badges(conn: sqlite3.Connection, child_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT badge FROM badges WHERE child_id = ? ORDER BY created_at", (child_id,)
    ).fetchall()
    return [r["badge"] for r in rows]

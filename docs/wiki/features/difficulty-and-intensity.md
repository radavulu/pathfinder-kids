# Feature: Difficulty & Intensity Controls

## Summary
Parents and kids can manually adjust how hard each subject feels. Auto-leveling still only
moves **up** at ≥80% session accuracy; manual controls move **down or up** on demand.
Related: [[home-kumon-app]], [[home-kumon-architecture]].

## Status
**shipped** (2026-06-08)

## Requirements
- **Per-subject levels** (1-indexed ladders in `app/curriculum.py`): math L1–L18, reading L1–L9,
  logic L1–L6.
- **Auto up, never auto down:** `leveling.apply_leveling()` bumps +1 when accuracy ≥80% and
  ≥3 answers; never demotes.
- **Parent dashboard:** each child card shows **Easier / Harder** buttons per subject with
  current skill name and level/max. Advanced numeric levels remain under Settings.
- **Kid view:** after finishing a subject, **"Too hard? Make it easier next time"** calls
  `POST /api/kid/{id}/adjust-level?subject=…&delta=-1` (kids cannot request harder from UI).
- **After manual change:** any level change (Easier, Harder, Settings, or auto level-up) **refreshes today's unserved problems** at the new level. Stale queues are also detected when a kid starts a subject.

## API
- `POST /api/parent/{child_id}/adjust-level` — body `{ "subject": "math", "delta": -1 | 1 }`
- `POST /api/kid/{child_id}/adjust-level` — query `subject`, `delta` (negative only from kid UI)
- Implementation: `leveling.adjust_level()` in `app/leveling.py`

## Open questions
- Should kid-initiated "easier" be limited (e.g. once per subject per day)? Currently unlimited.
# Session Log: Reading/Logic Level Sync + Concurrent Access

_Date: 2026-06-08_
_Related pages: [[difficulty-and-intensity]], [[home-kumon-architecture]]_

---

## Summary
User reported reading/logic levels not working and wanted two simultaneous sessions (e.g. both
kids or two browsers). Root cause: problem queues stayed at old levels after Harder, Settings,
or level-up; SQLite had no WAL/atomic claims for concurrent use.

## Reasoning
- Math appeared fine because parents often regenerated or because stale queues were less noticed;
  reading/logic depend on LM Studio batches that persisted at the wrong `level` column in `problems`.
- Only **Easier** refreshed the queue; Harder and Settings updated `child_levels` only.
- `ensure_set` skipped generation when any unserved rows existed, even at the wrong level.

## Actions Taken
1. Added `sync_problems_to_level()` — detects unserved problems where `level != child_levels.level` and regenerates.
2. Called sync from `ensure_set` / `next_problem` so kid sessions self-heal.
3. Regenerate on **any** level change (Easier/Harder, Settings, auto level-up after session).
4. SQLite: `journal_mode=WAL`, `busy_timeout=30000`, `check_same_thread=False`.
5. Atomic `next_problem` claim via `BEGIN IMMEDIATE` + conditional UPDATE.
6. Lenient LM Studio MC validation (answer snapped to nearest option).
7. Pad reading/logic batches with starter bank when LM returns too few items.
8. Tests: `tests/test_content.py` (sync + concurrent claims).

## Rejected Alternatives
- **Require manual Generate after every level change** — rejected; too easy to forget, especially for reading/logic.

## Assumptions Made
- Two concurrent users means two child profiles or two browsers on the same server, not two uvicorn workers on separate DB files.

## Insights & Observations
- Kid UI shows `cur.skill` from the problem row; syncing the queue is essential for level changes to feel immediate.

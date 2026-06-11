# Session Log: Modular Backend + input/ Cleanup

_Date: 2026-06-08_
_Related pages: [[modular-backend]], [[home-kumon-architecture]], [[placement-and-curriculum]], [[portable-launchers]]_

---

## Summary
User asked whether the `input/` PDF folder is still needed, to clean up code, and make the
project more modular. Confirmed `input/` is not used at runtime; refactored the backend into
`routes/`, `services/`, `schemas.py`, and `starter_bank.py` without changing API behavior.

## Reasoning
- Placement research from Kumon PDFs was already compiled into curriculum ladders, wiki pages,
  and SQLite seed levels — no code path reads `input/`.
- `main.py` had become a god-file (~490 lines) mixing HTTP, grading, generation, and child helpers.
- FastAPI `APIRouter` split matches the existing kid/parent API surface and keeps tests/import
  checks simple (`from app.main import app` still works).

## Actions Taken
1. Confirmed no `input/` folder in repo and no runtime references — documented in wiki + README.
2. Extracted `app/starter_bank.py` from `content.py` (math/reading/logic offline banks).
3. Added `app/schemas.py` for all Pydantic models.
4. Added `app/services/{children,generation,grading}.py` for domain logic.
5. Added `app/routes/{health,pages,children,kid,parent}.py` + `register_routes()`.
6. Slimmed `app/main.py` to startup + static mount (~20 lines).
7. Updated [[home-kumon-architecture]], [[placement-and-curriculum]], `log.md`, `index.md`.

## Rejected Alternatives
- **Keep `input/` for reference** — rejected for the shipped app; wiki + DB seed are the durable
  source of truth. User can keep PDFs elsewhere (OneDrive) if desired.
- **Full package restructure (`app/api/`, `app/domain/`)** — rejected as over-engineering; flat
  `routes/` + `services/` matches current project size.
- **Delete `scripts/find_port.py` when port fixed to 8700 in `run.sh`** — kept; still useful for
  other launch paths and optional auto-pick.

## Problems Encountered
- None — import check passed (`27` routes registered).

## Assumptions Made
- User wants modular Python backend only; frontend JS/HTML structure unchanged for this pass.
- Default port **8700** (set in `run.sh` / `config.py`) is intentional per prior user request.

## Insights & Observations
- `content.py` is now purely lifecycle; offline banks are easier to extend per subject.
- Wiki had partial updates (log + architecture) but was missing a session log and pattern page
  until this compile pass.

# Session Log: Portability, Docker, Difficulty Controls

_Date: 2026-06-08_
_Related pages: [[portability-and-deployment]], [[difficulty-and-intensity]], [[portable-launchers]], [[2026-06-08-port-bind-fix]]_

---

## Summary
After fixing port-8000 and `pip: command not found` startup errors, extended the app for
cross-machine use (export/import), one-command Docker, and manual difficulty (intensity)
controls for parents and kids.

## Reasoning
User asked whether export/import to another machine works and wanted Docker for easy runs.
Progress is already in SQLite — portability is a documentation + script problem, not a
schema change. Difficulty controls fill the gap left by "never auto-down" leveling: parents
need a quick way to ease work when kids struggle.

## Actions Taken
1. **`scripts/export-data.sh` / `import-data.sh`** — tar backup/restore of `DATA_DIR`.
2. **`docker-run.sh`**, updated `Dockerfile` (healthcheck, `scripts/`), `docker-compose.yml`
   (restart, volume env), `.dockerignore`.
3. **`GET /api/health`** — Docker healthcheck endpoint.
4. **`leveling.adjust_level()`** + parent/kid API routes; parent UI Easier/Harder; kid
   "Too hard?" on celebrate screen.
5. **`run.sh`/`run.bat`** — `.venv/bin/python -m pip` + `ensurepip` (prior fix in same arc).
6. **README** — sections on move-to-machine, Docker, difficulty.

## Rejected Alternatives
- **Auto-kill process on port 8000** — could stop unrelated services.
- **Kid can request harder** — rejected from kid UI; only parent adjusts up.
- **Pre-built Docker registry image** — deferred; user may want later.

## Problems Encountered
- **`pip: command not found`** — venv activate did not expose pip; fixed with `-m pip`.
- **`address already in use`** — fixed with `find_port.py` (see [[2026-06-08-port-bind-fix]]).

## Assumptions Made
- User syncs code via OneDrive Cowork folder; may run from `output/HomeKumon/` in repo or synced copy.
- LM Studio always on host at `localhost:1234`, not in container.

## Insights & Observations
- Corporate `PIP_PROXY` is unrelated to uvicorn bind errors — separate troubleshooting paths.
- After difficulty change, prepared problems for today may still be at old level until **Prepare sets** runs.

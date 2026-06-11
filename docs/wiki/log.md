# Wiki Operation Log

2026-06-08 — Created the wiki and compiled the Home Kumon project: architecture, app feature spec, placement & curriculum findings (Nivi & Nyra), the deterministic-math + proxy-bypass patterns, stakeholder context, and the build session log. Seeded index.md.
2026-06-08 — Fixed port-8000 bind failure: `scripts/find_port.py`, launcher updates, README troubleshooting; logged in [[2026-06-08-port-bind-fix]].
2026-06-08 — Fixed `pip: command not found`: launchers use `.venv/bin/python -m pip` and `ensurepip` bootstrap.
2026-06-08 — Docker one-command (`docker-run.sh`), export/import scripts, difficulty controls (parent Easier/Harder + kid "Too hard?"), health endpoint.
2026-06-08 — Wiki compiled: [[portability-and-deployment]], [[difficulty-and-intensity]], [[portable-launchers]], [[2026-06-08-portability-docker-difficulty]]; updated architecture + app feature pages.
2026-06-08 — Easier difficulty auto-regenerates today's unserved problems (`content.regenerate_subject_today`); wiki + README updated.
2026-06-08 — Kid session UI: right-side coach panel for hints/feedback; live session counters (done / correct / wrong).
2026-06-08 — Default data dir changed to **./data** beside the app (no OneDrive auto-detect); use `HOMEKUMON_DATA_DIR` to override.
2026-06-08 — Ages bumped to 8/9; Nyra math default L15; harder number ranges at L12–L18 in starter_bank.
2026-06-08 — Full reset lock fix: `run_immediate()` with retries, 60s busy timeout, regen after commit.

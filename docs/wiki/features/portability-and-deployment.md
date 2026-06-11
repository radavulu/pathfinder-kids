# Feature: Portability & Deployment

## Summary
Home Kumon is designed to move between machines without losing kid progress. Code and data
are separate; `.venv` is never copied. Docker provides a one-command alternative to
`./run.sh`. Related: [[home-kumon-architecture]], [[deterministic-math-and-proxy-bypass]].

## Status
**shipped** (2026-06-08)

## Requirements
- **Progress lives in SQLite** (`homekumon.db` under `DATA_DIR`), not in code or venv.
- **Default path:** `./data/homekumon.db` next to the app (`app/config.py`).
- **Optional OneDrive:** set `HOMEKUMON_DATA_DIR` to your synced folder.
- **Export:** `./scripts/export-data.sh` → `homekumon-backup-YYYYMMDD.tar.gz`
- **Import:** `./scripts/import-data.sh backup.tar.gz` on new machine
- **Do not copy:** `.venv/` — recreate with `./run.sh` on each machine
- **Native launch:** `run.sh` / `run.bat` — venv via `.venv/bin/python -m pip`, port auto-pick
  (`scripts/find_port.py`), `ensurepip` bootstrap if pip missing
- **Docker launch:** `./docker-run.sh` → `docker compose up -d`; image `homekumon:latest`;
  data volume `${HOMEKUMON_DATA_DIR:-./data}:/data`; LM Studio on host via
  `host.docker.internal:1234`
- **Health check:** `GET /api/health` (used by Docker `HEALTHCHECK`)

## Open questions
- Pre-built image on a registry (skip `docker compose build` on new machines)? Not built yet.
- Linux hosts: verify `host.docker.internal` via `extra_hosts: host-gateway` (already in compose).

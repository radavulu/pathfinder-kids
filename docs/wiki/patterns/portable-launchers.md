# Pattern: Portable Launchers (Native + Docker)

## Summary
Launch scripts must work on a fresh machine without assuming `pip` or `uvicorn` on PATH.
Default app port is **8700** (see `app/config.py` and `run.sh`). Related:
[[portability-and-deployment]], [[home-kumon-architecture]].

## When to use
- Any local Python app copied between Macs, especially behind corporate proxies or with
  Homebrew Python where venv activation does not expose `pip`.

## Example
**Native (`run.sh`):**
- Use `.venv/bin/python -m pip` and `.venv/bin/python -m uvicorn` (not bare commands).
- Bootstrap: `"$VENV_PY" -m ensurepip --upgrade` if pip missing.
- Port: `export HOMEKUMON_PORT="${HOMEKUMON_PORT:-8700}"` — fixed default; override per run if needed.
- Proxy: `NO_PROXY=localhost,127.0.0.1,::1`; optional `PIP_PROXY` + `--trusted-host` for PyPI.

**Docker (`docker-run.sh`):**
- `docker compose build && docker compose up -d`
- Default port **8700** inside container; map host port via `HOMEKUMON_PORT`.

## Anti-patterns
- ❌ Copying `.venv` between machines (architecture mismatch, broken pip).
- ❌ `pip install` without `-m pip` after venv activate on macOS.
- ❌ Assuming port 8000/8888 without checking `config.DEFAULT_PORT` or `run.sh`.
- ❌ Running LM Studio inside the same container (must stay on host for GPU/local model).

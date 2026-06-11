# Session Log: Flat Repo Layout

**Date:** 2026-06-08  
**Summary:** Removed `input/` and `output/` folders; app lives at repo root.

## Context

The Cowork workspace had an awkward layout: reference PDFs in `input/`, the runnable app nested under `output/HomeKumon/`. The user asked for a clean structure.

## Decisions

- **App at repo root** — `app/`, `web/`, `run.sh`, etc. sit directly under `home-ku/`. Run `./run.sh` from the repo root.
- **Reference PDFs** — moved to `docs/raw/placement/` (immutable archive; not read at runtime). PDFs gitignored (~400MB).
- **Removed** — empty `input/` and `output/` directories after the move.

## Actions

1. Moved all HomeKumon project files from `output/HomeKumon/` to repo root.
2. Moved placement PDFs from `input/` → `docs/raw/placement/`.
3. Added root `.gitignore` (`.venv/`, `data/`, PDFs).
4. Updated README, memory, wiki index, Cursor llm-wiki rule paths.

## Alternatives considered

- **Keep `HomeKumon/` subfolder** — rejected; user wanted no output nesting.
- **Delete PDFs entirely** — kept under `docs/raw/` for archival; documented as optional.

## Follow-up

- Recreate `.venv` after move: `rm -rf .venv && ./run.sh` (old venv paths were under `output/HomeKumon/`).
- Sync OneDrive Cowork copy if the user runs from there.

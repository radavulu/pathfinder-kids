# PathfinderKids — Wiki Index

Knowledge base for the PathfinderKids project: a local, Kumon-style daily learning app for
two children, with LM Studio-generated content. Compiled by the AI; do not hand-edit.

_Last updated: 2026-06-08 (flat repo layout)_

---

## Architecture
- [[home-kumon-architecture]] — stack choices (FastAPI + SQLite + vanilla JS + LM Studio), data dir, run paths, Docker.

## Features
- [[home-kumon-app]] — full app spec: profiles, subjects, daily sets, leveling, validation, rewards, parent dashboard.
- [[placement-and-curriculum]] — Nivi & Nyra placement assessment and the curriculum extension to match.
- [[difficulty-and-intensity]] — parent Easier/Harder + kid "Too hard?" controls.
- [[portability-and-deployment]] — export/import, OneDrive, Docker, native launchers.

## Patterns
- [[deterministic-math-and-proxy-bypass]] — compute-don't-prompt for math; bypass corporate proxy for localhost.
- [[portable-launchers]] — venv `-m pip`, default port 8700, Docker vs native.
- [[modular-backend]] — `routes/` + `services/` + `starter_bank.py` layout.
- [[llm-wiki-workflow]] — read wiki before changes; auto-update after major work.

## People & Context
- [[kids-and-stakeholder]] — who the app is for (Nivi, Nyra) and the parent's goals.

## Session Logs
- [[2026-06-08-home-kumon-build]] — the build session: design interview, build, placement, gaps, proxy fix.
- [[2026-06-08-port-bind-fix]] — launcher auto-picks free port when 8000 is busy.
- [[2026-06-08-portability-docker-difficulty]] — export/import, Docker, pip fix, difficulty UI.
- [[2026-06-08-modular-refactor]] — backend split into routes/services; `input/` not required.
- [[2026-06-08-cursor-rules-llm-wiki]] — global + project Cursor rules for read-before / auto-update wiki.
- [[2026-06-08-level-sync-concurrency]] — reading/logic level queue sync + two-session SQLite fixes.
- [[2026-06-08-flat-repo-layout]] — flattened repo: no `input/`/`output/`; app at root; PDFs in `docs/raw/placement/`.

---

## Quick facts
- Owner/parent: Raviteja Davuluri (Senior Cloud Engineer, macOS).
- Kids: **Nyra** (→3rd grade) and **Nivi** (→4th grade); both ~2 years above grade in Kumon math.
- Project files: repo root (`home-ku/`) — code, `plan.md`, `memory.md`, this wiki.
- Status: shipped v1.0; native run working; Docker + portability documented; live LM Studio verification ongoing.

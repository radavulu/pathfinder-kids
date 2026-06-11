# Memory: Home Kumon

_Last updated: 2026-06-08 after flat repo layout_
_Session scope: port 8888, Docker defaults, live generate + timer overlay, plan/memory update_

---

## Current Status
**Phase:** Phase 8 — Ops & UX polish (🔵 In Progress)
**Active Milestone:** J — Docker, port, live generation (J6 user verification pending)
**Overall Progress:** ~90% (app feature-complete; live ops polish + handoff remain)

---

## What Was Completed (Most Recent First)
- 2026-06-08 — **Flat repo layout:** app moved from `output/HomeKumon/` to repo root; PDFs archived to `docs/raw/placement/`; removed `input/`/`output/` folders.
- 2026-06-08 — **Milestone J (mostly complete):** default port **8888**; Docker compose/run on 8888; `POST /api/parent/generate` + `content.refresh_day()` for live today refresh; parent UI spinner+timer overlay; per-child generate buttons; README/plan updated.
- 2026-06-08 — **Milestone K:** kid session right-side coach panel; done/correct/wrong counters.
- 2026-06-08 — Easier difficulty auto-regenerates today's unserved problems; export/import scripts; difficulty controls; launcher pip/port fixes; native run verified on user's Mac.
- 2026-06-08 — Full v1 build (Phases 1–6), curriculum extended for Nyra/Nivi placement, gaps G1–G3 closed.

---

## What Is Next
1. **J6** — User runs `./docker-run.sh`, opens http://127.0.0.1:8666, tests **Generate new sets** with LM Studio and confirms timer + fresh problems.
2. **H3** — Printable PDF worksheets (offered; awaiting go-ahead).
3. **Phase 7** — Full E2E handoff validation on user's Mac.

---

## Open Questions / Blockers
- None blocking J6 — needs user to run Docker locally with LM Studio on host.

---

## Key Context
- **User:** Raviteja Davuluri; macOS; corporate iboss proxy (PIP_PROXY for pip); LM Studio on localhost:1234.
- **Run paths:** **Docker** `./docker-run.sh` → http://127.0.0.1:8700 (preferred). Native `./run.sh` also defaults to 8700.
- **Data:** `./data/homekumon.db` next to the app (override with `HOMEKUMON_DATA_DIR`).
- **Generation:** Live on-demand for **today** only — no "prepare tomorrow." Reading/Logic ~30–90s/child via LM Studio; math instant (computed). Parent UI shows elapsed timer during generate.
- **Kids:** Nyra (8, math L15) & Nivi (9, math L18). Data in `./data` (override with `HOMEKUMON_DATA_DIR`).
- **Files:** repo root (`home-ku/`) — code, `plan.md`, `memory.md`, wiki under `docs/wiki/`.

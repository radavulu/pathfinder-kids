# Plan: PathfinderKids

_Last updated: 2026-06-08_
_Version: 1.0_

---

## Overview
A local, Kumon-style daily learning web app for two children (ages 7 and 8), running on a
shared home computer. LM Studio generates Math / Reading / Logic problems; the app serves
time-based daily sets, adapts difficulty, validates answers with kid-friendly explanations,
and rewards progress with stars, streaks, and a mascot. Full design locked in
`HomeKumon-Design-Spec.md`.

**Stack:** FastAPI + SQLite backend, vanilla HTML/CSS/JS themed frontend, LM Studio
(`http://localhost:1234/v1`) content engine. Runs via venv script and Docker. Data dir
defaults to a OneDrive-synced folder for auto-backup.

---

## Build Status & Feature Coverage (audited 2026-06-08)

Phases 1–6 implemented and smoke-tested offline (DB seeding, starter-bank serving,
validation, adaptive level-up, rewards, theming, syntax across all modules).

**Covered ✅:** 2 profiles + rename, auto color themes, profile picker, 3 subjects,
time-based sets (finish-current + "I'm done"), Prepare button (today/tomorrow),
offline starter bank, adaptive forgiving leveling (80% up / never down / per subject /
8yo +1 tier), smart input (keypad + 4-choice), hybrid validation + pre-generated
explanations, hint→retry→reveal, hints/encouragement, stars/streaks/badges,
mascot + confetti, parent dashboard (progress, accuracy, levels, history, settings,
LM Studio config + test), OneDrive-default data dir, run.sh/run.bat + Docker.

**Gaps found 🔶 — ALL RESOLVED 2026-06-08:**
- G1 — ✅ Time-on-task now tracked (sessions table records seconds per child/subject/day;
  dashboard shows total + today minutes per subject).
- G2 — ✅ Math generated deterministically (computed answers, always correct); model no
  longer trusted for arithmetic. Reading/Logic still use LM Studio.
- G3 — ✅ Mascot name editable in the parent dashboard.

### Milestone G: Coverage gaps
**Status:** ✅ Complete
Tasks:
- [x] G1 — Track and display actual time spent per child/subject/day
- [x] G2 — Deterministic math generation (computed answers)
- [x] G3 — Expose mascot name in parent settings

### Milestone H: Placement from sample work (requested 2026-06-08)
**Status:** 🔵 In Progress
Tasks:
- [x] H1 — Scanned Nivi + Nyra Kumon PDFs (math + English)
- [x] H2 — Assessed placement: both ~2 yrs above grade (see memory.md)
- [ ] H3 — Printable practice worksheets (PDF) matching their level — offered, awaiting go-ahead

### Milestone I: Curriculum upgrade to match the kids (2026-06-08)
**Status:** ✅ Complete
Tasks:
- [x] Extended math ladder to L18 (multi-digit ×, long division w/ remainder)
- [x] Extended reading ladder to L9 (key details, sentence-combining, either-or/neither-nor)
- [x] Deterministic math generation (computed answers) — resolves G2
- [x] New `quotient_remainder` input type + keypad "R" key + validation
- [x] Seeded profiles Nyra (2nd, math L14) & Nivi (3rd, math L18) at real levels
- [x] Smoke test extended + passing

---

## Phase 1: Discovery & Design
**Status:** ✅ Complete

### Milestone 1.1: Requirements & design finalized
**Status:** ✅ Complete

Tasks:
- [x] Interview across 5 rounds, resolve all major design branches
- [x] Write locked design spec (`HomeKumon-Design-Spec.md`)
- [x] Confirm OneDrive-default data dir for auto-backup
- [x] Stand up project folder, `plan.md`, `memory.md`

---

## Phase 2: Backend Foundation
**Status:** ✅ Complete

### Milestone 2.1: Project scaffold & data model
Tasks:
- [ ] App skeleton (FastAPI, static serving, config loader, OneDrive DATA_DIR auto-detect)
- [ ] SQLite schema: children, levels (per subject), sessions, problems, answers, rewards/badges, settings
- [ ] DB access layer + migrations/seed-on-first-run
- [ ] Health/config endpoints + LM Studio "test connection"

### Milestone 2.2: Core domain logic
Tasks:
- [ ] Adaptive leveling engine (≥80% up, never auto-down, per subject; 8yo starts +1 tier)
- [ ] Session/timer logic (15 min/subject default, finish-current-problem, "I'm done")
- [ ] Hybrid validation (numeric exact + normalization; MC exact; short → LLM judge)
- [ ] Rewards engine (stars, daily streak, badge thresholds 10/50/100)

---

## Phase 3: Content Generation
**Status:** ✅ Complete

### Milestone 3.1: LM Studio integration
Tasks:
- [ ] OpenAI-compatible client (chat/completions), model auto-detect
- [ ] Per-subject/level prompts → structured JSON (problem, type, options, answer, explanation, hint, skill, level)
- [ ] JSON validation + retry on malformed output
- [ ] "Prepare tomorrow's sets" job + storage tied to date/child/subject/level

### Milestone 3.2: Offline starter bank
Tasks:
- [ ] Author seed JSON bank per subject/level (covers each ladder rung)
- [ ] Fallback wiring + "using offline bank" signal to dashboard

---

## Phase 4: Kid Experience (Frontend)
**Status:** ✅ Complete

### Milestone 4.1: Profiles & theming
Tasks:
- [ ] Start page → profile picker
- [ ] Name→color derivation, per-child themed UI (placeholders Kid 1 / Kid 2)

### Milestone 4.2: Session flow
Tasks:
- [ ] Today's plan (3 subjects), per-subject timer UI
- [ ] Math number keypad; Reading/Logic 4-choice tap
- [ ] Wrong-answer flow: hint → one retry → reveal + explanation
- [ ] Encouragement + hints display

### Milestone 4.3: Fun layer
Tasks:
- [ ] Stars/streak/badge UI
- [ ] Mascot reactions + end-of-session confetti/celebration

---

## Phase 5: Parent Dashboard
**Status:** ✅ Complete

### Milestone 5.1: Dashboard (open, no PIN)
Tasks:
- [ ] Per-child progress: accuracy, level/subject, time spent, streak, stars/badges
- [ ] Answer history view
- [ ] Settings: rename kids, color, per-subject time targets, starting levels
- [ ] "Prepare tomorrow's sets" button
- [ ] LM Studio settings: endpoint, model, Test connection; DATA_DIR location

---

## Phase 6: Packaging & Docs
**Status:** ✅ Complete

### Milestone 6.1: Run paths + README
Tasks:
- [ ] `run.sh` / `run.bat` (venv, install, launch, open browser)
- [ ] Dockerfile + docker-compose (host.docker.internal:1234 note)
- [ ] README: setup, LM Studio enablement, OneDrive data dir, troubleshooting

---

## Phase 7: Test & Handoff
**Status:** 🔵 In Progress

### Milestone 7.1: Validation
Tasks:
- [ ] End-to-end smoke test (with and without LM Studio)
- [ ] Validation edge cases (numeric normalization, MC, short-answer judge)
- [ ] Deliver full app to OneDrive Cowork files + handoff notes

---

## Phase 8: Ops & UX polish (2026-06-08)
**Status:** 🔵 In Progress

### Milestone J: Docker, port, live generation
**Status:** 🔵 In Progress

Tasks:
- [x] J1 — Change default app port to **8888** (run.sh, Docker, config, docs)
- [x] J2 — Docker as primary run path (`docker-run.sh`, compose on 8888)
- [x] J3 — Replace "prepare tomorrow" with **live generate for today** (`POST /api/parent/generate`, `content.refresh_day`)
- [x] J4 — Parent UI: generation overlay with spinner + elapsed timer; 10 min API timeout
- [x] J5 — Per-child **Generate new sets** buttons on dashboard
- [x] J7 — Code cleanup: shared helpers, CSS classes, formatting config (`pyproject.toml`, `.editorconfig`)
- [ ] J6 — User verifies Docker + live generate end-to-end on Mac with LM Studio

### Milestone K: Kid session UX
**Status:** ✅ Complete

Tasks:
- [x] K1 — Right-side coach panel for hints/feedback
- [x] K2 — Session counters (done / correct / wrong)

### Milestone L: Modular backend
**Status:** ✅ Complete

Tasks:
- [x] L1 — Split `main.py` into `app/routes/` (kid, parent, pages, health)
- [x] L2 — Extract `app/services/` (children, generation, grading) + `app/schemas.py`
- [x] L3 — Move offline bank to `app/starter_bank.py`; slim `content.py`
- [x] L4 — Document that `input/` PDFs are not required at runtime (wiki + README)

---

## Risks & Assumptions
- 2026-06-08 — Container is NOT the user's PC; app runs locally on their machine. Deliverables go to OneDrive for download. No runtime testing against the user's actual LM Studio is possible from here.
- 2026-06-08 — Generated content quality depends on the user's loaded LM Studio model; small models may need prompt tuning. Mitigated by JSON validation + retry + starter bank.
- 2026-06-08 — OneDrive path auto-detection varies by OS/locale (Documents/Cowork may be renamed). Will make DATA_DIR overridable.
- 2026-06-08 — Open dashboard (no PIN) means kids could change settings; accepted per user choice.

---

## Decisions & Notes
- 2026-06-08 — All design decisions captured in `HomeKumon-Design-Spec.md` (5 interview rounds).
- 2026-06-08 — DATA_DIR defaults to OneDrive-synced folder for auto-backup of kids' progress.
- 2026-06-08 — Level-ladder content (spec §12) approved as written; tunable later via dashboard + adaptive leveling.
- 2026-06-08 — Default port **8666** (was 8888); Docker primary; live worksheet generation with timer overlay (Milestone J).

# PathfinderKids — Design Spec

A local, Kumon-style daily learning app for two children (ages 7 and 8), running on a
shared home computer with LM Studio generating the content. This document captures every
decision agreed during the design interview. It is the build contract.

_Last updated: 2026-06-08_

---

## 1. Overview

| Aspect | Decision |
|---|---|
| Form factor | Local web app, shared computer, opened in a browser |
| Backend | Python (FastAPI) — serves the UI + REST API |
| Database | SQLite |
| Frontend | Vanilla HTML/CSS/JS, themed per child (no heavy framework) |
| Content engine | LM Studio (OpenAI-compatible API at `http://localhost:1234/v1`) |
| Run options | venv + run script (`run.sh` / `run.bat`) **and** Docker |

---

## 2. Children & Profiles

- **Two profiles.** Placeholders **"Kid 1" (age 7)** and **"Kid 2" (age 8)** — renamable in the parent dashboard.
- **Auto-assigned color themes:** a stable color is derived from each child's name (one cool, one warm) and themes that child's entire UI.
- **Start page:** pick a profile to begin.

---

## 3. Subjects

- **Math**
- **Reading / English**
- **Logic / Puzzles**

---

## 4. Daily Structure ("the schedule")

- **Time-based dose**, default **15 minutes per subject (~45 min/day total)**, adjustable per child.
- App serves problems continuously until the per-subject timer ends; the child **finishes the current problem**, and an **"I'm done" button** allows stopping early.
- Worksheets are **pre-generated**. The parent clicks **"Prepare tomorrow's sets"** in the dashboard (LM Studio must be running).
- **Offline fallback:** if LM Studio is unreachable, the app serves a **built-in starter question bank** per subject/level; the parent dashboard shows an "using offline bank" note.

---

## 5. Adaptive Leveling

- **Per-subject, independent** numeric level ladders (each level has a skill descriptor).
- **Forgiving rule:** session accuracy **≥ 80% → level up**; **never auto-down** (a weak session just holds the level).
- The **8-year-old starts one tier above** the 7-year-old.

---

## 6. Answer Input (smart per subject)

- **Math:** on-screen **number keypad** → typed numeric answer.
- **Reading & Logic:** **tap one of 4 choices**.

---

## 7. Validation (hybrid) — "verify, confirm, explain"

Every generated problem carries: `type` (numeric / multiple-choice / short), the **canonical answer**, a **kid-friendly explanation**, and a **hint**.

- **Math (numeric):** checked **locally and exactly**, with normalization (e.g. `0.5` == `1/2`). Instant.
- **Multiple-choice (Reading/Logic):** checked **locally** against the correct option. Instant.
- **Short / typed answers (if enabled):** **LM Studio judges** the child's answer against the canonical answer, returns correct/incorrect + explanation, spelling-lenient.
- Explanations are **pre-generated** with each problem, so feedback is instant and works offline.

**Wrong-answer flow:** gentle **hint → one retry → reveal** the correct answer with a kid-friendly explanation.

---

## 8. Interactivity (kid-facing)

- **Hints + encouragement:** warm, age-appropriate nudges and praise.
- **Stars / streaks / rewards:** a star per correct answer, a **daily streak** counter (consecutive days completed), **badges** at milestones (default 10 / 50 / 100 stars).
- **Mascot + celebration:** a friendly character reacts to answers; **confetti/animation** when a session is finished.
- **No read-aloud / text-to-speech.**

---

## 9. Parent Dashboard (open, no PIN)

- Per-child **progress:** accuracy, current level per subject, time spent, streak, stars/badges.
- **Answer history.**
- **Settings:** rename children, adjust color, set per-subject time targets, set/adjust starting levels.
- **"Prepare tomorrow's sets"** button.
- **LM Studio settings:** endpoint (default `http://localhost:1234/v1`), model (auto-detect loaded model), **Test connection**.

---

## 10. Content Generation

- Prompted per **subject + level** to return a **batch of problems as structured JSON**
  (`problem`, `type`, `options`, `answer`, `explanation`, `hint`, `skill`, `level`).
- Generated JSON is **validated**; malformed output triggers a retry.
- Stored in SQLite, tied to **date + child + subject + level**.
- **Starter bank** (seed JSON in the repo) covers each subject/level for offline use.

---

## 11. Data Persistence & OneDrive

- The app's SQLite database lives on **your PC** when the app runs.
- `DATA_DIR` **defaults to a OneDrive-synced folder** (`Documents/Cowork/HomeKumon/data`,
  auto-detected) so kids' progress **backs up automatically** and survives PC reinstalls.
  Configurable in the parent dashboard.
- **This spec** is saved to your OneDrive Cowork files so the design itself is preserved.

---

## 12. Defaults I'm assuming (all adjustable later)

- Generation batch size: ~20 problems per subject/level cached.
- Badge thresholds: 10 / 50 / 100 stars.
- Streak resets if a day is missed.
- Level ladders (sample):
  - **Math** — 7yo start: addition/subtraction within 20 → within 100 → intro multiplication.
    8yo start: within 100 → multiplication/division → simple fractions.
  - **Reading** — sight words / 1-sentence comprehension → short passages → vocabulary in context.
  - **Logic** — patterns & odd-one-out → sequences → simple word problems.

---

## 13. Open items before build

- [x] DATA_DIR defaults to a OneDrive-synced path for auto-backup.
- [ ] Confirm the level-ladder content above (or adjust) — to finalize during project planning.
- [ ] Greenlight to build.

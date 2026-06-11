# Session Log: PathfinderKids — design, build, placement, gaps, proxy fix

_Date: 2026-06-08_
_Related pages: [[home-kumon-architecture]], [[home-kumon-app]], [[placement-and-curriculum]], [[deterministic-math-and-proxy-bypass]], [[kids-and-stakeholder]]_

---

## Summary
Designed, built, and tuned the PathfinderKids app in one session: a 5-round design interview,
full build (FastAPI + SQLite + vanilla JS + LM Studio), a feature-coverage audit, placement
assessment from the kids' Kumon PDFs, a curriculum extension to match, closing of all coverage
gaps, and a corporate-proxy fix for installs.

## Reasoning
- Chose FastAPI + SQLite + vanilla JS for robustness and minimal tooling on a single home Mac.
- Pre-generated content + offline starter bank so kids never wait on the model and always have
  work. Hybrid validation keeps feedback instant.
- After seeing the worksheets, prioritized **extending the curriculum** over shipping as-is —
  the app would otherwise be far too easy for these kids.
- Made math deterministic to guarantee correct answer keys (resolving an audit risk).
- For the proxy, scoped the bypass to localhost only (LM Studio is always local), keeping
  behavior environment-driven.

## Actions Taken
1. Ran a grill/design interview (5 rounds) → locked spec; set up `plan.md` + `memory.md`.
2. Built backend (config/db/curriculum/leveling/validation/rewards/lmstudio/content/main),
   themed web UI, run scripts, Docker, README; passed an offline smoke test.
3. Feature-coverage audit → logged gaps G1 (time-on-task), G2 (LLM math keys), G3 (mascot).
4. Read the kids' Kumon PDFs; assessed placement (both ~2 yrs above grade).
5. Extended math ladder to L18 and reading to L9; made math deterministic; added
   `quotient_remainder` input/validation; seeded profiles Nyra & Nivi at real levels.
6. Closed G1 (sessions table + dashboard minutes) and G3 (editable mascot). G2 already closed.
7. Diagnosed a `pip install` failure behind an iboss PAC proxy; added proxy bypass for local
   LM Studio calls, `NO_PROXY` in launchers, and `PIP_PROXY` + `--trusted-host` for pip.

## Rejected Alternatives
- **Single HTML/localStorage app** — too fragile. **React/Node** — too heavy.
- **Model judges/produces math** — unreliable arithmetic; replaced with computed math.
- **PIN-locked dashboard / cron prep / TTS read-aloud** — user chose open dashboard, manual
  prep, and no TTS.
- **Tuning to school grade** — rejected in favor of real Kumon levels from the worksheets.
- **Global TLS-verify disable for pip** — rejected; scoped to PyPI `--trusted-host` only.

## Problems Encountered
- **Uploaded PDFs not initially visible** — workspace `input/` was empty; resolved when the
  user re-attached them directly.
- **Large PDFs** — read in page ranges; the "grade" PDFs were logistics packets, not grades.
- **`pip install` failed behind iboss proxy** — resolved via `PIP_PROXY` + trusted-host flags;
  LM Studio calls hardened to bypass the proxy (`trust_env=False`).

## Assumptions Made
- Nyra = 7 (→2nd) maps to Kid 1; Nivi = 8 (→3rd) maps to Kid 2.
- Worksheets (~May 2025) approximate current level; adaptive leveling will refine.
- The iboss proxy is reachable at `127.0.0.1:8009` (from the user's PAC default).

## Insights & Observations
- Both kids are notably advanced in math (Kumon Level D) relative to grade — the app's ceiling
  had to rise substantially to stay useful.
- The PAC only bypasses `localhost`/`127.0.0.1`; anything else (including the machine's own
  hostname) is proxied — a subtle gotcha for local dev tools on managed machines.

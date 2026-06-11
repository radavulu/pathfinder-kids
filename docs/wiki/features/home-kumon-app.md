# Feature: Home Kumon App

## Summary
A daily, Kumon-style practice app for two kids: pick a profile, do timed sets in Math,
Reading, and Logic, get instant feedback with explanations, and earn stars/streaks/badges.
A parent dashboard tracks progress and configures the app. See [[home-kumon-architecture]], [[modular-backend]],
[[placement-and-curriculum]], [[difficulty-and-intensity]], [[portability-and-deployment]].

## Status
**shipped** (v1.0) — feature-complete; native launch verified on user's Mac (port/pip fixes).
Docker + export/import + difficulty controls added 2026-06-08.

## Requirements (agreed in design interview, 2026-06-08)
- **Profiles:** two kids, auto color themes from names, renamable. Seeded as **Nyra** (8,
  →3rd) and **Nivi** (9, →4th). Start page = profile picker.
- **Subjects:** Math, Reading/English, Logic/Puzzles.
- **Daily dose:** time-based, default **15 min/subject** (~45/day); finish the current
  problem when time's up; an **"I'm done"** button stops early.
- **Adaptive leveling:** per subject, independent. **≥80% in a session → level up; never
  auto-down** (forgiving). Manual **Easier/Harder** in parent dashboard; kid **"Too hard?"**
  after session — see [[difficulty-and-intensity]].
- **Input:** Math = number keypad; Reading/Logic = tap one of 4 choices; long division uses
  a `quotient_remainder` keypad (digits + "R").
- **Validation (hybrid):** math computed/exact; multiple-choice exact; short answers judged
  by LM Studio. Wrong-answer flow: **hint → one retry → reveal answer + kid-friendly
  explanation**. Explanations pre-generated, so feedback is instant and works offline.
- **Interactivity:** hints + encouragement, stars/streaks/badges (10/50/100 stars;
  3/7/30-day streaks), mascot + confetti celebration. **No text-to-speech** (deselected).
- **Content prep:** live **"Generate new sets"** for today (parent dashboard, timer overlay);
  legacy Prepare endpoint kept; offline **starter bank** when LM Studio is unreachable.
- **Parent dashboard (open, no PIN):** per-child progress (accuracy, level, **time spent**,
  streak, stars/badges), **difficulty controls**, answer history, settings (rename, color,
  time targets, levels), Prepare button, LM Studio config + Test connection, editable mascot
  name, data location.

## Coverage gaps — found and resolved (2026-06-08)
- **G1 — time-on-task:** ✅ `sessions` table records seconds per child/subject/day; dashboard
  shows total + today minutes.
- **G2 — LLM math answer keys:** ✅ math now generated deterministically (computed answers).
  See [[deterministic-math-and-proxy-bypass]].
- **G3 — mascot rename:** ✅ editable in the parent dashboard.

## Deployment & portability (2026-06-08)
See [[portability-and-deployment]] — OneDrive sync, export/import scripts, Docker one-command.

## Open questions / next
- Printable PDF worksheets at each kid's level (offered; not yet built).
- Reading/Logic ladders may need tuning once observed in real use.
- Auto-regenerate today's unserved problems after **easier** only — ✅ `content.regenerate_subject_today()` via adjust-level API. Harder still manual Prepare.
- Kid "easier" rate limit? Currently unlimited.

# Session Log: Cursor Rules for LLM Wiki

_Date: 2026-06-08_
_Related pages: [[llm-wiki-workflow]], [[modular-backend]]_

---

## Summary
User asked for Cursor rules so the agent reads `docs/wiki/` before changes and auto-updates
the wiki on major work across all projects, without needing to be reminded.

## Reasoning
- Partial wiki updates in prior sessions showed the skill alone was not enough — needed
  enforceable `alwaysApply` Cursor rules plus read-before-write workflow.
- Global rule at `~/.cursor/rules/` plus per-project `.cursor/rules/` covers both User Rules
  and repo-opened projects; template supports bootstrapping new repos.

## Actions Taken
1. Created `~/.cursor/rules/llm-wiki.mdc` (`alwaysApply: true`).
2. Created `.cursor/rules/llm-wiki.mdc` in `home-ku` and `output/HomeKumon`.
3. Created `~/.cursor/templates/project-rules/llm-wiki.mdc` for new projects.
4. Created `~/.cursor/rules/USER-RULES-SNIPPET.md` for Cursor Settings → User Rules.
5. Updated `~/.cursor/skills/llm-wiki/SKILL.md` with before/after workflow and major vs minor table.
6. Added `docs/wiki/patterns/llm-wiki-workflow.md` and updated `index.md` + `log.md`.

## Rejected Alternatives
- **Wiki update on every response including trivial Q&A** — rejected; major-only reduces noise.
- **Wiki-only in User Rules without `.mdc` files** — rejected; project rules are versionable and shareable with repos.

## Assumptions Made
- Cursor loads `~/.cursor/rules/*.mdc` globally when `alwaysApply: true` (user should verify in Settings → Rules).
- User will paste `USER-RULES-SNIPPET.md` into User Rules for belt-and-suspenders coverage.

## Insights & Observations
- Platform Engineering Hub already had `patterns/llm-wiki-workflow.md`; Home Kumon now mirrors that pattern.

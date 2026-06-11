# LLM Wiki workflow (mandatory)

## Summary
Every agent session that makes **major** code, config, or behavior changes must **read** `docs/wiki/`
before implementing and **update** it after — without the user asking. Enforced by Cursor rule
[[modular-backend]] and `~/.cursor/rules/llm-wiki.mdc`.

## When to use
- Start of any implementation task in this project.
- After features, fixes, refactors, API/schema changes, deploy work, or milestones.

## Example

**Before coding (kid session UI change):**
1. Read `docs/wiki/index.md` → `features/home-kumon-app.md`, `session-log/` for prior UX work.
2. Read `plan.md` — confirm Milestone K is shipped; don't redo K1/K2.
3. Implement only what's still open.

**After coding (modular backend refactor):**
1. Add `patterns/modular-backend.md` + `session-log/2026-06-08-modular-refactor.md`.
2. Update `architecture/home-kumon-architecture.md`, `features/home-kumon-app.md`.
3. Append `log.md`; update `index.md`.

## Anti-patterns
- ❌ Shipping code with only README changes and no wiki update on major work.
- ❌ Starting implementation without reading wiki/plan (re-does finished milestones).
- ❌ Waiting for the user to say "/ingest" or "update wiki" — update automatically.
- ❌ Manually editing `docs/raw/` — compile into `docs/wiki/` only.

## Related
- Skill: `~/.cursor/skills/llm-wiki/SKILL.md`
- Cursor: `.cursor/rules/llm-wiki.mdc`, `~/.cursor/rules/llm-wiki.mdc`
- [[home-kumon-architecture]]

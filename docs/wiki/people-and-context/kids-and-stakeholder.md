# People & Context: Kids and Stakeholder

## Summary
Who Home Kumon is for and the goals behind it. Related: [[placement-and-curriculum]],
[[home-kumon-app]].

## Date
2026-06-08

## Participants
- **Raviteja Davuluri** — parent and builder; Senior Cloud Engineer (Infrastructure), macOS,
  comfortable with venv/Docker/Python. Behind a corporate iboss proxy.
- **Nyra** — younger child, going into **2nd grade**.
- **Nivi** — older child, going into **3rd grade**.

## Decisions made
- Build a local, Kumon-style daily app rather than buy/subscribe; use the user's own LM Studio.
- Two kid profiles, auto-themed; open parent dashboard (no PIN); manual nightly prep; offline
  fallback bank; OneDrive-default data storage for auto-backup.
- Tune the app to the kids' **real** Kumon levels (both ~2 years above grade) rather than to
  their school grade — see [[placement-and-curriculum]].

## Action items
- [ ] User to run the app on the Mac (`PIP_PROXY=http://127.0.0.1:8009 ./run.sh` first time)
      and verify against real LM Studio.
- [ ] Optional: generate printable PDF worksheets at each kid's level.
- [x] Document the project in this wiki.

## Notes
- Worksheets shared were dated ~May 2025, so current levels may be higher; adaptive leveling
  will adjust from the seeded starting points.

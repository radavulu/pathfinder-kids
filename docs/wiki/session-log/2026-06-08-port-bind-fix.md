# Session Log: Port bind fix for run.sh

_Date: 2026-06-08_
_Related pages: [[home-kumon-architecture]], [[deterministic-math-and-proxy-bypass]]_

---

## Summary
Fixed startup failure when port 8000 is already in use (`[Errno 48] address already in use`).
Launchers now auto-pick the next free port so the app starts reliably on a fresh machine or
when a previous instance is still running.

## Reasoning
Hard-coding port 8000 is brittle: another Home Kumon run, Docker, or unrelated dev servers
often occupy it. Auto-selection with a clear message is safer than failing silently or
requiring manual `lsof`/kill steps on every copy-to-machine scenario.

## Actions Taken
1. Added `scripts/find_port.py` — scans 8000–8019 on the chosen host and prints the first free port.
2. Updated `run.sh` — uses `find_port.py` when `HOMEKUMON_PORT` is unset; warns when falling back.
3. Updated `run.bat` — same logic; delayed browser open until 2s after server start (was racing).
4. Updated `README.md` troubleshooting and quick-start note.

## Rejected Alternatives
- **Kill process on 8000 automatically** — rejected; could terminate unrelated services.
- **Change default port away from 8000** — rejected; docs and muscle memory already use 8000; fallback is enough.

## Problems Encountered
- **`address already in use` on 127.0.0.1:8000** — resolved by port auto-selection.

## Assumptions Made
- User runs from `output/HomeKumon` (or a synced copy); changes apply when they re-copy or pull.

## Insights & Observations
- Corporate proxy (`PIP_PROXY`) is unrelated to this error; uvicorn bound successfully but port was taken.

# PathfinderKids

A local, Kumon-style daily learning app for two children (built for ages 8 & 9). It runs
on your home computer, generates Math / Reading / Logic problems with **LM Studio**, serves
short timed daily sets, adapts difficulty as kids improve, checks answers with friendly
explanations, and rewards progress with stars, streaks, badges, and a mascot.

> Version 1.0 · Project: PathfinderKids

---

## What it does

- **Two kid profiles** with auto color themes (placeholders "Kid 1" / "Kid 2" — rename in the parent dashboard).
- **Three subjects:** Math (number keypad), Reading & Logic (tap one of 4 choices).
- **Time-based daily sets** (default 15 min/subject) — finish the current problem when time's up, or tap **"I'm done."**
- **Adaptive, forgiving leveling:** ≥80% in a session moves a child up a level; they're never moved down automatically.
- **Difficulty controls:** parent dashboard **Easier / Harder** buttons per subject; kids can tap **"Too hard?"** after a session.
- **Hybrid checking:** math is checked exactly (0.5 = 1/2); choices are checked instantly; wrong answers give a **hint → one retry → the correct answer with a kid-friendly explanation.**
- **Rewards:** a star per correct answer, daily streaks, and badges (10/50/100 stars; 3/7/30-day streaks).
- **Offline starter bank:** if LM Studio is off, kids still get age-appropriate problems.
- **Parent dashboard:** progress, accuracy, levels, **difficulty controls**, **live worksheet generation** (with on-screen timer), **reset for testing**, answer history, settings, and LM Studio configuration.

---

## Where data lives & how new sets are made

| Question | Answer |
|---|---|
| **Database?** | Yes — everything is in **SQLite** (`homekumon.db`) under **`./data`** next to the app (path shown on the parent dashboard). |
| **Docker?** | Optional. **`./run.sh`** (native Python) and **`./docker-run.sh`** (Docker) both use the **same database file** on disk via a bind mount. Use whichever you prefer. |
| **New problem sets?** | Parent clicks **Generate new sets** → the app builds **fresh problems for today** at each child's **current level**. Nothing is copied from yesterday's rows. |
| **Math** | Computed locally (always correct answers). |
| **Reading / Logic** | Generated live by **LM Studio** from the skill guide in `curriculum.py`. If LM Studio is off, the built-in **starter bank** is used instead. |
| **Old problems?** | Served from today's rows in the DB until answered or reset. The app does **not** feed old answers back into the model — only the child's **level** and **curriculum guide** steer generation. |

**After testing:** Parent dashboard → **Reset today** (clears today's session) or **Full reset** (stars, badges, history, levels back to defaults + fresh sets).

---

## Requirements

- **Python 3.10+**
- **[LM Studio](https://lmstudio.ai)** with its local server enabled and an instruct model loaded.
  - In LM Studio: **Developer → Start Server** (default `http://localhost:1234`).
  - Any small instruct model works; a 7–8B instruct model gives nicely worded problems.

---

## Quick start with Docker (recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) and LM Studio running on the host.

```bash
./docker-run.sh
```

Open **http://127.0.0.1:8700** (default port).

---

## Quick start without Docker (macOS / Linux)

```bash
./run.sh
```

Opens **http://127.0.0.1:8700** (default port in `run.sh`; override with `HOMEKUMON_PORT=8890 ./run.sh`).

**Windows:** double-click `run.bat`.

---

## First-time flow

1. Start LM Studio's server and load a model.
2. Run the app (`./docker-run.sh` or `./run.sh`).
3. Open **http://127.0.0.1:8700** → **Parent area** → **LM Studio** → **Test connection** (✓ Connected).
4. Click **Generate new sets (all kids)** — a **timer overlay** shows while LM Studio works (Math is instant; Reading/Logic ~30–90s per child).
5. Kids tap their profile and start today's set.

> If LM Studio is off, kids automatically get problems from the built-in starter bank.

---

## Move to another machine (export / import)

**Yes — it works.** All progress lives in one SQLite database file, not in the code or `.venv`.

### What to copy

| Copy | Don't copy |
|---|---|
| The whole project folder (code) | `.venv/` — always recreate with `./run.sh` |
| The `data/` folder **or** your OneDrive `…/HomeKumon/data/` | Nothing else is required |

### Option A — OneDrive (easiest)

If your data folder is under OneDrive (default on macOS), sync happens automatically. On the new Mac:

1. Install Python 3.10+ and LM Studio.
2. Open the synced project folder and run `./run.sh`.

### Option B — Manual backup file

On the **old** machine:

```bash
./scripts/export-data.sh
# creates homekumon-backup-YYYYMMDD.tar.gz
```

Copy the project folder (without `.venv`) **and** the backup file to the new machine, then:

```bash
./scripts/import-data.sh ../homekumon-backup-YYYYMMDD.tar.gz
./run.sh
```

### Option C — Docker image + data volume

Build once, run anywhere Docker is installed:

```bash
./docker-run.sh
```

Copy only the `data/` folder (or set `HOMEKUMON_DATA_DIR` to your OneDrive path before starting).

---

## Difficulty (intensity)

Each subject has a **level** (1 = easiest on that ladder, max varies by subject). The app auto-levels **up** when a child scores ≥80% in a session; it never auto-levels down.

**Parent dashboard** — on each child's card, use **Easier** / **Harder** per subject. Advanced numeric levels are under **Settings**.

**Kid view** — after finishing a subject, **"Too hard? Make it easier next time"** drops that subject by one level for the next session.

When difficulty is **lowered** (Easier or kid button), today's **unserved** problems for that subject are replaced immediately. **Harder** does not auto-refresh — use **Generate new sets** when ready.

---

## Generate worksheets (live)

Worksheets are generated **on demand for today** — no more "prepare tomorrow."

| Button | What it does |
|---|---|
| **Generate new sets (all kids)** | Refreshes today's unserved problems for every child (all 3 subjects) |
| **Generate new sets for [name]** | Same, for one child only |

A **spinner + elapsed timer** appears while LM Studio runs. Typical time: **under 5s** for math-only refresh; **1–3 minutes** for both kids with Reading/Logic if LM Studio is generating fresh content.

**Docker notes:** LM Studio runs on the **host** (not in the container). Stop: `docker compose down` · Logs: `docker compose logs -f`

To store data on OneDrive with Docker:

```bash
HOMEKUMON_DATA_DIR="$HOME/Library/CloudStorage/OneDrive-YourOrg/Documents/Cowork/HomeKumon/data" ./docker-run.sh
```

---

## Where the data lives

By default the database is stored in **`./data/homekumon.db`** — a `data` folder next to `run.sh`. The parent dashboard shows the exact path.

To use a different folder (e.g. OneDrive for cloud backup):

```bash
export HOMEKUMON_DATA_DIR="/path/to/your/data"
./run.sh
```

See `.env.example` for all optional settings.

**Already have progress in OneDrive?** Copy `homekumon.db` (and any files) from your old OneDrive `…/HomeKumon/data/` folder into `./data/`, or set `HOMEKUMON_DATA_DIR` to that old path.

---

## Configuration

All optional — see `.env.example`:

| Variable | Default | Purpose |
|---|---|---|
| `HOMEKUMON_DATA_DIR` | `./data` next to the app | Where the database lives |
| `HOMEKUMON_LMSTUDIO_URL` | `http://localhost:1234/v1` | LM Studio server (also editable in the dashboard) |
| `HOMEKUMON_LMSTUDIO_MODEL` | auto-detect loaded model | Pin a specific model |
| `HOMEKUMON_HOST` / `HOMEKUMON_PORT` | `127.0.0.1` / `8700` | Web server address |

---

## Troubleshooting

- **"Not reachable" on Test connection** → make sure LM Studio's server is running and a model is loaded.
- **Kids see repeated problems** → click **Generate new sets** while LM Studio is on.
- **Generation is slow** → normal for Reading/Logic via LM Studio; the parent dashboard shows a timer while it runs (up to 15 min). **Generate before kids start** to avoid wait. If you see a timeout, LM Studio may still be working — wait and refresh, or use **Reset today** then **Generate** again.
- **Kid session times out on first Reading/Logic question** → pull latest code (smaller first batch + longer timeout). Or run **Generate new sets** from the parent dashboard first.
- **Wrong data folder** → default is `./data` next to the app. Set `HOMEKUMON_DATA_DIR` to use another path.
- **`pip install` fails behind a corporate proxy (e.g. iboss)** → install through the proxy:
  ```bash
  PIP_PROXY=http://127.0.0.1:8009 ./run.sh
  ```
  Use your proxy's address (the iboss PAC typically points to `127.0.0.1:8009`). When `PIP_PROXY`
  is set the script also trusts the PyPI hosts, because SSL inspection re-signs the certificate and
  pip would otherwise reject it. (Windows: `set PIP_PROXY=http://127.0.0.1:8009` then `run.bat`.)
- **LM Studio won't connect behind the proxy** → the app already forces local LM Studio traffic to go
  direct (it ignores `HTTP(S)_PROXY` for localhost), and the run script sets
  `NO_PROXY=localhost,127.0.0.1`. Keep LM Studio's server on `localhost:1234` — local addresses are
  bypassed by your proxy.
- **`pip: command not found` when running `./run.sh`** → the launcher uses `.venv/bin/python -m pip`
  directly (no `pip` on PATH required). If the venv is stale or broken, remove it and retry:
  `rm -rf .venv && ./run.sh`.
- **Reading/Logic still feel too easy or too hard after changing level** → fixed in app: today's problem queue now refreshes whenever the level changes (Easier, Harder, Settings, or level-up). Restart the kid session or tap the subject again to pick up the new queue.
- **Two kids (or two browsers) at once** → supported. SQLite uses WAL mode and atomic problem claims so Nyra and Nivi can practice simultaneously without duplicate questions or "database is locked" errors.
- **`database is locked` (older installs)** → pull latest code and restart `./run.sh`; WAL + busy timeout are enabled on startup.

---

## Project layout

```
home-ku/                    # repo root — run ./run.sh from here
  app/
    main.py           App entry (startup + static mount)
    config.py         Paths, port, ./data default (HOMEKUMON_DATA_DIR override)
    db.py             SQLite schema + seeding
    schemas.py        API request models
    routes/           HTTP routers (health, pages, kid, parent, children)
    services/         Domain logic (children, generation, grading)
    content.py        Problem generation lifecycle
    starter_bank.py   Offline fallback problem bank
    curriculum.py     Subject ladders + skills
    leveling.py       Adaptive difficulty
    validation.py     Answer checking
    rewards.py        Stars + badges
    lmstudio.py       LM Studio client
    theming.py        Per-child color palettes
  web/                HTML + static JS/CSS
  data/               SQLite DB (created on first run; gitignored)
  docs/
    wiki/             Project knowledge base
    raw/placement/    Optional reference PDFs (not used at runtime)
  scripts/            export-data.sh, import-data.sh
  tests/
  run.sh / run.bat    Launchers
  docker-run.sh       Docker launcher
```

No `input/` or `output/` folders — placement research is in `docs/wiki/` and the DB seed. Reference PDFs (if kept) live under `docs/raw/placement/`.

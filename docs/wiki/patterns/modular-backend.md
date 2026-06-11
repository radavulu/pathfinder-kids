# Pattern: Modular Backend (Routes + Services)

## Summary
Split the FastAPI app into thin route handlers, reusable domain services, and extracted
data modules so each file has one job. Related: [[home-kumon-architecture]],
[[home-kumon-app]].

## When to use
- When `main.py` grows past ~200 lines with mixed HTTP, business logic, and persistence.
- When offline/static data (starter banks, seed JSON) bloats a lifecycle module like `content.py`.

## Example
```
app/
  main.py              # startup + static mount only
  schemas.py           # Pydantic request models
  routes/              # HTTP layer (FastAPI APIRouter per area)
    health.py, pages.py, children.py, kid.py, parent.py
  services/            # domain logic callable from routes
    children.py        # profile helpers
    generation.py      # worksheet generation + level adjust orchestration
    grading.py         # answer check + kid feedback payloads
  content.py           # generation lifecycle (LM Studio → DB)
  starter_bank.py      # offline fallback problems (no HTTP imports)
```

**Rules:**
- Routes open/close DB connections; services receive an open `sqlite3.Connection`.
- Services must not import FastAPI except `HTTPException` in thin lookup helpers.
- Static/offline banks live in their own module; lifecycle code imports a public function
  (e.g. `starter_batch()`), not private bank dicts.

## Anti-patterns
- ❌ Keeping 400+ lines of endpoints + grading + generation in one `main.py`.
- ❌ Importing route modules from services (creates circular imports).
- ❌ Shipping reference PDFs in an `input/` folder the runtime never reads — archive findings
  in [[placement-and-curriculum]] and seed the DB instead.

# Architecture — Strategy B (Structured Context)

**Method note:** written from `AGENTS.md`'s content plus a one-line summary of each backend file
(not the full file contents) — richer than Strategy A, but still a curated summary rather than
reading the actual source.

Context provided:
- `AGENTS.md` (stack, commands, project rules, do-not list — see repo root)
- File summaries: `app/main.py` "FastAPI app + 5 CRUD routes + /health"; `app/models.py`
  "TaskCreate/TaskUpdate/TaskResponse + status/priority enums"; `app/storage.py` "in-memory dict
  storage"; `app/business_rules.py` "status-transition validation"; `frontend/index.html` "Kanban
  board, single file, vanilla JS"

## What the app does

A FastAPI Task Tracker with a vanilla-JS Kanban frontend. No database — `AGENTS.md` states
storage is in-memory. Confirmed via context, not assumed.

## Data model

`TaskCreate`, `TaskUpdate`, `TaskResponse` Pydantic models (per the `app/models.py` summary), with
`TaskStatus` (`ToDo`/`InProgress`/`Done`) and `TaskPriority` (`Low`/`Medium`/`High`) enums per
`AGENTS.md`. `AGENTS.md` also mentions `due_date` and `tags` fields and a computed `is_overdue` —
included here, though I have not seen the exact validation rules (max tag count, max length, etc.)
since that level of detail isn't in the one-line summary or `AGENTS.md`'s condensed business-rules
section.

## Request flow

Client → `POST/GET/PATCH/DELETE /tasks[/{id}]` → Pydantic validation → `app/storage.py`'s
in-memory dict → response. Status changes go through `app/business_rules.py`'s transition
validation per `AGENTS.md`, which states same-status transitions are invalid — a specific,
non-generic rule that Strategy A had no way to know about.

## Key files

- `app/main.py` — FastAPI app, CORS config, 5 CRUD routes + `/health` (per summary + `AGENTS.md`)
- `app/models.py` — Pydantic models + enums
- `app/storage.py` — in-memory dict + CRUD helpers
- `app/business_rules.py` — status-transition validation
- `frontend/index.html` — Kanban board, single file, vanilla JS/HTML/CSS, no framework
- `tests/` — pytest suite (`conftest.py`, `test_tasks.py`, `test_midcourse_features.py` per
  `AGENTS.md`'s architecture section)

## Conventions

`AGENTS.md` states: use `python -m pytest`, not bare `pytest` (CI-relevant); CORS allows a fixed
small set of local origins; no auth, no database. These are specific enough to be useful and are
attributed to `AGENTS.md` rather than inferred from "typical FastAPI project" patterns.

## Not visible / assumptions

The one-line file summaries don't include exact status codes per route, exact validation limits
(e.g. tag count/length maximums), or the exact CORS origin list — `AGENTS.md`'s prose covers some
of this but not at the same precision as reading `app/main.py`/`app/models.py` directly would.
Where `AGENTS.md` was silent (e.g. exact HTTP status per route), this doc doesn't guess.

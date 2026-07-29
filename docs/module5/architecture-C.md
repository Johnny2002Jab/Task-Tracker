# Architecture — Strategy C (Targeted Context)

**Method note:** limited strictly to `app/main.py`, `app/models.py`, and `app/storage.py` — no
`AGENTS.md`, no frontend, no tests, no CI config. Anything about those other areas is marked "not
visible from the files I read" rather than inferred.

## What the app does

A FastAPI REST API for tasks, exposing `POST /tasks`, `GET /tasks`, `GET /tasks/{id}`,
`PATCH /tasks/{id}`, `DELETE /tasks/{id}`, and `GET /health` (`app/main.py`, decorators read
directly). Whether there's a frontend, and what it looks like, is **not visible from the files I
read** — nothing in these three files renders UI.

## Data model

From `app/models.py` directly:
- `TaskStatus(str, Enum)`: `ToDo`, `InProgress`, `Done`.
- `TaskPriority(str, Enum)`: `Low`, `Medium`, `High`.
- `TaskCreate`: `title` (required, trimmed, 1-200 chars via a `field_validator`), `description`
  (optional, default `""`), `status` (default `ToDo`), `priority` (default `Medium`), `assignee`
  (optional), `due_date` (optional `date`), `tags` (`list[str]`, validated by a shared
  `_normalize_tags` helper: max 10 tags, max 30 chars each, blank tags rejected, case-insensitive
  dedup). All input models use `ConfigDict(extra="forbid")` — unknown fields are rejected.
- `TaskUpdate`: same fields, all optional, same validators applied only when a field is given.
- `TaskResponse`: adds `id`, `created_at`, `updated_at`, and a `@computed_field` property
  `is_overdue` — computed as `due_date < date.today() and status != Done`, not stored.

## Request flow

`app/main.py`'s `update_task` (`PATCH`) reads as: reject an empty update body (422) → if `status`
is being changed, fetch the existing task (404 if missing) and call
`validate_status_transition` (imported from `app.business_rules`, not read as part of this
strategy) → apply the update via `app/storage.py`'s `update_task` → return the result (404 if the
task disappeared between the two calls, though nothing in these three files shows how that race
would occur in practice given no concurrency is visible here).

## Key files

Only the three read for this strategy:
- `app/main.py` — routes, CORS middleware (`allow_origins` is a fixed list including
  `http://localhost:5500`, `http://127.0.0.1:5500`, `http://localhost:5173`, and the literal
  string `"null"`).
- `app/models.py` — models, enums, validators (detailed above).
- `app/storage.py` — a module-level `_tasks: dict[str, TaskResponse]`, with `add_task`,
  `get_all_tasks` (filters: `status`, `priority`, `overdue`, `tag` — all optional, combine with
  AND), `get_task_by_id`, `update_task` (uses `payload.model_dump(exclude_unset=True)`),
  `delete_task`, and a test-only `_reset()`.

Whether there's a `business_rules.py`, a `frontend/`, a `tests/` directory, a CI config, or a
Dockerfile is **not visible from the files I read** for this strategy — `app/main.py` imports
`from app.business_rules import validate_status_transition`, so that module must exist, but its
contents were not part of this read.

## Conventions

Consistent 404 message format (`f"Task with id {task_id} not found"`) across all three routes
that can 404. `TaskUpdate`'s partial-update semantics rely on Pydantic's `exclude_unset`, visible
directly in `app/storage.py`.

## Not visible / assumptions

Everything about the frontend, the test suite, CI, Docker, and the exact transition rules inside
`business_rules.py` is not visible from the three files this strategy was scoped to. No guesses
were made to fill those gaps.

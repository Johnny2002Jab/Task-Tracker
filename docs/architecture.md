# Task Tracker — Architecture

Built by combining the strongest parts of three context-engineering strategies run against the
same task (see `docs/module5/architecture-A.md`, `-B.md`, `-C.md` for the raw outputs and
`docs/module5/context-engineering-comparison.md` for the comparison log this document is based
on). This version favors Strategy C's file-level precision, filled in with Strategy B's
system-level framing where C had no visibility (frontend, tests, CI).

## System overview

A FastAPI Task Tracker backend (in-memory storage, no database) paired with a single-file vanilla
JS/HTML/CSS Kanban frontend (`frontend/index.html`). No authentication, no
persistence beyond process lifetime — see `docs/decisions/in-memory-task-storage.md` for why.

## Backend structure

- `app/main.py` — FastAPI app, CORS middleware (fixed local-origin allowlist including the
  literal `"null"` origin for `file://` access), and five CRUD routes + `/health`.
- `app/models.py` — `TaskCreate`/`TaskUpdate`/`TaskResponse`, `TaskStatus`/`TaskPriority` enums,
  and validation: `title` (1-200 chars, trimmed), `tags` (max 10, 30 chars each, case-insensitive
  dedup, blank rejected), `due_date` (optional calendar date), computed `is_overdue`. All input
  models reject unknown fields (`extra="forbid"`).
- `app/storage.py` — a single in-memory dict (`_tasks`), with filterable `get_all_tasks`
  (`status`/`priority`/`overdue`/`tag`, AND-combined) and a test-only `_reset()`.
- `app/business_rules.py` — `validate_status_transition`; only `ToDo→InProgress`,
  `InProgress→Done`, `Done→InProgress` are valid (same-status included as invalid).

## Frontend structure

`index.html` renders three status columns, sorted by priority within each; fetches via
`GET /tasks` with query-string filters; drags-and-drops via optimistic-update `PATCH` with
rollback on rejection; and a create/edit modal that (as of the mid-course checkpoint) only sends
`status` in the `PATCH` body when it actually changed, to avoid tripping the same-status-invalid
rule on unrelated edits.

## Data flow

Frontend or `curl` → FastAPI route → Pydantic validation (422 on failure) → for status changes,
`business_rules.validate_status_transition` (422 on an invalid transition) → `storage.py`'s dict →
JSON response, including the computed `is_overdue` field.

## Testing and verification

`tests/conftest.py` (client + `created_task` fixtures, autouse storage reset),
`tests/test_tasks.py` (core CRUD + business rules), `tests/test_midcourse_features.py`
(due-date/overdue + tags). CI (`.github/workflows/ci.yml`) runs `python -m pytest -v` on push/PR —
note the `python -m` is load-bearing, not stylistic; see `docs/module4/claim-vs-reality.md`.

## Known limits

No database (in-memory only, data lost on restart), no auth, `description`/`assignee` are
unbounded strings (see `docs/module5/security-review.md`), Docker image is authored but not
build/run-verified in this environment.

## Context-strategy verdict

Strategy C (targeted: `main.py`/`models.py`/`storage.py` only) produced the most accurate
file-level detail and was the most honest about what it hadn't seen. Strategy B (structured:
`AGENTS.md` + one-line summaries) was the most complete system-level picture with the least
effort, at the cost of some imprecision (e.g. it couldn't state the exact tag limits). Strategy A
(minimal) was the fastest but invented a database that doesn't exist — the one real error among
the three, and the one a security- or correctness-sensitive task can't afford.

**Rule:** for architecture/onboarding docs where completeness matters most, use structured context
(B); for anything correctness-sensitive — security review, business-rule documentation, a change
that will be trusted without independent verification — use targeted context (C), because an
honest "not visible from what I read" beats a fluent guess.

# CLAUDE.md

Project memory for Claude Code sessions working in this repository. Correct this file by hand
whenever the code changes underneath it — do not let it drift into a generic FastAPI description.

## Stack

- Backend: Python 3.13, FastAPI 0.115.0, Pydantic v2 (2.9.2), Uvicorn 0.30.6, python-dotenv 1.0.1.
- Tests: pytest 9.1.1, httpx 0.28.1 (used via FastAPI's `TestClient`).
- Frontend: vanilla HTML/CSS/JavaScript in `task-tracker/frontend/index.html`. No framework, no
  build step.
- Storage: in-memory Python dict (`app/storage.py`). No database. Data is lost on backend restart.

## Run and test commands

Run from `task-tracker/backend/` with the venv activated (or via `venv/Scripts/python.exe` on
Windows without activating):

```
uvicorn app.main:app --reload --port 8000       # backend, http://localhost:8000
pytest tests/ -v                                 # full test suite
```

Frontend: serve `task-tracker/frontend/` with a static file server on port 5500, e.g.:

```
python -m http.server 5500                       # from task-tracker/frontend/
```

Then open `http://localhost:5500/index.html`. The frontend calls the backend at
`http://localhost:8000` (hardcoded `baseUrl` in `index.html`).

## Architecture

```
task-tracker/
├── backend/
│   ├── app/
│   │   ├── main.py            FastAPI app, CORS config, 5 CRUD routes + /health
│   │   ├── models.py           TaskCreate/TaskUpdate/TaskResponse, TaskStatus/TaskPriority enums
│   │   ├── storage.py          in-memory _tasks dict + add/get/update/delete/_reset
│   │   └── business_rules.py   VALID_TRANSITIONS + validate_status_transition
│   ├── tests/
│   │   ├── conftest.py         client fixture, created_task fixture, autouse storage reset
│   │   ├── test_tasks.py       core CRUD + business-rule tests
│   │   └── test_midcourse_features.py   due-date/overdue and tags tests
│   └── requirements.txt
└── frontend/
    └── index.html              Kanban board, modal, drag-and-drop, filters — all in one file
```

## Business rules (verify against code before trusting this section)

- `TaskStatus`: `ToDo`, `InProgress`, `Done`. `TaskPriority`: `Low`, `Medium`, `High`.
- Status transitions (`app/business_rules.py`): only `ToDo->InProgress`,
  `InProgress->Done`, `Done->InProgress` are valid. Same-status and any other pair (including
  `ToDo->Done` and `Done->ToDo`) return HTTP 422.
- `PATCH /tasks/{id}` with an empty JSON body (`{}`) returns HTTP 422 — at least one field must be
  set.
- `due_date` is an optional calendar date (no time-of-day). `is_overdue` is a **computed** field
  (not stored): true only when `due_date` is in the past **and** status is not `Done`.
- `tags` is a `list[str]`, trimmed and case-insensitively de-duplicated, max 10 tags, max 30
  characters per tag. Blank tags are rejected with HTTP 422.
- `GET /tasks` supports combinable query filters: `status`, `priority`, `overdue` (bool), `tag`
  (case-insensitive substring match against a task's tag list).
- Title is required, trimmed, 1–200 characters, on both create and update.

## Frontend UI states and behavior

- Kanban board: three columns (`ToDo`/`InProgress`/`Done`), cards sorted High→Medium→Low priority
  (tie-break by id).
- Four board states: loading, ready, empty (per column), error (with Retry button).
- Drag-and-drop sends `PATCH /tasks/{id}` with `{"status": ...}`; optimistic update with rollback
  and an error banner on a rejected/failed move.
- Create/edit modal: title required after `.trim()`; PATCH only includes `status` in the payload
  when the user actually changed it (this is load-bearing — see business rules above; sending the
  unchanged status on every edit previously caused false 422s).
- Filter bar: tag text filter + "overdue only" checkbox, both applied server-side via query params.

## CORS

`app/main.py` allows exactly: `http://localhost:5500`, `http://127.0.0.1:5500`,
`http://localhost:5173`, and `"null"` (covers opening the frontend directly via `file://`).
Do not add origins beyond local dev without being asked.

## Do-not rules

- No authentication, user accounts, or multi-tenancy.
- No real database or persistence layer — storage is intentionally in-memory for this learning
  project.
- No production deployment steps beyond what a Module 4 Dockerfile/CI workflow requires.
- Do not modify `app/` or `frontend/` for documentation-only or DevOps tasks; if a fix there is
  genuinely required, call it out explicitly and explain why.
- Do not weaken or delete existing tests to make them pass — fix the source, or explain why the
  test's expectation was wrong.
- Do not add frameworks, bundlers, or new dependencies to the frontend.

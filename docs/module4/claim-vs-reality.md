# Claim vs. Reality — Documentation Audit

Checked README.md and docstring claims against the actual running backend (`curl` against
`http://localhost:8000`) and, where noted, flagged what could not be verified in this environment.

| Claim | Evidence used | Result | Change made |
|---|---|---|---|
| `POST /tasks` returns 201 Created | `curl -X POST /tasks` with a valid body | Confirmed: `HTTP:201` | None needed |
| `DELETE /tasks/{id}` returns 204 with no body | `curl -X DELETE` on an existing id, checked body byte count | Confirmed: `HTTP:204`, 0 body bytes | None needed |
| `DELETE`/`GET` on a missing id returns 404 with a detail message | `curl -X DELETE /tasks/does-not-exist` | Confirmed: `HTTP:404`, `{"detail":"Task with id does-not-exist not found"}` | None needed |
| `GET /tasks` with a filter that matches nothing returns 200 with `[]`, not 404 | `curl "/tasks?status=Done&priority=Low&tag=zzz-no-match"` | Confirmed: `HTTP:200`, body `[]` | None needed |
| Invalid enum value (e.g. `priority: "Urgent"`) returns 422 | `curl -X POST` with `"priority":"Urgent"` | Confirmed: `HTTP:422` with a Pydantic enum validation detail | None needed |
| `GET /health` returns `{"status":"ok","timestamp":...}` | `curl /health` | Confirmed | None needed |
| README's exact backend run command (`uvicorn app.main:app --reload --port 8000`) starts a working server | Started the server with this exact command, then ran the checks above against it | Confirmed | None needed |
| README's `pytest tests/ -v` invocation matches what CI actually needs | Compared against `.github/workflows/ci.yml`, which runs `python -m pytest -v` | **Mismatch found**: bare `pytest` (no `-m`) does not add the backend directory to `sys.path`, which is exactly what caused the first two CI runs to fail with `ModuleNotFoundError: No module named 'app'` (see CI red/green evidence). Local runs happened to work because `python -m pytest` was always used. | Fixed `ci.yml` to use `python -m pytest -v`; recommend using the same form in README/local instructions to avoid confusion. |
| Dockerfile builds a working image, runs as non-root (`docker exec ... whoami` → `app`), and responds to `/health` | N/A | **Not verified in this environment** — Docker is not installed/available here. The Dockerfile follows the required shape (multi-stage, `python:3.13-slim` runtime, `USER app` before `CMD`, no secrets copied), but the build/run/health/whoami checks described in the README have not actually been executed. | Documented as an open verification item rather than claimed as done. |

## Summary

Five of seven checked claims about API behavior were confirmed directly against the running
backend. One real inaccuracy was found and fixed: the README's test command and the CI
workflow's test command were inconsistent in a way that actually broke CI (see
`docs/module4/ai-review-log.md` and the CI run history on the `mid-course-project` branch for the
full green → red → green sequence). The Docker claims are written to spec but not run-verified
here, since this environment has no Docker daemon — that is called out explicitly rather than
asserted as tested.

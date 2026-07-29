# Release Evidence

## Baseline

- Branch: `final-project`
- Date: 2026-07-29
- Local app run command: `cd task-tracker/backend && venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000` (or `uvicorn app.main:app --reload --port 8000` with the venv activated)
- `/health` result: `HTTP 200`, `{"status":"ok","timestamp":"2026-07-29T17:46:10.454923+00:00"}`
- Frontend check: served `task-tracker/frontend/index.html` via `python -m http.server 5500`;
  `HTTP 200` on load; page contains the Kanban board title, "New Task" button, and the create/edit
  modal form markup (`taskModalForm`) — the board and modal are intact on this branch.
- Test command: `cd task-tracker/backend && ./venv/Scripts/python.exe -m pytest -v`
- Test result: **36 passed**, 0 failed (full suite: `test_tasks.py` + `test_midcourse_features.py`)

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest green run on `final-project`:
  https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30476792079 (commit `642756f`,
  status: success)
- Test command used by CI: `python -m pytest -v` (run from `task-tracker/backend`, per the
  workflow's `working-directory` default)
- Shortcut check: confirmed no `continue-on-error`, no `|| true`, no `--exit-zero`, pytest is not
  skipped or piped through anything that would hide its exit code; Python version is pinned
  (`"3.13"`, not `latest`); triggers cover `push` (all branches) and `pull_request` to `main`.
- Intentional red-run evidence (produced during Module 4, on this same branch history, so it
  still applies): green → https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30473998802
  → intentional red (status-transition validation temporarily disabled) →
  https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30474140944 (failed as expected,
  exit code 1, the two transition tests failing) → restored green →
  https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30474292565. Full narrative in
  `docs/module4/claim-vs-reality.md` and the commit history around that date.

## Docker evidence

- Build command: `docker build -t task-tracker:dev .`
- Run command: `docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev`
- `/health` check: `curl -i http://localhost:8000/health`
- Non-root check: `docker exec tt-dev whoami` (expected: `app`)
- No-baked-secrets check: `.dockerignore` excludes `.env`, `.git`, `venv/`, caches, and build
  artifacts; the `Dockerfile` only ever `COPY`s `task-tracker/backend/requirements.txt` and
  `task-tracker/backend/app`, never a broad `COPY . .`, so nothing outside those two paths could
  end up in the image regardless of `.dockerignore`.

**Status: NOT independently verified in this environment.** There is no Docker daemon available
here (`docker --version` → `command not found`), so the build/run/health/whoami sequence above has
never actually been executed — only authored to the required shape (multi-stage, `python:3.13-slim`
runtime, `USER app` before `CMD`, no secrets copied). This is stated plainly rather than implied as
done; see `docs/module4/claim-vs-reality.md` for the same caveat recorded earlier. **Action for
you:** run the four commands above locally (with Docker installed) and update this section with
the real output before treating Docker as verified.

## Documentation claim-vs-reality log

Full log (8 claims checked) is in `docs/module4/claim-vs-reality.md`. Summary of the three most
relevant to release readiness:

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| `POST /tasks` returns 201, `DELETE` returns 204 with no body, invalid input returns 422 | Live `curl` against a running backend | Confirmed for all three | None needed |
| README's test command matches what CI actually runs | Compared README's documented command against `.github/workflows/ci.yml` | **Mismatch found and fixed**: README/local usage always used `python -m pytest`, but CI originally ran bare `pytest`, which doesn't add the backend directory to `sys.path` — the actual cause of the first two CI failures (see red-run evidence above) | Fixed `ci.yml` to use `python -m pytest -v`, matching the README |
| Dockerfile builds a working, non-root image | N/A | Not verified in this environment (see Docker evidence section above) | Documented as an open item, not claimed as done |

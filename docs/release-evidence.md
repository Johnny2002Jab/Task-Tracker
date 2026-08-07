# Release Evidence

## Repository structure fix (resubmission)

Grading feedback on the first submission flagged that `app/`, `frontend/`, and `tests/` lived under
`task-tracker/backend/` and `task-tracker/frontend/` instead of the required top level. Fixed by
moving all three (plus `requirements.txt`) to the repo root via `git mv` (history preserved),
removing the now-redundant `task-tracker/backend/README.md` and `.gitignore` (superseded by the
root versions), and updating `.github/workflows/ci.yml` (dropped the `working-directory` default)
and `Dockerfile` (`COPY` paths no longer prefixed with `task-tracker/backend/`). The baseline below
was re-run after the move, against the new paths, not carried over from the old structure.

## Baseline

- Branch: `final-project`
- Date: 2026-08-06 (re-verified after the structure fix above; original baseline was 2026-07-29
  under the old `task-tracker/backend/` paths)
- Local app run command: `venv/Scripts/python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000` (or `uvicorn app.main:app --reload --port 8000` with the venv activated), run from the repo root
- `/health` result: `HTTP 200`, `{"status":"ok","timestamp":"2026-08-06T06:51:36.774436+00:00"}`
- Frontend check: served `frontend/index.html` via `python -m http.server 5500` from `frontend/`;
  `HTTP 200` on load; page contains the "New Task" button and the create/edit modal form markup
  (`taskModalForm`) — the Kanban board and create/edit flow are still visible on this branch.
- Test command: `./venv/Scripts/python.exe -m pytest -v`, run from the repo root
- Test result: **36 passed**, 0 failed (full suite: `test_tasks.py` + `test_midcourse_features.py`)

## CI evidence

- Workflow file: `.github/workflows/ci.yml`
- Latest green run on `final-project`, after the repository structure fix:
  https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/31078901336 (commit `82e4803`,
  status: success — `test` job 14s, `docker` job 19s, both on the new root-level `app`/`tests`
  layout). Earlier green run on the pre-fix structure, kept for history:
  https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30476792079 (commit `642756f`).
- Test command used by CI: `python -m pytest -v` (run from the repo root; the workflow no longer
  sets a `working-directory` default, since `app/`/`tests/` now live at the repo root)
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
  artifacts; the `Dockerfile` only ever `COPY`s `requirements.txt` and `app` (both now at the repo
  root), never a broad `COPY . .`, so nothing outside those two paths could end up in the image
  regardless of `.dockerignore`.

**Local status: genuinely unavailable, not just unverified.** This dev environment has no Docker
daemon and no Docker Desktop install at all (`docker --version` → command not found, and
`Test-Path "C:\Program Files\Docker\Docker\Docker Desktop.exe"` → `False`), so the four commands
above have never been run by hand here. Rather than leave that as an open item indefinitely (as it
was through Module 4 and Module 5 — see `docs/ai-playbook.md`, "What I am still figuring out"),
the same build/run/health/whoami sequence was added as a real job (`docker`) in
`.github/workflows/ci.yml`, which runs on GitHub's `ubuntu-latest` runners — these ship Docker
preinstalled, so it actually executes there instead of only being authored to the right shape.

- Docker CI job: `.github/workflows/ci.yml`, job `docker` (depends on `test` passing first)
- Latest run, on the current root-level layout:
  https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/31078901336 (commit `82e4803`) —
  **both jobs succeeded**: `test` in 14s, `docker` in 19s. The `docker` job's cleanup step
  (`docker stop`) is the only one with `continue-on-error`; the build, run, `/health` poll, and
  non-root check all had to pass for the job itself to report success. First-ever green run of this
  job (on the pre-restructure layout), kept for history:
  https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30908665181 (commit `2e7068b`).
- What it verifies, on a real container, on every push/PR: image builds, container starts, `/health`
  returns 200 within 15s (polled), `docker exec ... whoami` returns `app` (non-root)
- This does not replace running it on your own machine before a real release — it proves the image
  is genuinely buildable and runnable by *someone*, not that it works on any specific developer's
  Windows/Docker Desktop setup. If you have Docker installed locally, still run the four commands
  above once and confirm the same result.

## Documentation claim-vs-reality log

Full log (8 claims checked) is in `docs/module4/claim-vs-reality.md`. Summary of the three most
relevant to release readiness:

| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| `POST /tasks` returns 201, `DELETE` returns 204 with no body, invalid input returns 422 | Live `curl` against a running backend | Confirmed for all three | None needed |
| README's test command matches what CI actually runs | Compared README's documented command against `.github/workflows/ci.yml` | **Mismatch found and fixed**: README/local usage always used `python -m pytest`, but CI originally ran bare `pytest`, which doesn't add the backend directory to `sys.path` — the actual cause of the first two CI failures (see red-run evidence above) | Fixed `ci.yml` to use `python -m pytest -v`, matching the README |
| Dockerfile builds a working, non-root image | CI `docker` job: real build, run, `/health` poll, `whoami` check on GitHub's runner (no Docker daemon available locally to check this by hand) | **Confirmed** via CI run [31078901336](https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/31078901336) — image builds, `/health` returns 200, container runs as `app` | Added the `docker` job to `ci.yml` so this claim has a real run behind it instead of being an unverified assumption (see Docker evidence section above) |

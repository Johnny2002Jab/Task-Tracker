# Task-Tracker

A FastAPI + vanilla JS Kanban task tracker, built across Modules 1-3 and extended with a
mid-course checkpoint (due dates/overdue filtering and tags/labels — see
[docs/midcourse/](docs/midcourse/)).

## Final Project

Branch reviewed: `final-project`

### What this submission demonstrates

- The existing Task Tracker app still runs and stays inside the intended course scope — no new
  product features were added on this branch.
- CI runs the pytest suite on push and pull request (see `.github/workflows/ci.yml`), with a full
  green → intentional red → restored green proof already on this branch's history (Module 4).
- A Docker image is authored (multi-stage, non-root) but **not build/run-verified** in this
  environment — no Docker daemon was available. See `docs/release-evidence.md` for exactly what
  was and wasn't checked.
- AI review, security, and ownership evidence is in `docs/final-ai-review.md`, `docs/module4/`,
  and `docs/module5/`.

### How to run locally

```bash
cd task-tracker/backend
python -m venv venv        # first time only
venv\Scripts\Activate.ps1  # Windows PowerShell; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### How to run tests

```bash
cd task-tracker/backend
python -m pytest -v
```

### How to run with Docker

```bash
docker build -t task-tracker:dev .
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl -i http://localhost:8000/health
docker exec tt-dev whoami   # expect "app", not "root"
docker stop tt-dev
```

### Evidence files

- [docs/release-evidence.md](docs/release-evidence.md)
- [docs/final-ai-review.md](docs/final-ai-review.md)
- [docs/ai-playbook.md](docs/ai-playbook.md)

### AI assistance summary

AI helped draft or review: the due-dates/tags features, CI workflow, Dockerfile, docstrings,
README, security review, governance worksheet, and technical decision notes.

I verified the work by: running the full pytest suite (36/36) before and after each change,
curl-testing every documented API claim against a running backend, and pushing the CI workflow
to actually watch it pass, fail on an intentional break, and pass again — not by reading the YAML
and assuming it was correct.

One AI suggestion I rejected or corrected: an early backend-only fix for a status-transition bug
silently weakened a documented business rule; it was replaced with a frontend-side fix that kept
the rule strict (full story in `docs/final-ai-review.md`).

## Run the backend

```bash
cd task-tracker/backend
python -m venv venv        # first time only
venv\Scripts\Activate.ps1  # Windows PowerShell; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs
- Health check: `curl http://localhost:8000/health`

Storage is in-memory only — restarting the backend clears all tasks.

## Open the frontend

The frontend is a static `index.html` that calls the backend at `http://localhost:8000`, so it
must be served (not opened via `file://`) from an origin the backend's CORS config allows
(`http://localhost:5500`, `http://127.0.0.1:5500`, or `http://localhost:5173`):

```bash
cd task-tracker/frontend
python -m http.server 5500
```

Then open http://localhost:5500/index.html in a browser, with the backend already running.

## Run the tests

```bash
cd task-tracker/backend
venv\Scripts\python.exe -m pytest tests/ -v
```

## Run with Docker

```bash
docker build -t task-tracker:dev .
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl -i http://localhost:8000/health
docker exec tt-dev whoami   # expect "app", not "root"
docker stop tt-dev
```

The image is a multi-stage build (`Dockerfile`) with a `python:3.13-slim` runtime, a non-root
`app` user, and no `.env`/secrets copied in (see `.dockerignore`). It serves the backend only —
the frontend is still served separately as a static file (see above).

## Continuous integration

`.github/workflows/ci.yml` runs the full pytest suite on every push and on pull requests to
`main`, using the same `python -m pytest -v` command as the local test instructions above, on a
pinned Python 3.13. No `continue-on-error`, `|| true`, or similar failure-swallowing shortcuts —
a failing test fails the workflow.

## Project docs

- [task-tracker/backend/README.md](task-tracker/backend/README.md) — backend-specific setup notes
- [CLAUDE.md](CLAUDE.md) — project memory for Claude Code sessions: stack, commands, business
  rules, and do-not boundaries
- [docs/midcourse/](docs/midcourse/) — mid-course checkpoint deliverables: user stories,
  mini-ADR, prompt log, verification log, and reflection for the due-dates/overdue and
  tags/labels features
- [docs/decisions/in-memory-task-storage.md](docs/decisions/in-memory-task-storage.md) —
  technical decision note (Module 4): why storage is still an in-memory dict, not a database
- [docs/module4/](docs/module4/) — Module 4 evidence: documentation claim-vs-reality audit and
  AI-assisted code review log
- [AGENTS.md](AGENTS.md) — repo guardrails for agentic AI tools (Module 5)
- [docs/module5/](docs/module5/) — Module 5 evidence: security review, governance worksheet,
  comments-feature planning comparison, and context-engineering comparison
- [docs/decisions/comments-feature-plan.md](docs/decisions/comments-feature-plan.md) — planning
  only, not implemented (Module 5)
- [docs/architecture.md](docs/architecture.md) — system architecture overview (Module 5)
- [docs/ai-playbook.md](docs/ai-playbook.md) — personal AI usage playbook
- [docs/release-evidence.md](docs/release-evidence.md) — Final Project: baseline, CI, Docker, and
  documentation verification evidence
- [docs/final-ai-review.md](docs/final-ai-review.md) — Final Project: condensed AI review,
  security review, and ownership statement

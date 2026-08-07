# Task-Tracker

Branch reviewed: `final-project`

### What this submission demonstrates

- The existing Task Tracker app still runs and stays inside the intended course scope — no new
  product features were added on this branch.
- CI runs the pytest suite on push and pull request (see `.github/workflows/ci.yml`), with a full
  green → intentional red → restored green proof already on this branch's history (Module 4).
- A Docker image is authored (multi-stage, non-root) and build/run/health-verified via a dedicated
  `docker` job in CI (no Docker daemon is available in the local dev environment, so this runs on
  GitHub's runner instead — see `docs/release-evidence.md` for the real run link).
- AI review, security, and ownership evidence is in `docs/final-ai-review.md`, `docs/module4/`,
  and `docs/module5/`.
- Repo layout is now the flat, required top-level shape: `app/`, `frontend/`, `tests/` at the repo
  root (moved from `task-tracker/backend/` and `task-tracker/frontend/` after grading feedback
  flagged the nested structure — CI and Docker paths were updated to match, not just the docs).

### How to run locally

python -m venv venv        
venv\Scripts\Activate.ps1 
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

### How to run tests

python -m pytest -v

### How to run with Docker

docker build -t task-tracker:dev .
docker run --rm -d -p 8000:8000 --name tt-dev task-tracker:dev
curl -i http://localhost:8000/health
docker exec tt-dev whoami  
docker stop tt-dev

### Evidence files

- [docs/release-evidence.md](docs/release-evidence.md)
- [docs/final-ai-review.md](docs/final-ai-review.md)
- [docs/ai-playbook.md](docs/ai-playbook.md)

### AI assistance summary

AI helped draft or review: the due-dates/tags features, CI workflow, Dockerfile, docstrings,
README, security review, governance worksheet, technical decision notes, the CI-based Docker
build/run/health job, and the repo structure fix (`task-tracker/backend/` → repo root).

I verified the work by: running the full pytest suite (36/36) before and after each change,
curl-testing every documented API claim against a running backend, and pushing the CI workflow
to actually watch it pass, fail on an intentional break, and pass again — not by reading the YAML
and assuming it was correct. After the structure fix, re-ran the same checks (pytest, `/health`,
frontend serve) from the new root paths rather than assuming the move didn't break anything, and
watched two full CI runs (`test` + `docker` jobs) go green on the new layout before considering it
done.

One AI suggestion I rejected or corrected: an early backend-only fix for a status-transition bug
silently weakened a documented business rule; it was replaced with a frontend-side fix that kept
the rule strict (full story in `docs/final-ai-review.md`).

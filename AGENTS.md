# AGENTS.md

Repo-level guidance for AI agents working in this repository during Module 5 (security review,
governance, feature planning, context engineering) and beyond.

**Tool note:** Module 5's exercises are written around OpenAI's Codex App (desktop UI with a
project sidebar, thread workspace, and review pane). This repo's Module 5 work was actually done
with Claude Code instead, since that's the agent available in this environment. Every Module 5
doc under `docs/module5/` says so explicitly rather than implying a tool that wasn't used. The
guardrails below apply regardless of which agent is reading this file.

## Stack and commands

- Backend: Python 3.13, FastAPI 0.115.0, Pydantic v2, Uvicorn, in-memory storage. No database.
- Install: `cd task-tracker/backend && pip install -r requirements.txt`
- Run: `uvicorn app.main:app --reload --port 8000` (from `task-tracker/backend/`)
- Test: `python -m pytest -v` (from `task-tracker/backend/`) — **must** use `python -m pytest`,
  not bare `pytest`; see `docs/module4/claim-vs-reality.md` for why the bare form breaks on Linux.
- Frontend: static file, `python -m http.server 5500` from `task-tracker/frontend/`, then open
  `index.html`. No build step, no framework.
- CI: `.github/workflows/ci.yml`, runs the test command above on push/PR.
- Docker: `Dockerfile` + `.dockerignore` at repo root (multi-stage, non-root `app` user).

## Project rules

- Task fields: `title`, `description`, `status` (`ToDo`/`InProgress`/`Done`), `priority`
  (`Low`/`Medium`/`High`), `assignee`, `due_date`, `tags`.
- Status transitions are restricted — see `app/business_rules.py`. Same-status "transitions" are
  invalid.
- `is_overdue` is computed at read time, never stored.
- No authentication, no user accounts, no production database. This is a learning project;
  those are deliberate scope exclusions, not oversights — see `docs/decisions/` for the reasoning
  behind storage-layer choices specifically.
- Full architecture and business-rule detail lives in `CLAUDE.md` — read that first for anything
  code-level.

## Module 5 boundaries

- Default to read-only analysis. Security review, governance worksheet, feature planning, and
  context-engineering exercises should not modify `app/` or `frontend/`.
- Any required edit to `app/` or `frontend/` (e.g. a one-line security fix) must be explained in
  the relevant `docs/module5/` file: what was found, why it's real, and why the fix is minimal.
- Module 5 deliverables live under `docs/module5/`, `docs/decisions/`, and `docs/ai-playbook.md`.
  This module does not add a new product feature (comments planning is plan-only, never
  implemented).

## Review expectations

- Cite real files and line numbers for every claim about this repo. If something wasn't actually
  read/checked, say so instead of guessing.
- Grade AI findings (security, code review) as Valid/Useful, False Positive/Wrong, or Noise, with
  a one-sentence reason for each — not just a list of concerns.
- Do not invent repo facts, business rules, or "typical FastAPI" conventions that don't match what
  `app/main.py`, `app/models.py`, and `app/storage.py` actually do.

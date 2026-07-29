# Module 5 Setup Verification

**Tool note:** written with Claude Code, not Codex App (see `AGENTS.md`). The verification habit
— confirm the agent is reading the real repo before trusting anything else it says — is the same
regardless of which tool is doing the reading.

## Smoke test 1 — repo summary with file evidence

| Claim | Evidence file | Confidence |
|---|---|---|
| Backend is FastAPI, in-memory storage, no database | `task-tracker/backend/app/storage.py` (`_tasks: dict[str, TaskResponse] = {}`), `task-tracker/backend/app/main.py` (`from fastapi import FastAPI, ...`) | High |
| Task fields include `due_date` and `tags`, added after the original Module 1-3 scope | `task-tracker/backend/app/models.py` (`due_date: Optional[date]`, `tags: list[str]`), `docs/midcourse/mini-adr.md` | High |
| Status transitions are restricted to a specific set of pairs, not free-form | `task-tracker/backend/app/business_rules.py` (`VALID_TRANSITIONS` frozenset) | High |
| CI runs `python -m pytest -v`, not bare `pytest` | `.github/workflows/ci.yml` line with `run: python -m pytest -v` | High (this repo's CI run history on `mid-course-project` shows the bare-`pytest` version actually failing, then this fixed version passing) |
| Docker image build/run has not been verified in this environment | `docs/module4/claim-vs-reality.md` | High (this is a claim about what *hasn't* been checked, confirmed by the lack of a Docker daemon here) |

## Smoke test 2 — most recently modified files

Checked via `git log --name-only` on the most recent commit (`7d47fda`, Module 4 completion)
rather than filesystem `mtime`, since filesystem timestamps get reset on checkout/clone and
aren't a reliable signal in a git repo — commit history is.

1. `README.md` — updated with Docker/CI sections and doc links.
2. `docs/decisions/in-memory-task-storage.md` — new Module 4 technical decision note.
3. `docs/module4/ai-review-log.md` / `docs/module4/claim-vs-reality.md` — new Module 4 evidence
   docs (same commit).

These match what this session actually did in the immediately preceding Module 4 work — not a
generic guess about a typical FastAPI project's file layout.

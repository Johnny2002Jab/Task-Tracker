# Final AI Review and Ownership Evidence

This is a condensed, final-project-scoped version of the fuller Module 4/5 evidence in
`docs/module4/` and `docs/module5/` — see those for the complete logs this one summarizes.

**Tool note:** produced with Claude Code throughout (Modules 4 and 5's exercises, which are
written around Claude Code and Codex App respectively, were both actually done with Claude Code —
see `AGENTS.md` and `docs/module5/` for why).

**Resubmission note:** the first submission was flagged for a non-standard repo layout (`app/`,
`frontend/`, `tests/` nested under `task-tracker/backend/` and `task-tracker/frontend/` instead of
at the repo root). Fixed via `git mv` (history preserved) plus matching updates to
`.github/workflows/ci.yml` and `Dockerfile`; full detail and re-verified baseline in
`docs/release-evidence.md`.

## AGENTS.md guardrails

- Repo-specific stack and commands included: **yes** (Python 3.13/FastAPI/pytest versions, exact
  `python -m pytest -v` / `uvicorn ...` commands, not generic placeholders)
- Docs-first/read-first guardrail included: **yes** ("Default to read-only analysis... Module 5
  deliverables live under `docs/`")
- Unexpected app/frontend edits rule included: **yes** ("Any required edit to `app/` or
  `frontend/`... must be explained in the relevant `docs/module5/` file")

## AI code review mini-log

Condensed from `docs/module4/ai-review-log.md` (full log has 6 entries; these 3 are the ones with
real decisions behind them):

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| The Docker image has never actually been built or run in this environment, so the multi-stage `pip install --prefix` → `COPY --from=builder` approach is unverified. | Useful | Biggest real risk in the Docker work — a plausible Dockerfile that's never been executed. | Initially logged as an open verification item. Later closed: since no Docker daemon exists in this dev environment at all (Docker Desktop isn't installed, not just missing from PATH), added a `docker` job to `.github/workflows/ci.yml` that builds, runs, and health/non-root-checks the image on GitHub's `ubuntu-latest` runner instead — real run: [Actions run 30908665181](https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30908665181), both jobs succeeded. See `docs/release-evidence.md` for full detail. |
| `.dockerignore` excludes `docs/`/`README.md`/`CLAUDE.md`, but the `Dockerfile` never uses a broad `COPY . .`, so this currently has zero effect on the final image. | Noise | True but not actionable — harmless forward-looking protection, not a bug. | Left as-is. |
| Initial instinct: excluding `docs/` from the image means an on-call engineer can't read documentation inside a running container. | Wrong | Misunderstands the purpose of a runtime image — the container serves the API; docs were never going to be shipped inside it regardless of `.dockerignore`, since the `Dockerfile` doesn't copy them. | Rejected, no change made. Recorded specifically because it's the kind of AI comment that sounds responsible but doesn't hold up on inspection. |

## AI security mini-review

Condensed from `docs/module5/security-review.md` (full log has 5 findings):

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| `description` and `assignee` are unbounded strings (no max length), unlike `title` (200 chars) or `tags` (30 chars/10 max) | `app/models.py` | Valid | Concrete resource-exhaustion risk: unauthenticated clients can grow the in-memory store without bound. | Add a max length to both fields; consider a max total task count. |
| No automated dependency-vulnerability scanning (no Dependabot, no `pip-audit` step) | `.github/workflows/ci.yml`, repo root | Valid, low severity | Pinned versions give reproducibility but no ongoing CVE check. | Add a `pip-audit` CI step or a `dependabot.yml`. |
| 404/422 error details echo back client-supplied data (e.g. task id) — initial concern: reflected input | `app/main.py` | False Positive | Checked the frontend: `showModalError`/`createStatusBanner` in `index.html` use `.textContent`, never `.innerHTML` — reflected text rendered via `textContent` isn't an XSS vector. | Rejected; recorded because it's exactly the kind of pattern worth a second look, even though it didn't hold up. |

## Manual security check

Verified (not assumed) that the tag limits (max 10, 30 chars each, blank rejected) can't be
bypassed via `PATCH`: confirmed in `app/models.py` that `TaskCreate.tags` and `TaskUpdate.tags`
share the identical `_normalize_tags` validator via matching `@field_validator` decorators, so
there's no update-path bypass of a create-path-only rule. No new finding — this closes a
plausible gap rather than opening one. Full context in `docs/module5/security-review.md`.

## One AI output I rejected or corrected

The clearest example spans this whole project: an earlier fix for "editing a task fails if you
don't change its status" initially patched the **backend** to skip status-transition validation
whenever the status was unchanged. That silently violated the actual documented business rule
(same-status transitions must return 422 — see `app/business_rules.py`'s `VALID_TRANSITIONS`,
which deliberately excludes same→same pairs). It was rejected and replaced with the correct fix on
the **frontend**: only send `status` in the PATCH payload when the user actually changed it
(`frontend/index.html`, `editingOriginalStatus` tracking in the modal — path was
`task-tracker/frontend/index.html` at the time, moved to the repo root in the resubmission
structure fix below). The backend
rule stayed strict; the bug was actually in what the frontend was sending, not in what the backend
was rejecting. This is recorded at length in `docs/midcourse/prompt-log.md` because it happened
more than once before the frontend-side root cause was actually understood and fixed for good.

## Three AI usage rules

(Full reasoning in `docs/ai-usage.md`.)

1. **Never paste:** long-lived credentials, `.env` contents, tokens, or real personal/customer
   data into an AI tool or the repo. If a tool genuinely needs a credential, retrieve it
   programmatically immediately before use and never print or log it.
2. **Always verify:** run it, don't just read it. A CI workflow, a security finding, a bug fix —
   none of these are "done" until there's a real run, a real curl, or a real test result behind
   the claim, not just a plausible-looking diff.
3. **Record AI contributions by:** writing down what was proposed, accepted, corrected, and why,
   next to the change itself (commit message or `docs/` note) — not from memory afterward. The
   same-status PATCH bug came back a second time specifically because the first correction wasn't
   documented clearly enough to stop it from quietly reverting.

## Ownership statement

I'm comfortable submitting this repo as my own work because every non-trivial claim in it is
backed by something I actually ran, not just a plausible-looking diff. The CI green→red→green
sequence was produced by genuinely pushing an intentional break and watching it fail for the right
reason, and the security findings were checked against the actual frontend rendering code before
being accepted or rejected, not accepted at face value. The one thing I initially could not verify
by hand — the Docker build, since no Docker daemon exists in this dev environment — was recorded
as unverified rather than glossed over, and was later actually closed, not just re-flagged again,
by adding a real `docker` job to CI that builds, runs, and health/non-root-checks the image on
GitHub's runner (`docs/release-evidence.md` has the passing run link). The parts written in a
first-person "voice" (this statement, the AI playbook, the decision notes' trade-offs sections)
were drafted with AI assistance but reflect judgment calls I'd defend if asked why, not
boilerplate. Every open item in this project got either an honest "not verified" label or, once
actually resolved, evidence of the real run that resolved it — never a claim I hadn't checked.

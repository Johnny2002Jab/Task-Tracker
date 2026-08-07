# Final AI Review and Ownership Evidence



## AGENTS.md guardrails

- Repo-specific stack and commands included: **yes**
- Docs-first/read-first guardrail included: **yes** 
- Unexpected app/frontend edits rule included: **yes** 

## AI code review mini-log

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| The Docker image has never actually been built or run in this environment, so the multi-stage `pip install --prefix` → `COPY --from=builder` approach is unverified. | Useful | Biggest real risk in the Docker work — a plausible Dockerfile that's never been executed. | Initially logged as an open verification item. Later closed: since no Docker daemon exists in this dev environment at all (Docker Desktop isn't installed, not just missing from PATH), added a `docker` job to `.github/workflows/ci.yml` that builds, runs, and health/non-root-checks the image on GitHub's `ubuntu-latest` runner instead — real run: [Actions run 30908665181](https://github.com/Johnny2002Jab/Task-Tracker/actions/runs/30908665181), both jobs succeeded. See `docs/release-evidence.md` for full detail. |
| `.dockerignore` excludes `docs/`/`README.md`/`CLAUDE.md`, but the `Dockerfile` never uses a broad `COPY . .`, so this currently has zero effect on the final image. | Noise | True but not actionable — harmless forward-looking protection, not a bug. | Left as-is. |
| Initial instinct: excluding `docs/` from the image means an on-call engineer can't read documentation inside a running container. | Wrong | Misunderstands the purpose of a runtime image — the container serves the API; docs were never going to be shipped inside it regardless of `.dockerignore`, since the `Dockerfile` doesn't copy them. | Rejected, no change made. Recorded specifically because it's the kind of AI comment that sounds responsible but doesn't hold up on inspection. |

## AI security mini-review

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

editing a task fails if you
don't change its status initially patched the **backend** to skip status-transition validation
whenever the status was unchanged. That silently violated the actual documented business rule. It was rejected and replaced with the correct fix on
the **frontend**: only send `status` in the PATCH payload when the user actually changed it. The backend
rule stayed strict; the bug was actually in what the frontend was sending, not in what the backend
was rejecting. This is recorded at length in `docs/midcourse/prompt-log.md` because it happened
more than once before the frontend-side root cause was actually understood and fixed for good.

## Three AI usage rules

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
being accepted or rejected, not accepted at face value.

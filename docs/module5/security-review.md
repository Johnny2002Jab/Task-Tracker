# Security Review — Task Tracker

**Tool note:** performed with Claude Code, not Codex App. This also means the "AI audit" and
"manual scan" below were both done by the same agent (me), not by an AI pass followed by a
genuinely separate human reviewer as the module describes. I've kept the two passes distinct in
method — a first structured audit checklist, then a second skeptical pass specifically looking
for what the first pass might have gotten wrong or missed — to preserve the actual point of the
exercise (don't trust the first pass at face value), even though it isn't a two-person review.

Scope inspected: `task-tracker/backend/app/` (`main.py`, `models.py`, `storage.py`,
`business_rules.py`), `task-tracker/backend/requirements.txt`, `Dockerfile`, `.dockerignore`,
`.github/workflows/ci.yml`, `task-tracker/frontend/index.html`. Read-only — no files were changed
as part of this review.

## AI findings

| # | Finding | File evidence | Grade | Reason |
|---|---|---|---|---|
| 1 | `description` and `assignee` are unbounded strings — no max length, unlike `title` (200 chars) or `tags` (30 chars each, 10 max). Combined with no cap on total task count, an unauthenticated client can grow the in-memory store without bound. | `app/models.py`: `title` has a `field_validator` enforcing `<=200` chars; `description`/`assignee` have none | **Valid** | This is a real, concrete gap matching the exact "unbounded fields" pattern to look for. Since storage is an in-memory process-wide dict with no persistence, this is a resource-exhaustion / memory-growth risk, not just a data-quality one. |
| 2 | No authentication, authorization, or ownership checks on any endpoint — anyone who can reach the API can read, create, edit, or delete any task. | `app/main.py` — no auth dependency on any route | **Valid**, but scoped | Explicitly an intentional Module 1 scope decision (see `CLAUDE.md`/`AGENTS.md` do-not rules), and correctly so for a local learning project. Still a real production risk if this were ever exposed beyond localhost — logged here so that context isn't lost. |
| 3 | No automated dependency vulnerability scanning (no Dependabot config, no `pip-audit`/`safety` step in CI). | Confirmed absent: no `.github/dependabot.yml`, no such step in `.github/workflows/ci.yml` | **Valid**, low severity | Pinned exact versions in `requirements.txt` give reproducibility but no ongoing check for known CVEs in those pins. A `dependabot.yml` or a `pip-audit` CI step would close this cheaply. |
| 4 | CORS allows the `"null"` origin (covers `file://` access) plus `allow_methods=["*"]`/`allow_headers=["*"]`. | `app/main.py` `CORSMiddleware` config | **Noise** | Broad-looking, but `allow_credentials=False` means no cookies/credentials are ever sent cross-origin, which removes the main class of attack this configuration would otherwise enable. Reasonable for local dev; would need tightening only if this were ever deployed with real user sessions. |
| 5 | 404/422 error details echo back client-supplied data (e.g. `f"Task with id {task_id} not found"`) — initial concern: reflected input in error responses. | `app/main.py`, multiple routes | **False Positive** | Checked the frontend rendering path: `showModalError`/`createStatusBanner` in `index.html` assign this text via `.textContent`, never `.innerHTML` or template-string DOM injection. Reflected text in a JSON API response, rendered through `textContent`, is not an XSS vector. Recorded as a rejected finding rather than silently dropped, since "reflects user input" is exactly the kind of pattern a security pass *should* flag for a closer look — it just doesn't hold up here. |

## Manual check

Verified, rather than assumed, that the tag limits (max 10 tags, 30 chars each, blank-tag
rejection) can't be bypassed via `PATCH` — the concern was that `TaskCreate` might validate tags
strictly while `TaskUpdate` (partial update) validates more loosely. Confirmed in `app/models.py`
that both `TaskCreate.tags` and `TaskUpdate.tags` share the same `_normalize_tags` validator via
identical `@field_validator("tags", ...)` decorators, so there's no update-path bypass. No new
finding from this check — it closes a plausible gap rather than opening one, which is worth
recording precisely because a shallower pass could have left it as an open question.

## Reconciliation

| Agreement | AI-only | You-only (manual) |
|---|---|---|
| — (single-pass tool, no independent second reviewer to agree/disagree with) | Findings 1-5 above (unbounded fields, no auth, no dependency scanning, CORS breadth, the rejected reflected-input concern) | The PATCH tag-limit bypass check — a targeted verification the structured audit checklist didn't happen to prompt, since it's about consistency *between* two models rather than a property of either model alone |

*(The Agreement/AI-only/You-only split assumes two independent reviewers; with one agent doing
both passes there's nothing to "agree" with. Kept the column for format-compatibility with the
module's template, but the honest read is: one systematic pass, one supplementary targeted check.)*

## Top-3 backlog

1. **Add a max length to `description` and `assignee`, and consider a max total task count.**
   Highest severity of the Valid findings — directly enables unbounded memory growth against a
   process with no persistence and no restart-recovery story beyond "all data is lost." Cheapest
   real fix in this list.
2. **Add a `pip-audit` (or Dependabot) step.** Low effort, closes finding #3, and would have
   caught real CVEs if any existed in the pinned FastAPI/Pydantic/Uvicorn versions — worth doing
   before this ever runs anywhere with real traffic.
3. **Document (don't yet fix) the no-auth decision as an explicit, revisit-if-deployed item.**
   Already true in spirit via `CLAUDE.md`'s do-not rules, but worth a one-line pointer in
   `docs/decisions/` the next time storage or deployment decisions are revisited, so "no auth" and
   "in-memory only" get reconsidered together rather than one at a time.

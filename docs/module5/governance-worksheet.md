# Governance Retrospective

**Tool note:** written from this session's actual Claude Code conversation history (Modules
mid-course through 4-5), not a generic template filled with invented examples.

## What did I share with AI?

| Item shared | Risk | Reason |
|---|---|---|
| Full application source (`app/*.py`, `frontend/index.html`, tests) | Low | Course project code, no secrets, no real user data, already headed for a public repo. |
| pytest failure output, tracebacks, CI failure screenshots | Low | Local error text and public CI run screenshots — no credentials or private data in any of it. |
| Course module PDFs (lecture notes, prompt libraries, project briefs) | Low | Publicly-issued course materials, not confidential. |
| Screenshots of the running app (Kanban board error state) | Low | UI screenshots of a local dev instance with placeholder task data. |
| **A live GitHub OAuth token**, retrieved via `git credential fill` and passed directly into a `curl` command to call the GitHub Actions API (trigger a workflow re-run) | **High** | This is the one genuinely high-risk moment in this session. The token was never printed to chat output or written to a file, and was `unset` immediately after use — but it *was* passed through a shell command whose arguments could in principle appear in a process list or a stored session transcript. A credential is a credential regardless of how carefully it's handled downstream. |
| Repository structure / branch names / commit messages | Low | Not sensitive; this is a course project intended to be graded from a public repo. |

## What did I receive from AI?

| Item received | Did I verify it, or accept it too quickly? |
|---|---|
| Due-dates/overdue and tags/labels backend + frontend implementation | Verified: ran the full pytest suite (36/36), manually curl-tested overdue/tag filters and validation errors before considering it done. |
| A backend-only fix for the "editing a task fails" PATCH bug | **Accepted too quickly the first time.** The initial fix (skip transition validation when status unchanged) silently violated the documented business rule that same-status transitions must be `422`. It was corrected — twice, actually, since it reverted on its own between sessions and had to be re-diagnosed — by moving the fix to the frontend (only send `status` when it actually changed) instead of weakening the backend rule. Recorded in the mid-course prompt log as the clearest "AI proposed a shortcut, I had to catch it" moment in this project. |
| CI workflow (`.github/workflows/ci.yml`) | Verified with real evidence, not just "it looks right": pushed it, watched it fail with `ModuleNotFoundError`, diagnosed the actual cause (bare `pytest` vs `python -m pytest`), fixed it, and proved green → red → green with an intentional, reverted break. |
| Dockerfile / `.dockerignore` | **Not fully verified** — authored to spec (multi-stage, non-root, slim), but never actually built or run, since no Docker daemon was available in this environment. Logged honestly as an open item in `docs/module4/claim-vs-reality.md` rather than claimed as tested. |
| Security review findings (this session, Module 5) | Self-graded Valid/False Positive/Noise rather than accepted wholesale — one finding (reflected input in error messages) was flagged, checked against the actual frontend rendering code, and rejected as a False Positive once it was clear `.textContent` (not `.innerHTML`) was used everywhere. |

## Trace one generated block, line by line

Selected: `_normalize_tags` in `task-tracker/backend/app/models.py`, the shared validator behind
both `TaskCreate.tags` and `TaskUpdate.tags`.

```python
def _normalize_tags(tags: Optional[list[str]]) -> list[str]:
    if tags is None:
        return []
    if len(tags) > MAX_TAGS:
        raise ValueError(f"a task may have at most {MAX_TAGS} tags")

    normalized: list[str] = []
    seen_lower: set[str] = set()
    for raw_tag in tags:
        tag = str(raw_tag).strip()
        if not tag:
            raise ValueError("tags must not be blank")
        if len(tag) > MAX_TAG_LENGTH:
            raise ValueError(f"each tag must be {MAX_TAG_LENGTH} characters or fewer")
        if tag.lower() in seen_lower:
            continue
        seen_lower.add(tag.lower())
        normalized.append(tag)
    return normalized
```

| Line(s) | What it does | Why it's there | What breaks if removed |
|---|---|---|---|
| `if tags is None: return []` | Treats "no tags provided" as an empty list rather than an error. | `TaskCreate.tags` defaults to `[]`, and `TaskUpdate.tags` defaults to `None` (meaning "not touched" — see `storage.update_task`'s `exclude_unset` logic); this line normalizes both into the same empty-list shape once the field *is* being validated. | Without it, creating a task with no `tags` key would raise a `TypeError` iterating over `None` a few lines down. |
| `if len(tags) > MAX_TAGS: raise ValueError(...)` | Enforces the max-10-tags rule *before* doing any per-tag work. | Checking count first, before the loop, means a client can't bypass the cap by relying on later dedup to shrink the list — the count check happens on the raw input length. | Without it, a client could send unlimited tags and only the loop's per-tag checks would apply — no cap at all. |
| `seen_lower: set[str] = set()` / the `if tag.lower() in seen_lower: continue` | Case-insensitive de-duplication: `"Backend"` and `"backend"` collapse to one tag, keeping the *first* casing seen. | Chosen deliberately (see `docs/midcourse/mini-adr.md`) so a user mistake like re-adding a tag with different casing doesn't silently create two "different" tags that a case-sensitive `GET /tasks?tag=` filter would treat as distinct. | Without it, `["Backend", "backend"]` would be stored as two separate tags, and the tag filter's case-insensitive match (`app/storage.py`) would then match both when filtering by either casing — inconsistent and confusing. |
| `if not tag: raise ValueError("tags must not be blank")` | Rejects a tag that's empty after stripping whitespace. | Mirrors the `title` validator's blank-check pattern elsewhere in the same file, for consistency. | Without it, `["  "]` would pass through as a single blank-string tag, which would render as an empty chip in the frontend UI with no visible content. |

Everything in this block was understood well enough to explain the *why*, not just the *what* —
which is the actual point of tracing generated code rather than trusting it because it runs.

See `docs/ai-usage.md` for the rules this retrospective turned into.

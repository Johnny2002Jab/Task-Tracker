# Prompt Log — Mid-Course Project


## Weak vs. strong prompt (feature scoping)

**Weak prompt (what I'd have asked without the course habits):**
> "Add due dates and tags to my task tracker."

**What would likely go wrong:** no constraint on date type (date vs datetime), no definition
of "overdue" (does a `Done` task count?), no decision on tags-as-string vs tags-as-list, no
test requirement, and a high chance of scope creep into bulk tagging, saved filters, or a full
tag-management UI.

**Strong prompt actually used (paraphrased from this session):**
> "Implement 'Due dates + overdue filter' and 'Tags/labels' from the mid-course brief on the
> existing FastAPI Task Tracker. Constraints: additive fields only on the existing
> `TaskCreate`/`TaskUpdate`/`TaskResponse` models, no database, no new routes beyond then existing CRUD shape, overdue computed at read time (not stored), tags as a real
> `list[str]` (not comma-separated), max 10 tags/30 chars each, case-insensitive dedup, a `Done` task is never overdue.

- **Accepted:** the constraint list above became the actual `mini-adr.md` decisions.
- **Edited:** the initial mini-ADR draft used the Module 1 P0-style long-form ADR format;
  I asked for it to be rewritten  (Status/Date header → Context → Decision → Reasoning → Consequences →
  Implementation Notes → AI Assumptions Reviewed → Alternatives Considered) rather than a
  generic format.

## Prompt 1 — Baseline stabilization before feature work

**Prompt:** "Run the existing pytest suite on the new branch before making any changes and
tell me what's failing and why."

**What AI returned:** identified 2 pre-existing failures. One (`test_patch_same_status`) was
traced to a prior backend fix that actually violated the course's documented business rule
(same-status transitions must be 422). The other (`test_patch_empty_json_object`) was traced
to a genuinely missing guard (empty PATCH body should be rejected, wasn't).

**Accepted:** both root-cause diagnoses.
**Edited:** the fix for the first one. AI's first inclination was to keep the backend
workaround; I redirected it to fix the *frontend* instead (only send `status` in the PATCH
payload when it changed), since that's the fix consistent with the documented transition
rules, not a second workaround stacked on the first.

## Prompt 2 — Due dates: overdue definition

**Prompt:** "Should a completed (`Done`) task with a past due date count as overdue?"

**What AI returned:** first draft of `is_overdue` compared only `due_date < today`, with no
status check.

**Rejected/corrected:** flagged as wrong before implementation — a task finished late isn't
actionable as "overdue." Added the explicit `status != Done` exclusion. This is recorded as
the AI-assumption-corrected item in both `user-stories.md` and `mini-adr.md`.

## Prompt 3 — Tags: storage shape

**Prompt:** "What's the smallest change to store tags on a task?"

**What AI returned:** first suggestion was a single comma-separated string field to minimize
the diff against `TaskCreate`/`TaskUpdate`.

**Rejected/corrected:** rejected in favor of a real `list[str]` field, because a
comma-separated string pushes parsing/validation into the frontend and makes tag-equality
filtering ambiguous (`"backend, api"` vs `"backend,api"`). Recorded as the second
AI-assumption-corrected item.

## Prompt 4 — Test generation

**Prompt:** "Generate pytest tests for both features covering: valid/invalid due dates,
overdue detection (including the Done exclusion), due-date update/clear, overdue filter
(match + no-match), tag creation/trimming, blank tag rejection, tag count/length limits,
duplicate-tag dedup, tag replace-on-PATCH, tags preserved on unrelated PATCH, and tag filter
(match + no-match). Use the existing `client`/`created_task` fixtures and naming style from
`tests/test_tasks.py`."

**Accepted:** all 16 generated tests, after reading each assertion against its test name (per
the Module 2 D1 habit of checking that a test asserts the actual scenario, not just "some
error happened"). No changes needed to the generated test bodies.

## Prompt 5 — Break Test verification

**Prompt:** "For the Done-exclusion overdue test and the tag-dedup test, tell me the smallest
temporary source change that should make each fail, so I can prove they're meaningful."

**What AI returned:** two temporary breaks (removing the `Done` check; removing the
`seen_lower` dedup loop), both matched to the specific rule each test claims to protect.

**Accepted as-is** — both breaks produced the expected failing assertions (see
`verification.md`), confirming the tests are real rather than vacuously passing.

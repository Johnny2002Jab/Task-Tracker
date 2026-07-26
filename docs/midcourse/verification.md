# Verification Log — Mid-Course Project

## 1. Baseline check (before any feature work)

Ran the existing suite on `mid-course-project` immediately after branching, before touching
any feature code:

```
20 items collected
18 passed, 2 failed
FAILED tests/test_tasks.py::test_patch_same_status_returns_422
FAILED tests/test_tasks.py::test_patch_empty_json_object_returns_422
```

**Root causes found and fixed before starting feature work** (see `mini-adr.md` context and
`prompt-log.md` for the AI-assisted debugging trail):

1. `test_patch_same_status_returns_422` — a previous backend workaround (skip transition
   validation when `payload.status == existing.status`) violated the documented business rule
   that same→same status transitions are invalid. Reverted the backend to always validate the
   transition pair; fixed the actual root cause on the **frontend** instead — the edit modal
   now only includes `status` in the PATCH payload when the user actually changed it.
2. `test_patch_empty_json_object_returns_422` — an empty `{}` PATCH body silently no-op'd
   (200) instead of being rejected. Added a guard in `update_task` that rejects an update body
   with no fields set (HTTP 422).

Result after fix, before feature work: **20 passed, 0 failed.**

## 2. Backend test results (after both features)

```
36 items collected
36 passed in 0.23s
```

16 new tests in `tests/test_midcourse_features.py` (8 for due dates/overdue, 8 for tags),
all 20 pre-existing tests in `tests/test_tasks.py` untouched and still passing.

## 3. Manual browser checks (Feature verification)

Backend confirmed via `curl` for every rule below; UI confirmed manually in the browser
(no browser-automation tool was available in this environment, so these were eyeballed
directly rather than screenshotted):

| Check | Method | Result |
|---|---|---|
| Create task with due date + tags via modal | Manual (browser) | Pass — card shows due date and tag chips |
| Task with past due date shows "Overdue" pill | Manual (browser) + curl | Pass |
| `Done` task with past due date does **not** show overdue | curl (`test_task_with_past_due_date_but_done_status_is_not_overdue`) | Pass |
| Invalid `due_date` format rejected | `curl -d '{"due_date":"not-a-date"}'` | 422, `loc` includes `due_date` |
| Tag filter bar returns matching tasks only | Manual (browser) + curl | Pass |
| Overdue filter checkbox returns overdue tasks only | Manual (browser) + curl | Pass |
| Combined filter `priority=High&tag=urgent` | `curl "/tasks?priority=High&tag=urgent"` | Returned only the 2 matching tasks (case-insensitive tag match confirmed against a real task created via the browser during manual testing) |
| Editing an existing task (title/priority only) no longer 422s | Manual (browser) — this was the original bug report | Pass |
| Tag count/length limits (>10 tags, >30 chars) rejected | `curl` with 11 tags | 422 |
| Duplicate tags de-duplicated case-insensitively | `curl -d '{"tags":["Backend","backend","BACKEND"]}'` | Returned `["Backend"]` |

## 4. Behavior contract (Modules 1-3 behaviors, re-checked after this work)

| # | Behavior | Before this project | After this project |
|---|---|---|---|
| 1 | Three status columns render with correct counts | Pass | Pass (unchanged) |
| 2 | Cards sort by priority inside each column | Pass | Pass (unchanged) |
| 3 | Loading state appears before tasks load | Pass | Pass (unchanged) |
| 4 | Empty columns remain visible | Pass | Pass (unchanged) |
| 5 | Error state appears when backend is stopped | Pass | Pass (unchanged) |
| 6 | Valid drag sends PATCH and updates the board | Pass | Pass (unchanged) |
| 7 | Invalid drag/server 422 reverts and shows message | Pass | Pass (unchanged) |
| 8 | New Task / Edit modal flows work, including title validation and dismissal | Pass | Pass — edit flow bug (same-status 422 on unrelated edits) fixed as part of this project |
| 9 | Due date set/clear/display + overdue pill | N/A (new) | Pass |
| 10 | Tags set/replace/preserve + tag chips + tag/overdue filters | N/A (new) | Pass |

## 5. Break Test evidence

**Break 1 — `is_overdue` Done-status exclusion**
Temporarily removed the `self.status == TaskStatus.DONE` check from `TaskResponse.is_overdue`
in `app/models.py`.

```
tests/test_midcourse_features.py::test_task_with_past_due_date_but_done_status_is_not_overdue FAILED
AssertionError: assert True is False
```

Confirms the test actually protects the "Done tasks are never overdue" rule. Source restored;
suite back to 36 passed.

**Break 2 — tag case-insensitive de-duplication**
Temporarily removed the `seen_lower` de-duplication loop in `_normalize_tags` in
`app/models.py`.

```
tests/test_midcourse_features.py::test_create_task_with_duplicate_tags_deduplicates_case_insensitively FAILED
AssertionError: assert ['Backend', 'backend', 'BACKEND'] == ['Backend']
```

Confirms the test actually protects the de-duplication rule, not just "no error raised."
Source restored; suite back to 36 passed.

## 6. Final state

```
36 passed in 0.23s
```

All pre-existing behavior preserved; both features implemented, tested, and manually verified
end-to-end.

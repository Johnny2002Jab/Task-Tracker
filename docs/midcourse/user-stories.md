# Mid-Course Project — User Stories

Role convention: "team member" (consistent with Modules 1-3). No authentication, accounts, or
per-user data — the task list remains a single shared board.

## Feature 1: Due dates + overdue filter

**Story 1 — Set a due date when creating a task**
As a team member, I want to optionally set a due date when I create a task, so that I know
when the work needs to be finished.
- Acceptance criteria:
  - `due_date` is optional; omitting it creates the task with no due date.
  - A valid due date is an ISO calendar date (`YYYY-MM-DD`).
  - An invalid date format (e.g. `"next friday"`, `"31-02-2026"`) returns HTTP 422.

**Story 2 — Change or clear a task's due date**
As a team member, I want to update or remove a task's due date, so that I can adjust plans
without recreating the task.
- Acceptance criteria:
  - PATCH accepts `due_date` as part of a partial update.
  - Sending `due_date: null` clears an existing due date.
  - Other fields are unaffected by a due-date-only PATCH.

**Story 3 — See which tasks are overdue**
As a team member, I want tasks past their due date to be visibly marked overdue, so that I can
prioritize what's late.
- Acceptance criteria:
  - A task is overdue only when `due_date` is in the past **and** status is not `Done`.
  - A `Done` task with a past due date is never shown as overdue.
  - Overdue status is computed at read time, not stored, so it stays correct as days pass.

**Story 4 — Filter the board to overdue tasks only**
As a team member, I want to filter the task list to only overdue tasks, so that I can see
what needs immediate attention without scanning every column.
- Acceptance criteria:
  - `GET /tasks?overdue=true` returns only tasks currently overdue.
  - The filter combines with existing `status`/`priority` filters.
  - No overdue tasks returns HTTP 200 with `[]`, not 404.

**Story 5 — See due dates and overdue status in the UI**
As a team member, I want to see a task's due date and an overdue indicator on its card, so
that I don't have to open the edit modal to check.
- Acceptance criteria:
  - Cards with a due date show it in a readable format.
  - Overdue cards show a distinct visual indicator (pill/badge).
  - Cards without a due date show no date row (not "None" or "null").

**AI assumption corrected:** The first draft treated any task with a past `due_date` as
overdue regardless of status. This was corrected because a completed task that finished late
is not "overdue" in any actionable sense — the rule now excludes `Done` tasks explicitly.

---

## Feature 2: Tags / labels

**Story 1 — Add tags when creating a task**
As a team member, I want to attach one or more tags to a task, so that I can categorize work
beyond status and priority.
- Acceptance criteria:
  - `tags` is an optional list of strings; omitting it creates a task with an empty tag list.
  - Each tag is trimmed of surrounding whitespace before saving.
  - A blank/whitespace-only tag in the list is rejected with HTTP 422.

**Story 2 — Enforce reasonable tag limits**
As a team member, I want the system to reject unreasonable tag input, so that the tag list
stays useful and doesn't get abused.
- Acceptance criteria:
  - A single tag longer than 30 characters returns HTTP 422.
  - More than 10 tags on one task returns HTTP 422.
  - Duplicate tags (case-insensitive) are silently de-duplicated rather than rejected.

**Story 3 — Update a task's tags without touching other fields**
As a team member, I want to add, remove, or replace a task's tags independently, so that
retagging doesn't require resending the whole task.
- Acceptance criteria:
  - PATCH `tags` replaces the full tag list (not a merge).
  - A PATCH that omits `tags` leaves the existing tags unchanged.
  - Sending `tags: []` clears all tags.

**Story 4 — Filter tasks by tag**
As a team member, I want to filter the task list by a single tag, so that I can find related
work quickly.
- Acceptance criteria:
  - `GET /tasks?tag=backend` returns only tasks that include that tag (case-insensitive match).
  - The filter combines with existing `status`/`priority`/`overdue` filters.
  - A tag with no matching tasks returns HTTP 200 with `[]`.

**Story 5 — See tags on the board**
As a team member, I want to see a task's tags as chips on its card, so that I can scan the
board by category at a glance.
- Acceptance criteria:
  - Each tag renders as a small chip on the card.
  - A task with no tags shows no chip row.
  - Tag text is escaped before insertion into the DOM (same rule as title/description).

**AI assumption corrected:** The first draft proposed storing tags as a single comma-separated
string field to minimize model changes. This was corrected in favor of a proper `list[str]`
field — a comma-separated string would have pushed parsing/validation logic into the frontend
and made "exact match" filtering ambiguous (e.g. `"backend, api"` vs `"backend,api"`).

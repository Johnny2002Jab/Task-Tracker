Architecture Decision Record (ADR)
ADR-002: Add Due Dates/Overdue Filtering and Tags to the Task Tracker
Status: Accepted
Date: 2026-07-26

________________________________________
Context
The Task Tracker is the Module 1-3 learning project: Python/FastAPI backend with in-memory
storage, Pydantic validation, and a vanilla JS/HTML Kanban frontend. This mid-course
checkpoint adds two small, end-to-end features on top of that existing architecture:

1. Due dates, with an overdue indicator and an overdue filter.
2. Tags/labels, with tag chips on cards and a tag filter.

Both features must fit inside the existing model/storage/route structure without a database,
authentication, or new services, and without breaking any existing behavior or tests.

________________________________________
Decision
Add both features as additive fields on the existing `TaskCreate` / `TaskUpdate` /
`TaskResponse` models, with matching optional query filters on `GET /tasks`:

- `due_date: Optional[date]` — a calendar date, no time-of-day. Overdue status
  (`is_overdue`) is computed at response time from `due_date` and `status`, not stored.
- `tags: list[str]` — a real list field, trimmed and case-insensitively de-duplicated, with a
  per-tag length cap and a max-count cap.
- `GET /tasks` gains `overdue` (bool) and `tag` (string) filters, combinable with the
  existing `status`/`priority` filters.

________________________________________
Reasoning
Keeping both features as plain fields on the existing models was chosen because it required
no new storage layer, no new routes beyond the existing CRUD shape, and no schema migration
concerns, since storage is in-memory. This kept both features small enough to implement and
verify end-to-end in one small-loop workflow, consistent with the project's "small, scoped
feature" expectation.

Computing `is_overdue` instead of storing it avoids a background job or write-time recompute
step to keep an overdue flag from going stale as calendar days pass; deriving it at read time
is simpler and cannot drift out of sync.

Using a real `list[str]` for tags instead of a comma-separated string was chosen because it
keeps validation (blank tags, length, count) and filtering (exact tag match) unambiguous,
matching how the existing `status`/`priority` enums are already validated and filtered.

Testability was considered for both features: both are pure model/storage additions, so the
existing FastAPI TestClient pattern and reset fixture cover them with no new test
infrastructure.

________________________________________
Consequences

Positive consequences
- Both features reuse the existing model/storage/route/test patterns; no new architecture.
- All pre-existing tests continue to pass unmodified; both features are additive.
- Overdue status and tag filtering stay correct automatically (computed/derived, not cached).
- Frontend changes are confined to the existing modal and card template, not a new surface.

Negative consequences
- Tag filtering is single-tag only; multi-tag AND/OR filtering is out of scope here and
  would need its own query-param design.
- `is_overdue` depends on server wall-clock time; this is invisible on a local single-user
  deployment but would need reconciling in a hypothetical multi-timezone setup.
- The tag de-duplication and length/count limits are reasonable defaults, not requirements
  from a stakeholder — they could need revisiting if real usage patterns differ.

________________________________________
Implementation Notes
Changes stay inside the existing structure:
```
backend/
└── app/
    ├── main.py            (new overdue/tag query params on GET /tasks)
    ├── models.py           (due_date, is_overdue, tags fields + validators)
    └── storage.py          (filter logic for overdue/tag)
frontend/
└── index.html              (due date + tags fields in modal; due date/overdue/tag chips on cards)
```
The implementation includes:
- Pydantic validation for:
  - `due_date` as an ISO calendar date; invalid formats return HTTP 422.
  - Each tag non-blank after trimming, ≤30 characters, ≤10 tags per task.
- Business rule for overdue: `due_date` in the past **and** status is not `Done`.
- HTTP 422 responses for validation failures, consistent with existing model validators.

________________________________________
AI Assumptions Reviewed
During implementation, AI-generated assumptions were corrected:
- Rejected assumption: any task with a past `due_date` should count as overdue. Corrected
  because a `Done` task finished late is not actionable as "overdue" — the rule now excludes
  `Done` tasks explicitly.
- Rejected assumption: tags should be stored as a single comma-separated string to minimize
  the model diff. Corrected in favor of a real `list[str]` field, because a comma-separated
  string would push parsing into the frontend and make exact-tag filtering ambiguous.

________________________________________
Alternatives Considered

Storing `is_overdue` as a persisted, recomputed-on-write field
Considered because it would avoid a computed property. Not selected because it requires a
recompute step on every read anyway to stay correct as days pass, adding complexity with no
benefit over a pure computed property.

A separate `Tag` resource with its own CRUD endpoints
Considered because it is more representative of a production tagging system. Not selected
because it introduces a second resource, its own routes, and referential-integrity concerns
that are unnecessary for a learning project with in-memory storage and no database.

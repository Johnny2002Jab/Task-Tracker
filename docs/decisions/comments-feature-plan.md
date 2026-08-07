# Comments-on-Tasks Feature Plan (Planning Only — Not Implemented)

## Generic plan (deliberately written without re-reading this repo's actual files)

1. **Data Model** — Add a `Comment` SQLAlchemy/SQLModel table with a foreign key to `Task.id`,
   using a database migration to add the table.
2. **API Routes** — `POST /tasks/{id}/comments` (create), `GET /tasks/{id}/comments` (list),
   `DELETE /comments/{id}` (delete). Standard REST nesting under the parent resource.
3. **Tests** — `test_create_comment`, `test_list_comments`, `test_delete_comment`, plus
   validation tests for blank `author`/`body`.
4. **Frontend Changes** — Add a comments panel to a task detail view; fetch comments on open,
   POST new ones, refresh the list after submit.
5. **Migration Notes** — Run a database migration to create the `comments` table with a foreign
   key constraint to `tasks.id`, with `ON DELETE CASCADE`.
6. **Open Questions** — Should comments support edit, or only create/delete? Should there be a
   max comment count per task?

**Assumptions this plan makes:** that there is a database and migration tool in this project, and
that there is an existing "task detail view" separate from the Kanban card in the frontend.

## Repo-grounded plan

Read before planning: `app/models.py`, `app/main.py`, `app/storage.py`, `app/business_rules.py`,
`tests/conftest.py`, `tests/test_tasks.py`, `task-tracker/frontend/index.html`, `CLAUDE.md`,
`AGENTS.md`.

1. **Data Model** — No database or ORM exists in this repo (`app/storage.py` is a plain in-memory
   dict; see `docs/decisions/in-memory-task-storage.md`). A `Comment` would be a plain Pydantic
   model (`CommentCreate`, `CommentResponse`) in `app/models.py`, following the same
   `model_config = ConfigDict(extra="forbid")` + `field_validator` pattern already used for
   `title`/`tags`. Comments would live in a second in-memory dict in `app/storage.py`
   (`_comments: dict[str, CommentResponse]`, or nested under each task), reset by the same
   `_reset()` test fixture pattern `tests/conftest.py` already relies on.
2. **API Routes** — `POST /tasks/{task_id}/comments` (201) and `GET /tasks/{task_id}/comments`
   (200, empty list if none) and `DELETE /tasks/{task_id}/comments/{comment_id}` (204), matching
   this repo's existing conventions exactly: `HTTPException(status_code=404, detail=f"Task with
   id {task_id} not found")` style for a missing task, `response_model=` on every route, `tags=
   ["tasks"]` (or a new `"comments"` tag) like every existing route in `app/main.py`.
3. **Tests** — Following `tests/test_tasks.py`'s naming convention
   (`test_<action>_<condition>_returns_<status>`): `test_create_comment_valid_returns_201`,
   `test_create_comment_blank_body_returns_422`, `test_create_comment_on_missing_task_returns_404`,
   `test_list_comments_empty_returns_200_and_empty_list`,
   `test_delete_comment_existing_returns_204_no_body`,
   `test_delete_comment_missing_returns_404`. Would use the existing `client` and `created_task`
   fixtures from `tests/conftest.py` rather than new ones.
4. **Frontend Changes** — There is no separate "task detail view" in `index.html` — everything is
   Kanban cards + one create/edit modal. The natural fit is a comments section *inside the
   existing edit modal* (only shown in edit mode, since a task must exist before it can have
   comments), following the same `escapeText()` pattern already used for card content to avoid
   introducing an XSS gap the rest of the frontend doesn't have.
5. **Migration Notes** — None needed; no database exists to migrate. The only "migration" concern
   is that adding a new in-memory dict doesn't change the shape of the existing `_tasks` dict, so
   this is purely additive to `app/storage.py`.
6. **Open Questions** — (a) Should deleting a task cascade-delete its comments? With two separate
   dicts there's no automatic foreign-key cascade the way there would be in a real database — this
   would need to be handled explicitly in `storage.delete_task`. (b) Should there be a max comment
   count per task, mirroring the existing `MAX_TAGS = 10` pattern in `models.py`? (c) Is
   `author` a free-text string (matching this project's no-auth, no-user-accounts scope) or should
   it eventually tie to a real user identity if auth is ever added?

## Critique of the repo-grounded plan

| Section | Label | Evidence |
|---|---|---|
| Data Model | **Right** | Correctly extends the existing plain-dict/Pydantic-validator pattern instead of inventing a database this repo doesn't have. |
| API Routes | **Right** | Status codes and error-detail wording match `app/main.py`'s existing routes exactly, not generic REST-tutorial conventions. |
| Tests | **Right** | Naming and fixture reuse match `tests/test_tasks.py`'s actual conventions. |
| Frontend Changes | **Right** | Correctly identifies there's no task-detail view to extend, unlike the generic plan's incorrect assumption. |
| Migration Notes | **Right** (trivially) | Correctly identifies there's nothing to migrate, rather than describing a migration step this repo has no tooling for. |
| Open Questions | **Missing** one item | Doesn't ask whether comment `author` should reuse the existing `assignee` free-text pattern from `TaskCreate`/`TaskUpdate` for consistency — a natural question given the rest of the model already establishes that convention. |

## Comparison

- **Biggest difference:** the generic plan invented a database and a migration step that don't
  exist in this project; the grounded plan correctly extended the actual in-memory/Pydantic
  pattern instead.
- **Plan I'd hand to a teammate:** the grounded one, without hesitation — the generic plan's
  first implementation step (`SQLAlchemy migration`) would immediately be wrong and require a
  round of "wait, we don't have a database" correction before any real work could start.
- **Where the generic plan would have been enough:** for a from-scratch project that genuinely
  does use a database and a conventional REST/detail-view frontend, the generic plan's shape
  (nested routes, standard test names, a detail-view comments panel) is a perfectly reasonable
  starting sketch — it just isn't reasonable *for this specific repo*, which is exactly why
  reading the actual files before planning mattered here.

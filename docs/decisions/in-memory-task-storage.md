# In-Memory Dict as the Task Storage Layer

## Context

The Task Tracker backend (`app/storage.py`) has stored all tasks in a single module-level Python
dict (`_tasks: dict[str, TaskResponse]`) since Module 2, and every feature added since — status
transitions, due dates/overdue, tags — has been layered on top of that same dict without ever
introducing a database. Module 4 adds CI and Docker around this backend, which is exactly the
point where "should this still be in-memory?" becomes a fair question to answer explicitly rather
than by default: a CI pipeline and a container image both quietly assume the app can start clean
and be thrown away, which is only true because storage isn't persisted anywhere.

## Decision

Keep the in-memory dict as the storage layer. No database, no file-backed persistence, no ORM.

## Alternatives Considered

- **SQLite with SQLAlchemy/SQLModel.** Would add real persistence across restarts and a more
  production-realistic query layer. Rejected for now: it would require a migration story, change
  how `tests/conftest.py`'s reset fixture works, and add an entire new class of things to get
  wrong (connection handling, schema drift) that this project has no current need for.
- **JSON file persistence** (write `_tasks` to a file on every mutation). Considered as a
  middle ground that would survive a restart without a database. Rejected because it adds file
  I/O error handling and concurrent-write concerns for a single-process learning project, in
  exchange for a benefit (surviving a restart) that doesn't matter for how this app is actually
  used or graded.
- **A database is genuinely needed for the Docker/CI story.** This was a real question going into
  Module 4: does containerizing the app imply it needs to persist data across container restarts?
  The answer here is no — the container's job is to prove the app runs consistently somewhere
  other than a developer's machine, not to add a persistence guarantee nothing in this project's
  scope has asked for.

## Trade-offs

- **What this makes easier:** the entire storage layer is ~90 lines with no external dependency,
  no schema migrations, and a one-line test reset (`storage._reset()`) that autouse-fixtures every
  test on a clean slate. CI and Docker both stay simple because there's no database service to
  spin up alongside the app.
- **What this makes harder:** every restart of the backend (including every `docker run` of a
  fresh container) throws away all task data. That's a real limitation being made explicit here,
  not hidden — the README and `CLAUDE.md` both state it plainly rather than let a future maintainer
  discover it by surprise in production.

## Consequences

- The Docker image is stateless by construction: there is no volume to mount, no persisted file to
  worry about excluding via `.dockerignore`, and no database credentials that could ever leak into
  the image. That actually simplified the Module 4 Docker work — there was nothing to get wrong
  around secrets or volumes.
- The CI workflow doesn't need a services block (e.g. a Postgres service container), which keeps
  `.github/workflows/ci.yml` to a single job with no extra moving parts.
- Anyone who wants to actually deploy this Task Tracker for real, ongoing use (not just as a course
  project) would need to revisit this decision first, before anything else in Module 4's CI/Docker
  work — persistence is the actual blocker, not containerization.

## Open Questions

- If this project ever needed to survive a restart, would the right first step be the JSON-file
  middle ground, or jumping straight to SQLite? I lean toward JSON file first, since it's the
  smaller change and this project's data volume is trivial, but I haven't had a reason to actually
  need this yet.
- Should the `_reset()` test-only function be more clearly firewalled off from ever being reachable
  via the API? Right now it's just not registered as a route, which is sufficient today but is an
  implicit guarantee rather than an explicit one.
- I would do this differently if I already knew the project needed multiple concurrent backend
  processes (e.g. running more than one Uvicorn worker) — the in-memory dict only works correctly
  as a single-process store, and nothing currently stops someone from starting the container with
  `--workers 2` and getting silently inconsistent data between requests.

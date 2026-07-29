from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app import storage
from app.business_rules import validate_status_transition
from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker learning project backend.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "null",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a task.

    Args:
        payload: Task fields from the request body. `title` is required
            (non-blank, <=200 chars); `status`/`priority` default to `ToDo`/
            `Medium`; `due_date` and `tags` are optional.

    Returns:
        The created task with server-generated `id`, `created_at`, `updated_at`.

    Raises:
        HTTPException: Implicitly via FastAPI/Pydantic — HTTP 422 for a
            blank/overlong title, invalid enum value, invalid due_date, or
            invalid tags (blank tag, too many tags, tag too long).
    """
    return storage.add_task(payload)


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    tag: str | None = None,
) -> list[TaskResponse]:
    """List tasks, optionally filtered by status, priority, overdue, and/or tag.

    All filters are optional and combine with logical AND. An empty or
    no-match result returns HTTP 200 with `[]`, never 404.

    Args:
        status: Exact status to filter by.
        priority: Exact priority to filter by.
        overdue: If true/false, only return tasks whose computed
            `is_overdue` matches.
        tag: Only return tasks containing this tag (case-insensitive).

    Returns:
        The matching tasks (possibly empty).
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, tag=tag)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Return a single task by id.

    Raises:
        HTTPException: HTTP 404 with detail `"Task with id {task_id} not
            found"` if no task exists with that id.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Apply a partial update to a task.

    Only fields present in the request body are changed. A status change is
    checked against `validate_status_transition` before being applied; other
    fields (title, description, priority, assignee, due_date, tags) are not
    subject to transition rules.

    Args:
        task_id: Id of the task to update.
        payload: Partial update body; at least one field must be set.

    Raises:
        HTTPException: HTTP 422 if the body has no fields set, or if a
            requested status change is not a valid transition (see
            `app/business_rules.py`); HTTP 404 if the task does not exist.
    """
    if payload.model_dump(exclude_unset=True) == {}:
        raise HTTPException(status_code=422, detail="Update body must include at least one field")

    if payload.status is not None:
        existing_task = storage.get_task_by_id(task_id)
        if existing_task is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing_task.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by id.

    Returns HTTP 204 with an empty body on success.

    Raises:
        HTTPException: HTTP 404 if no task exists with that id.
    """
    if not storage.delete_task(task_id):
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")


@app.get("/health")
def health_check():
    """Liveness check. Returns HTTP 200 with `{"status": "ok", "timestamp": ...}`."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }



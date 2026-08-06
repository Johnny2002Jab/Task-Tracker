from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models import TaskCreate, TaskResponse, TaskUpdate

_tasks: dict[str, TaskResponse] = {}
"""In-memory task store, keyed by task id. Cleared by `_reset()` between tests.
Not persisted: all data is lost when the process restarts."""


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create a task and store it in memory.

    Args:
        payload: Validated task fields from the client (title, description,
            status, priority, assignee, due_date, tags).

    Returns:
        The stored task, with a generated `id`, `created_at`, and `updated_at`.
    """
    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=task_id,
        created_at=now,
        updated_at=now,
        **payload.model_dump(),
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(
    status: Optional[TaskResponse.__fields__["status"].annotation] = None,
    priority: Optional[TaskResponse.__fields__["priority"].annotation] = None,
    overdue: Optional[bool] = None,
    tag: Optional[str] = None,
) -> list[TaskResponse]:
    """Return stored tasks, optionally narrowed by one or more filters.

    Filters combine with logical AND. Each filter is skipped when its value is
    `None`. `overdue` and `tag` match against `TaskResponse.is_overdue` and
    `TaskResponse.tags` respectively; the `tag` match is case-insensitive.

    Args:
        status: Only return tasks with this exact status.
        priority: Only return tasks with this exact priority.
        overdue: Only return tasks whose computed `is_overdue` equals this value.
        tag: Only return tasks that have this tag (case-insensitive).

    Returns:
        Matching tasks, or an empty list if nothing matches or no tasks exist.
    """
    tasks = list(_tasks.values())
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    if priority is not None:
        tasks = [task for task in tasks if task.priority == priority]
    if overdue is not None:
        tasks = [task for task in tasks if task.is_overdue == overdue]
    if tag is not None:
        tag_lower = tag.lower()
        tasks = [task for task in tasks if tag_lower in (t.lower() for t in task.tags)]
    return tasks


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Return the task with the given id, or None if it does not exist."""
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task.

    Only fields explicitly present in `payload` are changed
    (`model_dump(exclude_unset=True)`); omitted fields are left untouched.
    Callers are responsible for business-rule checks (e.g. status-transition
    validation) before calling this function — it applies whatever is in
    `payload` unconditionally.

    Args:
        task_id: Id of the task to update.
        payload: Partial update; unset fields are ignored.

    Returns:
        The updated task, or None if no task exists with that id.
    """
    task = _tasks.get(task_id)
    if task is None:
        return None
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)
    return task


def delete_task(task_id: str) -> bool:
    """Delete a task by id.

    Returns:
        True if a task was deleted, False if no task existed with that id.
    """
    return _tasks.pop(task_id, None) is not None


def _reset() -> None:
    """Clear all stored tasks. Test-only; not exposed via the API."""
    _tasks.clear()
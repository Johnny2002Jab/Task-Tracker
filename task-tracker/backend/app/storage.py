from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.models import TaskCreate, TaskResponse, TaskUpdate

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
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
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = _tasks.get(task_id)
    if task is None:
        return None
    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(task, key, value)
    task.updated_at = datetime.now(timezone.utc)
    return task


def delete_task(task_id: str) -> bool:
    return _tasks.pop(task_id, None) is not None


def _reset() -> None:
    _tasks.clear()
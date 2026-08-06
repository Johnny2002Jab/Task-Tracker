from fastapi import HTTPException, status

from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset(
    {
        (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
        (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
        (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
    }
)


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Raise HTTP 422 if (current, new) is not an allowed status transition.

    Same-status "transitions" (e.g. InProgress -> InProgress) are invalid,
    since they aren't in `VALID_TRANSITIONS`.

    Args:
        current: The task's current status.
        new: The requested new status.

    Raises:
        HTTPException: HTTP 422 with a detail message listing allowed
            transitions, if (current, new) is not in `VALID_TRANSITIONS`.
    """
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{from_status.value}->{to_status.value}" for from_status, to_status in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )

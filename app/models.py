from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, computed_field, field_validator

MAX_TAGS = 10
MAX_TAG_LENGTH = 30


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


def _normalize_tags(tags: Optional[list[str]]) -> list[str]:
    if tags is None:
        return []
    if len(tags) > MAX_TAGS:
        raise ValueError(f"a task may have at most {MAX_TAGS} tags")

    normalized: list[str] = []
    seen_lower: set[str] = set()
    for raw_tag in tags:
        tag = str(raw_tag).strip()
        if not tag:
            raise ValueError("tags must not be blank")
        if len(tag) > MAX_TAG_LENGTH:
            raise ValueError(f"each tag must be {MAX_TAG_LENGTH} characters or fewer")
        if tag.lower() in seen_lower:
            continue
        seen_lower.add(tag.lower())
        normalized.append(tag)
    return normalized


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: list[str] = []

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: str) -> str:
        title = str(value).strip()
        if not title:
            raise ValueError("title must not be blank")
        if len(title) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return title

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> list[str]:
        return _normalize_tags(value)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None
    due_date: Optional[date] = None
    tags: Optional[list[str]] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title(cls, value: str) -> str:
        title = str(value).strip()
        if not title:
            raise ValueError("title must not be blank")
        if len(title) > 200:
            raise ValueError("title must be 200 characters or fewer")
        return title

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, value: Optional[list[str]]) -> list[str]:
        return _normalize_tags(value)


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    due_date: Optional[date] = None
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def is_overdue(self) -> bool:
        if self.due_date is None or self.status == TaskStatus.DONE:
            return False
        return self.due_date < date.today()
"""Task model and input validation. Pure logic, no I/O."""

from __future__ import annotations

import datetime
import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

PRIORITIES = ("low", "med", "high")
STATUSES = ("todo", "done")
MAX_TITLE_LEN = 200

# strptime accepts "2026-1-5"; require the strict zero-padded ISO shape first.
_ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class ValidationError(ValueError):
    """Raised when user input does not satisfy the task rules."""


@dataclass
class Task:
    id: int
    title: str
    priority: str = "med"
    due: Optional[str] = None
    status: str = "todo"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority,
            "due": self.due,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Build a Task from stored data, re-validating every field."""
        if not isinstance(data, dict):
            raise ValidationError("task entry is not an object")
        task_id = data.get("id")
        if not isinstance(task_id, int) or isinstance(task_id, bool) or task_id < 1:
            raise ValidationError("task id must be a positive integer")
        status = data.get("status")
        if status not in STATUSES:
            raise ValidationError("task status must be one of: " + ", ".join(STATUSES))
        return cls(
            id=task_id,
            title=validate_title(data.get("title")),
            priority=validate_priority(data.get("priority")),
            due=validate_due(data.get("due")),
            status=status,
        )


def validate_title(title) -> str:
    if not isinstance(title, str):
        raise ValidationError("title must be text")
    title = title.strip()
    if not title:
        raise ValidationError("title must not be empty")
    if any(unicodedata.category(ch) == "Cc" for ch in title):
        raise ValidationError("title must not contain control characters")
    if len(title) > MAX_TITLE_LEN:
        raise ValidationError("title must be at most %d characters" % MAX_TITLE_LEN)
    return title


def validate_priority(priority) -> str:
    if priority not in PRIORITIES:
        raise ValidationError("priority must be one of: " + ", ".join(PRIORITIES))
    return priority


def validate_due(due) -> Optional[str]:
    """Return the ISO date string, or None when no due date is set."""
    if due is None:
        return None
    if not isinstance(due, str) or not _ISO_DATE.match(due):
        raise ValidationError("due date must be YYYY-MM-DD")
    try:
        datetime.date.fromisoformat(due)
    except ValueError:
        raise ValidationError("due date is not a real calendar date: " + due) from None
    return due


def due_sort_key(task: Task):
    """Sort by due date ascending, tasks without a due date last, ties by id."""
    return (task.due is None, task.due or "", task.id)

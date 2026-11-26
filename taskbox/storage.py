"""JSON file persistence with atomic writes."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import List, Tuple

from .models import Task, ValidationError

FORMAT_VERSION = 1
ENV_VAR = "TASKBOX_FILE"


class StorageError(Exception):
    """Raised when the data file cannot be read, parsed or written."""


def resolve_path(cli_path=None) -> Path:
    """Pick the data file: --file, then $TASKBOX_FILE, then ~/.taskbox/tasks.json."""
    if cli_path:
        return Path(cli_path)
    env = os.environ.get(ENV_VAR)
    if env:
        return Path(env)
    return Path.home() / ".taskbox" / "tasks.json"


def load_tasks(path: Path) -> Tuple[List[Task], int]:
    """Return (tasks, next_id). A missing or empty file means an empty store."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return [], 1
    except OSError as exc:
        raise StorageError("cannot read %s: %s" % (path, exc)) from exc
    except UnicodeDecodeError as exc:
        raise StorageError("%s is not valid UTF-8 (%s); fix or remove it" % (path, exc)) from exc
    if not raw.strip():
        return [], 1
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise StorageError("%s is not valid JSON (%s); fix or remove it" % (path, exc)) from exc
    if not isinstance(data, dict) or data.get("version") != FORMAT_VERSION:
        raise StorageError("%s has an unsupported format or version" % path)
    entries = data.get("tasks")
    next_id = data.get("next_id")
    if not isinstance(entries, list) or not isinstance(next_id, int) or isinstance(next_id, bool):
        raise StorageError("%s has a malformed structure" % path)
    try:
        tasks = [Task.from_dict(entry) for entry in entries]
    except ValidationError as exc:
        raise StorageError("%s contains an invalid task: %s" % (path, exc)) from exc
    highest = max((t.id for t in tasks), default=0)
    return tasks, max(next_id, highest + 1)


def save_tasks(path: Path, tasks: List[Task], next_id: int) -> None:
    """Write atomically: temp file in the same directory, then os.replace."""
    path = Path(path)
    payload = {
        "version": FORMAT_VERSION,
        "next_id": next_id,
        "tasks": [t.to_dict() for t in tasks],
    }
    tmp_name = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=".taskbox-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_name, path)
    except OSError as exc:
        if tmp_name and os.path.exists(tmp_name):
            os.unlink(tmp_name)
        raise StorageError("cannot write %s: %s" % (path, exc)) from exc

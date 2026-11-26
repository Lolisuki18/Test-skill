"""Command-line interface: argument parsing and command handlers."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from . import __version__
from .models import (
    PRIORITIES,
    STATUSES,
    Task,
    ValidationError,
    due_sort_key,
    validate_due,
    validate_priority,
    validate_title,
)
from .storage import StorageError, load_tasks, resolve_path, save_tasks


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="taskbox", description="A tiny command-line task tracker.")
    parser.add_argument("--version", action="version", version="taskbox " + __version__)
    parser.add_argument("--file", help="data file (default: $TASKBOX_FILE or ~/.taskbox/tasks.json)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="add a task")
    p_add.add_argument("title")
    p_add.add_argument("--priority", choices=PRIORITIES, default="med")
    p_add.add_argument("--due", metavar="YYYY-MM-DD")

    p_list = sub.add_parser("list", help="list tasks")
    p_list.add_argument("--status", choices=STATUSES)
    p_list.add_argument("--priority", choices=PRIORITIES)
    p_list.add_argument("--sort", choices=("due",))

    p_done = sub.add_parser("done", help="mark a task as done")
    p_done.add_argument("id", type=int)

    p_del = sub.add_parser("delete", help="delete a task")
    p_del.add_argument("id", type=int)
    return parser


def _find(tasks: List[Task], task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    raise ValidationError("no task with id %d" % task_id)


def cmd_add(args, path) -> int:
    title = validate_title(args.title)
    priority = validate_priority(args.priority)
    due = validate_due(args.due)
    tasks, next_id = load_tasks(path)
    tasks.append(Task(id=next_id, title=title, priority=priority, due=due))
    save_tasks(path, tasks, next_id + 1)
    print("Added task %d: %s" % (next_id, title))
    return 0


def cmd_list(args, path) -> int:
    tasks, _ = load_tasks(path)
    if args.status:
        tasks = [t for t in tasks if t.status == args.status]
    if args.priority:
        tasks = [t for t in tasks if t.priority == args.priority]
    tasks = sorted(tasks, key=due_sort_key) if args.sort == "due" else sorted(tasks, key=lambda t: t.id)
    if not tasks:
        print("No tasks.")
        return 0
    print("%-4s %-6s %-4s %-10s  %s" % ("ID", "STATUS", "PRIO", "DUE", "TITLE"))
    for t in tasks:
        print("%-4d %-6s %-4s %-10s  %s" % (t.id, t.status, t.priority, t.due or "-", t.title))
    return 0


def cmd_done(args, path) -> int:
    tasks, next_id = load_tasks(path)
    task = _find(tasks, args.id)
    if task.status == "done":
        print("Task %d is already done." % task.id)
        return 0
    task.status = "done"
    save_tasks(path, tasks, next_id)
    print("Task %d marked done." % task.id)
    return 0


def cmd_delete(args, path) -> int:
    tasks, next_id = load_tasks(path)
    task = _find(tasks, args.id)
    tasks.remove(task)
    save_tasks(path, tasks, next_id)
    print("Deleted task %d." % task.id)
    return 0


_HANDLERS = {"add": cmd_add, "list": cmd_list, "done": cmd_done, "delete": cmd_delete}


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    path = resolve_path(args.file)
    try:
        return _HANDLERS[args.command](args, path)
    except (ValidationError, StorageError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

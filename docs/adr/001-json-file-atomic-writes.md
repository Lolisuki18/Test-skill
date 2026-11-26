# 001. Store tasks in one JSON file, written atomically

- **Status:** Accepted
- **Date:** 2026-11-26 (date of `plan/001-taskbox.md`; implemented in commit `b0fea6d`)
- **Deciders:** [Cần bổ sung: deciders - plan lists none]
- **Related:** [ADR 002](002-never-overwrite-corrupt-file.md), `plan/001-taskbox.md` R6, section 4

## Context

taskbox is a local, single-user command-line tool written with the Python standard library only (`plan/001-taskbox.md` section 1: "third-party packages" are out of scope; "multi-user" is out of scope). Tasks must survive between runs. The plan requires that an interrupted write never leaves a half-written file (plan section 5, last edge case).

Current state: `taskbox/storage.py` reads and writes one JSON file with `{"version": 1, "next_id": int, "tasks": [...]}` (`taskbox/storage.py:13`, `:61-80`). The path is `--file`, else `$TASKBOX_FILE`, else `~/.taskbox/tasks.json` (`taskbox/storage.py:21-28`). A save creates the parent folder, writes a temp file in the same folder (`tempfile.mkstemp`, `storage.py:72`) and then calls `os.replace` (`storage.py:76`).

## Options Considered

### Option 1: One JSON file, temp file + `os.replace` (chosen)
- Description: whole store serialized on every write.
- Pros: standard library only; human-readable; an interrupted write leaves the previous file intact (the temp file is the only partial artifact).
- Cons: whole file rewritten on each change; no locking.

### Option 2: Write the JSON file in place
- Description: open the data file for writing and dump the JSON.
- Pros: fewer lines of code.
- Cons: a crash during the write can leave a truncated file, which the plan forbids (plan section 5).
- Note: the plan states the requirement, not that this option was discussed. `[Cần bổ sung: confirm whether in-place write was actually considered]`

### Other options
`[Cần bổ sung: other options considered, e.g. a database; neither the plan nor the git log mentions any]`

## Decision

We store all tasks in a single JSON file and replace it atomically on every write. This applies to every command that changes data (`add`, `done`, `delete`); `list` only reads. The stored `next_id` keeps ids from being reused after `delete` (`taskbox/storage.py:58`; plan section 5).

## Consequences / Trade-offs

- **Positive:** no dependencies; the file can be read and fixed by hand; a failed write does not damage the previous file.
- **Negative / costs:** no file locking, so two taskbox processes running at once can lose an update (plan section 8, accepted for a single-user tool). On Windows `os.replace` can fail if another process holds the file; this surfaces as `StorageError` and is not retried (plan section 8).
- **Risks and how they are checked:** unit tests in `tests/test_storage.py` cover round-trip, missing file and new-subfolder cases (plan section 6, R6).
- **Follow-ups:** file locking is listed as an optional follow-up in plan section 10.

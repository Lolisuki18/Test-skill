# 002. Never overwrite a data file that cannot be read

- **Status:** Accepted
- **Date:** 2026-11-26 (rule in `plan/001-taskbox.md` R6; extended by commits `9a50011` and `ac9ee0a`)
- **Deciders:** [Cần bổ sung: deciders - plan lists none]
- **Related:** [ADR 001](001-json-file-atomic-writes.md), `plan/001-taskbox.md` R6

## Context

The data file is the only copy of the user's tasks. If it is damaged (hand-edited, written by another tool), a command that treated it as empty and saved would erase the remaining content. The plan therefore requires "corrupt JSON -> clear error, exit 1, file NOT overwritten" (plan R6).

Current state: `load_tasks` raises `StorageError` for an unreadable file, invalid UTF-8, invalid or too deeply nested JSON, an unsupported `version`, a malformed structure, or an invalid task entry (`taskbox/storage.py:37-56`). `main` catches it, prints `error: ...` to stderr and returns 1 (`taskbox/cli.py:110-112`). Every command loads before it saves, so a failed load stops the command before any write. A missing file or a file with only whitespace is the only case treated as an empty store (`storage.py:35-36`, `:41-42`).

Two later fixes on branch `fix/list-bad-path` widened the rule: `9a50011` (a UTF-16 file raised an uncaught `UnicodeDecodeError` and printed a traceback) and `ac9ee0a` (a deeply nested file raised `RecursionError`).

## Options Considered

### Option 1: Stop with an error and leave the file untouched (chosen)
- Pros: no data loss; the user can repair the file; clear message naming the path.
- Cons: the tool is unusable until the user fixes or removes the file by hand.

### Option 2: Treat an unreadable file as empty and overwrite it
- Pros: the tool keeps working.
- Cons: silently destroys whatever was in the file. Contradicts plan R6.
- Note: `[Cần bổ sung: confirm this option was discussed; the plan only states the chosen rule]`

### Option 3: Rename the bad file to a backup, then start empty
`[Cần bổ sung: not found in plan, code or git log; listed only as a possibility for the team to confirm or delete]`

## Decision

We never write to a data file that `load_tasks` rejects. Any `StorageError` ends the command with exit code 1 and the file is left byte-for-byte as it was. The message tells the user to "fix or remove it" (`taskbox/storage.py:40,46`); taskbox does not repair or back up the file itself. Applies to all four commands, including `list`.

## Consequences / Trade-offs

- **Positive:** a damaged file is never made worse by taskbox; tests assert the file is unchanged (`tests/test_cli.py` `test_C12_non_utf8_file_reports_error_without_traceback`, `tests/test_storage.py` `test_S3_deeply_nested_json_raises_storage_error`).
- **Negative / costs:** the user must repair or delete the file manually before using taskbox again; there is no automatic backup.
- **Risks and how they are checked:** new failure modes of reading a file (as the two later fixes showed) must be mapped to `StorageError`, otherwise a traceback appears instead of exit 1. Checked by the corrupt-file tests listed above.
- **Follow-ups:** none recorded in the plan.

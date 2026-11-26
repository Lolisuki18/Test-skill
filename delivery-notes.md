# Delivery notes - taskbox: DEF-001/DEF-002 fix to release

## Stage 0 - Kickoff - 2026-11-26 - status: Done
Existing artifacts kept (user said "continue"): plan/001-taskbox.md (Done), qa-artifacts/01..05 (+02b, 04b), docs/, README.md, CHANGELOG.md. No tags. Skill sets installed: all four (user).
Entry point: Stage 1 as a bug-fix loop (bug-investigator), because QA round 1 is Conditional Go with DEF-001 (Major) and DEF-002 (Minor) open. No new plan file created (plan 001 is Done and its R1, R2, R5 cover the fixes).
Branch: fix/console-encoding-and-newline-title (cut from fix/list-bad-path). Nothing pushed.

## Stage 1 - Build - 2026-11-26 - status: Done
Artifacts: taskbox/cli.py (`_make_output_safe`, called at start of `main`), taskbox/models.py (`validate_title` rejects Cc characters), tests/test_models.py (+2 tests), tests/test_console_encoding.py (4 tests, real subprocess with PYTHONIOENCODING=cp1252), plan/001-taskbox.md (note + count), commit 81d0868.
Real results:
- Reproduced before fix: `UnicodeEncodeError: 'charmap' codec can't encode character '☕'`, exit 1 for add and list.
- New regression tests failed before the fix (7 failures, `Ran 66 tests ... FAILED (failures=7)`), pass after.
- `python -W error -m unittest discover -s tests -t .` -> `Ran 66 tests in 0.906s OK` (baseline was 60).
- `python -m py_compile taskbox/*.py` OK. No formatter/linter (plan section 8: declined).
- After fix with PYTHONIOENCODING=cp1252: `Added task 1: Buy coffee ?` exit 0; list prints the table, exit 0; `add $'line1\nline2'` -> `error: title must not contain control characters`, exit 1.
Open items: unprintable characters now display as `?` on a narrow console (by design, stored data keeps the emoji). TC-ENC-005 (real interactive terminal) not run. A stored title with a control character (none known outside QA temp files) would now fail to load (StorageError path via from_dict); not tested with such a file.
Decisions: see table.

## Stage 2 - Pull Request - 2026-11-26 - status: Done (PR text drafted; PR not opened, nothing pushed)
Artifacts: branch fix/console-encoding-and-newline-title (1 commit 81d0868 on top of fix/list-bad-path 40d2564); PR text below. Base for the diff: fix/list-bad-path (origin/main is gone; local `main` is b0fea6d, so the real PR base is [Needs input: PR base branch]).
Real results: pre-pr-self-review verdict "ready to open"; R1, R2, R5 covered (traced + ran). Re-ran `python -W error -m unittest discover -s tests -t .` -> 66 tests OK.
Open items (worth considering, accepted): U+2028 (category Zl) in a title is still accepted (ran: `add` exit 0, stored); a stored title with a control character would now fail to load via Task.from_dict; reconfigure() changes the real sys.stdout for the process; commit mixes DEF-001 and DEF-002 in one commit (split proposed by commit-message-writer, user kept one commit).

### PR text
Title: fix: no crash on unprintable console text; reject control chars in titles

**Problem**
On a cp1252 Windows console `taskbox add "Buy coffee <emoji>"` saves the task and then crashes with `UnicodeEncodeError` (exit 1); `list` then crashes on every call (DEF-001). A title with a line break is accepted and breaks the `list` table (DEF-002).

**Cause**
`print()` writes to a strict cp1252 `sys.stdout` (`cli.py` cmd_add/cmd_list); unit tests capture output in `io.StringIO`, which has no code page. `validate_title` checked only type, empty and length.

**Fix**
`main()` sets stdout/stderr `errors="replace"` (unprintable characters show as `?`, stored data is unchanged). `validate_title` rejects control characters (category Cc) with `error: title must not contain control characters`, exit 1.

**How to verify**
`PYTHONIOENCODING=cp1252 python -m taskbox add "Buy coffee <emoji>"` -> exit 0; `list` prints the table. `add $'a
b'` -> error, exit 1. Tests: `tests/test_console_encoding.py` (real subprocess on cp1252), `ControlCharacterTitleTests` in `tests/test_models.py`; `python -W error -m unittest discover -s tests -t .` -> 66 OK.

**Notes**
U+2028 is still accepted; titles already stored with control characters will not load. Tests: [CI result: no CI configured]. Closes DEF-001, DEF-002 (qa-artifacts/04-defects.md).

## Stage 3 - QA - status: not started
## Stage 4 - Docs - status: not started
## Stage 5 - Release - status: not started

## Decisions
| Date | Decision | By |
|---|---|---|
| 2026-11-26 | Continue from existing plan/qa-artifacts/docs; all four sets installed | user |
| 2026-11-26 | Fix = errors="replace" on stdout/stderr + reject control chars in titles | user (ok at bug-investigator hard stop) |
| 2026-11-26 | Keep DEF-001 and DEF-002 in one commit; accept the Notes-level risks | user |

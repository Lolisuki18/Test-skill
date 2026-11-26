# Defect Log — taskbox 0.1.0 (CLI task tracker)
- **Phase:** 4/5 — Defect Management
- **Date:** 2026-11-26
- **Version:** v0.2
- **Status:** Draft (round 2: both defects Closed by the user; TC-ENC-005 still Not Run)
- **Requirement source:** `qa-artifacts/03-execution-notes.md` round 1 (build `ac9ee0a`), `qa-artifacts/02-test-matrix.md`
- **Approver:** n/a (no hard stop in Phase 4)

## 1. Summary table
| Defect ID | Title | Severity | Priority | Status | Related TC |
|---|---|---|---|---|---|
| DEF-001 | [Console output] `add`/`list` crash with a Python traceback when a title has a character the console code page cannot print (e.g. `☕` on cp1252) | Major | P1 (proposed) | Closed (user, 2026-11-26, after round 2 Pass) | TC-ENC-001, TC-ENC-002 |
| DEF-002 | [Add] A title containing a line break is accepted and breaks the `list` table | Minor | P3 (proposed) | Closed (user, 2026-11-26, after round 2 Pass) | TC-ADD-008 |

## 2. Defect details

### DEF-001 — [Console output] `add`/`list` crash with a traceback when a title has a character the console code page cannot print
| Field | Content |
|---|---|
| Title | [Console output] `add`/`list` crash with a Python traceback when a title has a character the console code page cannot print (e.g. `☕` on cp1252) |
| Related TC | TC-ENC-001, TC-ENC-002 (one cause, two symptoms, so one defect) |
| Environment | Windows 11 10.0.26200, Python 3.14.6, taskbox 0.1.0 at commit `ac9ee0a`, branch `fix/list-bad-path`; stdout/stderr redirected to a pipe, locale code page cp1252, `PYTHONUTF8` and `PYTHONIOENCODING` unset. Interactive console (Windows Terminal / cmd): `[Needs input: not run, TC-ENC-005]` |
| Severity / Priority | Major / P1 (proposed). Severity: a main function (`add`, `list`) fails for a valid title and there is a workaround (`PYTHONUTF8=1`), no data loss, so not Critical. Priority: any Windows user typing an emoji or non-Latin title hits it, and `list` stays unusable until the task is deleted; PO to confirm. |
| Status | New |
| Reproducibility | Always (4/4 attempts: 2 manual shell runs, 2 runs of the scripted case) |
| Pre-conditions | `TASKBOX_FILE` points to a temp file; `PYTHONUTF8` unset |
| Steps to Reproduce | 1. `set TASKBOX_FILE=<temp>\u.json` (or export in bash)<br>2. Run `python -m taskbox add "Buy coffee ☕"`<br>3. Note exit code and output<br>4. Open `u.json`<br>5. Run `python -m taskbox list` |
| Actual Result | Step 2 prints a traceback ending `UnicodeEncodeError: 'charmap' codec can't encode character '☕' in position 25`, exit code 1, no `Added task` line. Step 4: the task IS stored (`"id": 1, "title": "Buy coffee ☕"`, `next_id` 2). Step 5 prints only the header line, then the same traceback, exit 1. A later `add Café` and `done 1` still work; `list` fails on every call while that task exists. |
| Expected Result | Exit 0 and a normal `Added task 1: ...` line (unprintable characters may be replaced) and `list` prints the table; no traceback. Sources: plan 001 section 5 ("unicode title kept intact"), R1 "prints its id", R2 "prints tasks", plan R5 "violations -> message on stderr" (a traceback is not a message); TC-ENC-001/002. |
| Evidence | Real output (QA run 2026-11-26):<br>`File ".../taskbox/cli.py", line 61, in cmd_add` `print("Added task %d: %s" % (next_id, title))`<br>`File ".../taskbox/cli.py", line 77, in cmd_list` `print("%-4d %-6s %-4s %-10s  %s" % (...))`<br>`UnicodeEncodeError: 'charmap' codec can't encode character '☕' in position 34: character maps to <undefined>`<br>Workaround check, TC-ENC-003: with `PYTHONUTF8=1` both commands succeed and `list` shows `1    done   med  -           Buy coffee ☕`.<br>Files: `qa-artifacts/03-execution-notes.md` section 3 (raw output); `qa-artifacts/tools/results.json`. Screenshot: None yet. |
| Notes / Hypothesis (unconfirmed) | The state is saved before the message is printed (`save_tasks` precedes `print` in `cmd_add`), which is why the file contains the task although the command reports failure. The repo's 60 unit tests capture output in `io.StringIO`, which has no code page, so they cannot see this. Cause of the cp1252 stdout and the fix are for the developer to decide. |

### DEF-002 — [Add] A title containing a line break is accepted and breaks the `list` table
| Field | Content |
|---|---|
| Title | [Add] A title containing a line break is accepted and breaks the `list` table |
| Related TC | TC-ADD-008 |
| Environment | Windows 11 10.0.26200, Python 3.14.6, taskbox 0.1.0 at commit `ac9ee0a`, Git Bash shell, temp `TASKBOX_FILE` |
| Severity / Priority | Minor / P3 (proposed). Severity: secondary presentation problem, no data loss, easy to avoid. Priority: PO to confirm; low urgency. |
| Status | New |
| Reproducibility | Always (2/2 attempts) |
| Pre-conditions | No data file |
| Steps to Reproduce | 1. In a bash shell run `python -m taskbox add $'line1\nline2'`<br>2. Run `python -m taskbox list` |
| Actual Result | Step 1: `Added task 1: line1` / `line2`, exit 0. Step 2: `1    todo   med  -           line1` and the text `line2` on a separate line outside the column layout, exit 0. |
| Expected Result | Rejected with an `error:` line and exit 1. Source: `01-test-plan.md` section 8 item 2 (default "reject control characters", accepted by the user at the Phase 1 approval). The original spec R5 does not mention control characters, so if the PO decides they are allowed this becomes "Won't Fix / spec change". |
| Evidence | Real output of the two commands above (see `03-execution-notes.md`, TC-ADD-008). Screenshot: None yet. |
| Notes / Hypothesis (unconfirmed) | `validate_title` in `taskbox/models.py` only checks type, empty and length. |

## 3. Re-test history
| Defect ID | Round | Build | Result | Regression checked |
|---|---|---|---|---|
| DEF-001 | 2 | `81d0868` | Pass. Original steps on a cp1252 pipe: `add "Buy coffee ☕"` -> `Added task 1: Buy coffee ?`, exit 0; `list` prints the table, exit 0 (TC-ENC-001/002 Pass in `03-execution-notes.md` R2.2). Variants: TC-ENC-003 (PYTHONUTF8=1) and TC-ENC-004 (Café) Pass. Not tested: real interactive terminal (TC-ENC-005 Not Run). Behaviour note: the emoji is shown as `?` on a narrow console, the stored data keeps it. | 66 unit tests OK; all 66 Auto cases Pass; TC-ADD-001, TC-LIST-001, TC-STORE-004 Pass (conditions of `05-summary-report.md` v0.1) |
| DEF-002 | 2 | `81d0868` | Pass. `add $'line1
line2'` -> `error: title must not contain control characters`, exit 1, nothing saved (TC-ADD-008 Pass). Variants ``, `	` rejected; trailing newline trimmed. | TC-VAL-001..004, TC-STORE-006/007/014 Pass |

> **QA Advisor**
> - *Why Severity and Priority are separate:* DEF-001 is technically Major (a main command fails) but its urgency depends on how many users run Windows consoles with non-Latin text; that call is the PO's.
> - *Easily underrated:* a command that saves and then reports failure (DEF-001) invites a retry, and a retry saves the task a second time (verified: two failing `add "Buy coffee ☕"` calls, both exit 1, `list` with `PYTHONUTF8=1` then shows ids 1 and 2 with the same title).
> - *Default I rated:* DEF-001 Major/P1, DEF-002 Minor/P3. Say "raise" or "lower" to change.

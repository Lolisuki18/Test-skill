# Regression Plan — build `ac9ee0a` (taskbox 0.1.0)
- **Phase:** 4/5 — Defect Management (regression)
- **Date:** 2026-11-26
- **Version:** v0.2
- **Status:** Draft
- **Requirement source:** `qa-artifacts/02-test-matrix.md` (RTM), `qa-artifacts/04-defects.md`, `git diff 9a50011 ac9ee0a`
- **Approver:** [Needs input: user to confirm the layer to run]

## 1. Change summary
- Base to target: `9a50011` (fix: non-UTF-8 data file) to `ac9ee0a` (fix: deeply nested JSON reported as `StorageError`). Branch `fix/list-bad-path`.
- Change set from `git diff 9a50011 ac9ee0a`: `taskbox/storage.py` line 45, `except json.JSONDecodeError` becomes `except (json.JSONDecodeError, RecursionError)`; `tests/test_storage.py` +3 lines (one new test). Nothing else.
- Defects fixed in this build (from `04-defects.md`): none. DEF-001 and DEF-002 are open and unrelated to this change.
- Note: the previous fix `9a50011` touched `load_tasks` too (UTF-8 decode) and `tests/test_cli.py`; it is included in the neighbour set below.

## 2. Impact table
| Changed area | Impacted requirements | Cases | Why | Layer |
|---|---|---|---|---|
| `storage.py:45` JSON parse error handling in `load_tasks` | R6 | TC-STORE-004, TC-STORE-009 | Direct change; TC-STORE-009 is the exact case (200000 `[`), TC-STORE-004 is the sibling corrupt-JSON path in the same `try` | Targeted |
| `load_tasks` is called by every command (`cli.py:58,66,82,94`) | R1, R2, R3, R4, R6 | TC-STORE-001, TC-STORE-003, TC-STORE-005, TC-STORE-006, TC-STORE-007, TC-STORE-008, TC-STORE-014 | Same function, other branches (missing, empty, version, structure, UTF-8, BOM, invalid task); neighbour of the changed `except` | Targeted |
| Smoke: P0 main flows | R1, R3, R4, R5, R6 | TC-ADD-001, TC-DONE-001, TC-DONE-003, TC-DEL-001, TC-DEL-002, TC-VAL-016, TC-STORE-004, TC-STORE-007 | P0 rule | Smoke |
| Shared decode path used by commands that read then write | R2 | TC-LIST-001, TC-LIST-012 | `list` reads through the changed function | Targeted |
| Past-defect hotspot: console output (`cli.py` print calls, DEF-001/002) | R1, R2 | TC-ENC-001, TC-ENC-002, TC-ENC-003, TC-ENC-004, TC-ADD-008 | Not changed by this build; kept so the open defects are re-observed, not re-tested for a fix | Targeted (observe only) |

## 3. Layers
- **Smoke (8 cases):** TC-ADD-001, TC-DONE-001, TC-DONE-003, TC-DEL-001, TC-DEL-002, TC-VAL-016, TC-STORE-004, TC-STORE-007. Stop and report if any fails.
- **Targeted (smoke plus 14 more):** TC-STORE-001, 003, 004, 005, 006, 007, 008, 009, 014; TC-LIST-001, 012; TC-ENC-001..004; TC-ADD-008 (the last five only to re-observe the open defects).
- **Full:** all 70 cases plus the 60 unit tests plus NF-PERF-01/02 and NF-SEC-01. Recommended only if smoke or targeted shows a new failure.

## 4. Excluded cases
All cases of R2 filters/sort (TC-LIST-002..011), R5 validation (TC-VAL-001..015), TC-DONE-002/004..006, TC-DEL-003..005, TC-STORE-002, 010..013, TC-CLI-*: no code in these paths changed (`git diff` touches only `storage.py:45`), and `models.py` / `cli.py` were not modified between the two commits. Not skipped by anyone's decision, only not selected; no P0 case is excluded (all P0 are in smoke).

## 5. Effort
- Auto cases: the whole scripted set of 66 cases ran in one pass in round 1 (duration not timed: `[Needs input: exact duration]`), the 60 unit tests ran in 0.315 s.
- Manual cases: TC-ADD-008 only (about 1 minute by hand). Everything else in the selected layers can run unattended.

## 6. Entry / exit conditions
- Entry: `git status` shows `taskbox/` and `tests/` unchanged; temp data folder.
- Stop and report when any smoke case fails. Escalate to Full if more than 10% of targeted cases fail (suggested; `[Needs input: agreed share]`).
- Evidence already available: all smoke and targeted cases were executed in round 1 on exactly this build (`ac9ee0a`); TC-STORE-004/009 Pass (see `03-execution-notes.md`). A second run is only needed for the next build.

> **QA Advisor**
> - *Why these layers:* a one-line change in the JSON error path touches one requirement (R6) but every command calls `load_tasks`, so smoke plus the R6 sibling cases is enough; a full run would repeat 60 cases that cannot be affected.
> - *Blind spots that remain:* other exceptions `json.loads` can raise (e.g. `MemoryError`, huge numbers) have no case; config and data changes map to no case.
> - *Default I will choose if you do not reply:* run smoke first, then targeted, full only on a failure.


---
# Round 2 — build `81d0868` (fix for DEF-001, DEF-002)
Version v0.2. The section above stays as the plan for build `ac9ee0a`.

## R2.1 Change summary
- Base to target: `40d2564` to `81d0868` (`git diff fix/list-bad-path...HEAD`): `taskbox/cli.py` +`_make_output_safe()` called first in `main()` (stdout/stderr `errors="replace"`); `taskbox/models.py` `validate_title` rejects category-Cc characters; tests: `tests/test_console_encoding.py` (new, 4), `tests/test_models.py` (+2).
- Defects fixed in this build: DEF-001, DEF-002.

## R2.2 Impact table
| Changed area | Impacted requirements | Cases | Why | Layer |
|---|---|---|---|---|
| `cli.py` `main()` runs for every command | R1-R6 | all `Auto (API)` cases | `main()` is the entry of every command; reconfiguring stdout/stderr can alter every printed line | Full (Auto only: one scripted pass of 66 cases is cheap) |
| `models.py` `validate_title` (also called by `Task.from_dict` when loading) | R1, R5, R6 | TC-ADD-001..008, TC-VAL-001..004, TC-STORE-006/007/014, TC-ENC-001/002 | Direct change; load path re-validates stored titles | Targeted (covered by the full Auto pass) |
| Smoke: P0 | R1, R3, R4, R5, R6 | TC-ADD-001, TC-DONE-001, TC-DONE-003, TC-DEL-001, TC-DEL-002, TC-VAL-016, TC-STORE-004, TC-STORE-007 | P0 rule | Smoke |
| Defect re-test | R1, R2, R5 | TC-ENC-001, TC-ENC-002, TC-ENC-003, TC-ENC-004, TC-ADD-008 | Original steps of DEF-001/002 | Re-test |

## R2.3 Layers run
- Smoke + Targeted + all 66 Auto cases in one scripted pass; Manual TC-ADD-008 run by hand.
- Excluded: Manual TC-STORE-015/016 (concurrency and read-only file; no change in `storage.py`, evidence: `git diff --stat` shows no `storage.py`), NF-* cases (no timing-relevant change: one `reconfigure` call; NF-PERF not re-run, [Needs input: confirm]), TC-ENC-005 (needs the user's terminal).
- Process note: the scripted pass was run before the user confirmed this plan (the harness has no partial mode); the plan was written from the same change set afterwards.

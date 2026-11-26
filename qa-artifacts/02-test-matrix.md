# Test Matrix — taskbox 0.1.0 (CLI task tracker)
- **Phase:** 2/5 — Test Matrix
- **Date:** 2026-11-26
- **Version:** v0.1
- **Status:** Approved (approved on: 2026-11-26, user said "approved"; defaults accepted)
- **Requirement source:** `qa-artifacts/01-test-plan.md` v0.2 (Approved), `plan/001-taskbox.md` R1–R6; expected results cross-checked against `taskbox/` code
- **Approver:** project owner (user)
- **Source of truth:** the cases are defined in `qa-artifacts/tools/matrix_cases.py`; this table is generated from it so the table and the run cannot drift.

## 1. Overview
Cases: 70 | P0: 8 | P1: 23 | P2: 31 | P3: 8 | Manual: 4 | Auto (browser): 0 | Auto (API): 66
(`Auto (API)` = scripted command-line run with a temp `TASKBOX_FILE`, see plan §4 mapping note. Priorities follow plan §3 risk: data-loss cases raised to P0 by the user; core CRUD happy paths and unknown-id safety P0 as smoke set.)

## 2. Test Cases
| TC ID | Req/UC ID | Module | Title | Pre-condition | Test Steps | Test Data | Expected Result | Priority | Execution Type |
|---|---|---|---|---|---|---|---|---|---|
| TC-ADD-001 | R1 | ADD | Add with title only creates task 1, med/todo, no due | Temp data file does not exist | 1. Run `add "Buy milk"`<br>2. Read the data file | title=Buy milk | Exit 0; stdout contains `Added task 1: Buy milk`; file holds one task id 1, priority med, status todo, due null | P0 | Auto (API) |
| TC-ADD-002 | R1 | ADD | Add with --priority high and --due stores both values | No data file | 1. Run `add Report --priority high --due 2026-12-01`<br>2. Read the data file | priority=high, due=2026-12-01 | Exit 0; stored priority `high`, due `2026-12-01` | P1 | Auto (API) |
| TC-ADD-003 | R1 | ADD | Second add gets id 2 | No data file | 1. Run `add one`<br>2. Run `add two` | titles one, two | Second add prints id 2; file ids are [1, 2] | P1 | Auto (API) |
| TC-ADD-004 | R1, R4 | ADD | Id is not reused after delete (next add gets 3) | No data file | 1. `add a`<br>2. `add b`<br>3. `delete 2`<br>4. `add c` | titles a, b, c | Step 4 prints `Added task 3` | P1 | Auto (API) |
| TC-ADD-005 | R1, R6 | ADD | Accented title (cp1252-safe) is stored as real UTF-8, not \u escapes | No data file | 1. Run `add "Café crème"`<br>2. Read the file bytes as UTF-8 | title=Café crème | Exit 0; file text contains `Café crème` literally | P2 | Auto (API) |
| TC-ADD-006 | R1 | ADD | Title starting with `-` can be added after `--` | No data file | 1. Run `add -- -dash` | title=-dash | Exit 0; stored title `-dash` | P2 | Auto (API) |
| TC-ADD-007 | R1 | ADD | Title starting with `-` without `--` is rejected as a usage error, file untouched | No data file | 1. Run `add -dash` | title=-dash | Exit 2 (argparse); no file created; wording of message `[Needs input: exact error message]` | P3 | Auto (API) |
| TC-ADD-008 | R1, R5 | ADD | Title containing a newline: behaviour is observed and recorded | No data file | 1. In a shell run `add $'line1\nline2'`<br>2. Run `list`<br>3. Note whether it is rejected or accepted and how the table looks | title=line1<LF>line2 | [Needs input: expected behaviour for control characters; plan default is reject] | P3 | Manual |
| TC-VAL-001 | R5, R1 | VAL | Empty title is rejected, exit 1, file not created | No data file | 1. Run `add ""` | title=(empty) | Exit 1; stderr contains `title must not be empty`; no data file | P1 | Auto (API) |
| TC-VAL-002 | R5, R1 | VAL | Whitespace-only title is rejected, exit 1 | No data file | 1. Run `add "   "` | title=3 spaces | Exit 1; stderr contains `must not be empty` | P1 | Auto (API) |
| TC-VAL-003 | R5 | VAL | Title of exactly 200 characters is accepted | No data file | 1. Run `add` with 200 x's | title=x*200 | Exit 0; stored length 200 | P1 | Auto (API) |
| TC-VAL-004 | R5, R1 | VAL | Title of 201 characters is rejected, exit 1, file not created | No data file | 1. Run `add` with 201 x's | title=x*201 | Exit 1; stderr contains `at most 200`; no data file | P1 | Auto (API) |
| TC-VAL-005 | R5 | VAL | Surrounding whitespace is trimmed before saving | No data file | 1. Run `add "  padded  "` | title=2 spaces+padded+2 spaces | Stored title `padded` | P2 | Auto (API) |
| TC-VAL-006 | R5 | VAL | Limit is counted after trim: 200 chars plus padding is accepted | No data file | 1. Run `add` with 2 spaces + 200 x's + 2 spaces | title=204 chars raw | Exit 0 (plan open question 2 default: count after trim) | P2 | Auto (API) |
| TC-VAL-007 | R5, R1 | VAL | Invalid priority `urgent` is rejected by argparse, exit 2, file not created | No data file | 1. Run `add X --priority urgent` | priority=urgent | Exit 2; stderr `invalid choice`; no data file | P1 | Auto (API) |
| TC-VAL-008 | R5 | VAL | Each valid priority low, med, high is accepted | No data file | 1. Run `add` three times with --priority low / med / high | low, med, high | Three exit 0; stored priorities in order | P2 | Auto (API) |
| TC-VAL-009 | R5, R1 | VAL | Impossible date 2026-02-30 is rejected, exit 1 | No data file | 1. Run `add X --due 2026-02-30` | due=2026-02-30 | Exit 1; stderr `not a real calendar date`; no file | P1 | Auto (API) |
| TC-VAL-010 | R5, R1 | VAL | Wrong date format 31/12/2026 is rejected, exit 1 | No data file | 1. Run `add X --due 31/12/2026` | due=31/12/2026 | Exit 1; stderr mentions `YYYY-MM-DD` | P1 | Auto (API) |
| TC-VAL-011 | R5, R1 | VAL | Empty --due value is rejected, exit 1 | No data file | 1. Run `add X --due ""` | due=(empty) | Exit 1; message about YYYY-MM-DD | P2 | Auto (API) |
| TC-VAL-012 | R5 | VAL | Leap day 2028-02-29 is accepted | No data file | 1. Run `add leap --due 2028-02-29` | due=2028-02-29 | Exit 0 | P2 | Auto (API) |
| TC-VAL-013 | R5, R1 | VAL | 2027-02-29 (not a leap year) is rejected | No data file | 1. Run `add leap --due 2027-02-29` | due=2027-02-29 | Exit 1; `not a real calendar date` | P2 | Auto (API) |
| TC-VAL-014 | R5, R1 | VAL | Non-zero-padded date 2026-1-5 is rejected | No data file | 1. Run `add X --due 2026-1-5` | due=2026-1-5 | Exit 1; `YYYY-MM-DD` | P2 | Auto (API) |
| TC-VAL-015 | R5 | VAL | Past due date is accepted (plan assumption, no overdue logic) | No data file | 1. Run `add old --due 1999-01-01` | due=1999-01-01 | Exit 0 | P3 | Auto (API) |
| TC-VAL-016 | R5, R6 | VAL | Three rejected adds leave an existing data file byte-identical | Data file with one task `keep` | 1. Save the file bytes<br>2. Run `add ""`, `add X --priority urgent`, `add X --due 2026-02-30`<br>3. Compare bytes | see steps | Exit codes 1, 2, 1; file bytes identical to step 1 | P0 | Auto (API) |
| TC-LIST-001 | R2 | LIST | List without options shows all tasks by id with a header | Seeded store: 1 A low todo due 12-05, 2 B high done due 12-01, 3 C med no due, 4 D high todo due 12-03 | 1. Run `list` | seed (4 tasks) | Header line then ids 1,2,3,4 | P1 | Auto (API) |
| TC-LIST-002 | R2 | LIST | --status done shows only done tasks | Seeded store | 1. Run `list --status done` | status=done | Only id 2 | P2 | Auto (API) |
| TC-LIST-003 | R2 | LIST | --status todo shows only todo tasks | Seeded store | 1. Run `list --status todo` | status=todo | Ids 1,3,4 | P2 | Auto (API) |
| TC-LIST-004 | R2 | LIST | --priority high filters by priority | Seeded store | 1. Run `list --priority high` | priority=high | Ids 2,4 | P2 | Auto (API) |
| TC-LIST-005 | R2 | LIST | Status and priority filters combine with AND | Seeded store | 1. Run `list --status todo --priority high` | todo + high | Only id 4 | P2 | Auto (API) |
| TC-LIST-006 | R2 | LIST | --sort due orders by date ascending, no-due task last | Seeded store | 1. Run `list --sort due` | sort=due | Ids 2,4,1,3 | P1 | Auto (API) |
| TC-LIST-007 | R2 | LIST | --sort due ties are broken by id; undated tasks keep id order | No data file | 1. Add n1 (no due), n2 and n3 (due 2026-12-01), n4 (no due)<br>2. Run `list --sort due` | 4 tasks | Ids 2,3,1,4 | P2 | Auto (API) |
| TC-LIST-008 | R2 | LIST | List on an empty store prints `No tasks.`, exit 0 | No data file | 1. Run `list` | none | Exit 0; stdout `No tasks.` | P1 | Auto (API) |
| TC-LIST-009 | R2 | LIST | Filter with no match prints `No tasks.`, exit 0 | One todo task | 1. Run `list --status done` | status=done | Exit 0; `No tasks.` | P2 | Auto (API) |
| TC-LIST-010 | R2 | LIST | Invalid --status value is rejected by argparse, exit 2 | None | 1. Run `list --status bogus` | status=bogus | Exit 2; `invalid choice` | P2 | Auto (API) |
| TC-LIST-011 | R2 | LIST | Unsupported --sort value name is rejected, exit 2 | None | 1. Run `list --sort name` | sort=name | Exit 2 | P3 | Auto (API) |
| TC-LIST-012 | R2, R6 | LIST | List is read-only: data file bytes unchanged | Seeded store | 1. Save bytes<br>2. Run `list` and `list --sort due`<br>3. Compare | seed | Bytes identical | P2 | Auto (API) |
| TC-DONE-001 | R3 | DONE | done marks the task done and persists it | One todo task id 1 | 1. Run `done 1`<br>2. Read file | id=1 | Exit 0; `Task 1 marked done.`; stored status done | P0 | Auto (API) |
| TC-DONE-002 | R3 | DONE | done on an already-done task is idempotent (message, exit 0, file unchanged) | Task 1 already done | 1. Run `done 1` again | id=1 | Exit 0; `already done`; bytes unchanged | P1 | Auto (API) |
| TC-DONE-003 | R3 | DONE | done with an unknown id fails, exit 1, file unchanged | One task id 1 | 1. Run `done 99` | id=99 | Exit 1; stderr `no task with id 99`; bytes unchanged | P0 | Auto (API) |
| TC-DONE-004 | R3 | DONE | done with non-integer id abc is a usage error, exit 2 | None | 1. Run `done abc` | id=abc | Exit 2 | P1 | Auto (API) |
| TC-DONE-005 | R3 | DONE | Ids 0 and -1 are reported as unknown ids, exit 1 | One task | 1. `done 0`<br>2. `done -1` | 0, -1 | Both exit 1 | P2 | Auto (API) |
| TC-DONE-006 | R3 | DONE | Huge id (23 digits) is a clean error, no traceback | One task | 1. Run `done 99999999999999999999999` | id=9*23 | Exit 1; no traceback | P3 | Auto (API) |
| TC-DEL-001 | R4 | DEL | delete removes the task and persists | Tasks 1 and 2 | 1. Run `delete 1`<br>2. Read file | id=1 | Exit 0; `Deleted task 1.`; file ids [2] | P0 | Auto (API) |
| TC-DEL-002 | R4 | DEL | delete with unknown id fails, exit 1, file unchanged | One task | 1. Run `delete 7` | id=7 | Exit 1; `no task with id 7`; bytes unchanged | P0 | Auto (API) |
| TC-DEL-003 | R4 | DEL | Deleting the same id twice: second call exits 1 | One task | 1. `delete 1`<br>2. `delete 1` | id=1 | Second exit 1 | P1 | Auto (API) |
| TC-DEL-004 | R4 | DEL | After deleting the last task, list prints `No tasks.` | One task | 1. `delete 1`<br>2. `list` | id=1 | `No tasks.`, exit 0 | P2 | Auto (API) |
| TC-DEL-005 | R4, R6 | DEL | next_id survives deleting every task (file keeps next_id 2) | One task | 1. `delete 1`<br>2. Read file | id=1 | File: tasks [], next_id 2 | P2 | Auto (API) |
| TC-STORE-001 | R6 | STORE | Missing file means empty list and list does not create the file | No data file | 1. Run `list` | none | Exit 0; `No tasks.`; file still absent | P1 | Auto (API) |
| TC-STORE-002 | R6 | STORE | add creates missing parent folders for the data file | Folder `a/b` absent | 1. Run `add x` with TASKBOX_FILE=<tmp>/a/b/t.json | path with 2 missing levels | Exit 0; file exists | P1 | Auto (API) |
| TC-STORE-003 | R6 | STORE | Zero-byte data file is treated as an empty store | Empty file | 1. Run `list` | 0-byte file | Exit 0; `No tasks.` | P2 | Auto (API) |
| TC-STORE-004 | R6 | STORE | Corrupt JSON: all four commands exit 1 with a clear error and the file is not overwritten | Data file containing `{bad` | 1. Run `list`, `add x`, `done 1`, `delete 1` in turn<br>2. After each, compare file bytes | content=`{bad` | Each: exit 1; stderr `not valid JSON`; no traceback; bytes unchanged | P0 | Auto (API) |
| TC-STORE-005 | R6 | STORE | Unknown format version 2 is rejected and file untouched | File with version 2 | 1. Run the four commands<br>2. Compare bytes | version=2 | Each: exit 1; `unsupported format or version`; bytes unchanged | P1 | Auto (API) |
| TC-STORE-006 | R6 | STORE | Wrong structure (tasks is not a list) is rejected and file untouched | File with tasks as object | 1. Run the four commands<br>2. Compare bytes | tasks={} | Each: exit 1; `malformed structure`; bytes unchanged | P1 | Auto (API) |
| TC-STORE-007 | R6 | STORE | UTF-16 data file (e.g. written by PowerShell `>`) gives a clean error, file untouched (last fix, commit 9a50011) | File saved as UTF-16 | 1. Run the four commands<br>2. Compare bytes | UTF-16 `[]` | Each: exit 1; `not valid UTF-8`; no traceback; bytes unchanged | P0 | Auto (API) |
| TC-STORE-008 | R6 | STORE | UTF-8 file with BOM (Notepad style) gives a clean error and file untouched | File saved as UTF-8 with BOM | 1. Run the four commands<br>2. Compare bytes | BOM + valid JSON | Each: exit 1; clean `error:` line, no traceback; bytes unchanged. Whether BOM should be tolerated: `[Needs input: product decision]` | P2 | Auto (API) |
| TC-STORE-009 | R6 | STORE | Deeply nested JSON (200000 `[`) gives a clean error, no traceback (last fix, commit ac9ee0a) | File of 200000 `[` | 1. Run the four commands<br>2. Compare bytes | `[` x 200000 | Each: exit 1; `not valid JSON`; no traceback; bytes unchanged | P1 | Auto (API) |
| TC-STORE-010 | R6 | STORE | Data file path that is a directory gives `error:` and exit 1 | Folder exists at the path | 1. Run `list` with TASKBOX_FILE=<folder> | path=folder | Exit 1; `error: cannot read ...`; no traceback | P2 | Auto (API) |
| TC-STORE-011 | R6 | STORE | --file wins over TASKBOX_FILE | Both set to different files | 1. Run `--file cli.json add x` with TASKBOX_FILE=env.json | two paths | cli.json created; env.json absent | P2 | Auto (API) |
| TC-STORE-012 | R6 | STORE | Default path is <home>/.taskbox/tasks.json (home redirected to a temp folder) | TASKBOX_FILE unset; USERPROFILE/HOME point to a temp folder | 1. Run `add x`<br>2. Look for <home>/.taskbox/tasks.json | temp home | Exit 0; file at <temp home>/.taskbox/tasks.json (the real home is never touched) | P2 | Auto (API) |
| TC-STORE-013 | R6 | STORE | Successful writes leave no `.taskbox-*.tmp` temp files | No data file | 1. add, add, done, delete<br>2. List the folder | 4 writes | Folder contains only tasks.json | P2 | Auto (API) |
| TC-STORE-014 | R6, R5 | STORE | A stored task that violates R5 (empty title) is rejected on load, file untouched | Valid JSON with one task whose title is empty | 1. Run the four commands<br>2. Compare bytes | title="" | Each: exit 1; `contains an invalid task`; bytes unchanged | P2 | Auto (API) |
| TC-STORE-015 | R6 | STORE | Two processes adding at the same time: no corruption (lost update tolerated by plan §8) | No data file | 1. Start 10 `add` processes at once against one file<br>2. Count tasks and check the file is valid JSON | 10 parallel adds | File stays valid JSON; every process exits 0 or prints a clean `error:`; count of tasks recorded (plan accepts lost updates) | P2 | Manual |
| TC-STORE-016 | R6 | STORE | Read-only data file: add fails with a clean error and the file is not changed | Data file with one task, set read-only | 1. `attrib +R` the file<br>2. Run `add x`<br>3. Compare bytes | read-only attribute | Exit 1 `error: cannot write ...`, no traceback, bytes unchanged | P2 | Manual |
| TC-ENC-001 | R1, R5 | ENC | Add a title with a character outside cp1252 (`☕`) on a cp1252 console: no traceback, exit 0 | Windows console, code page cp1252; PYTHONUTF8 unset | 1. Run `add "Buy coffee ☕"`<br>2. Check exit code and stderr | title=Buy coffee ☕ | Exit 0 and `Added task 1: ...` (characters may be replaced); no Python traceback; (source: plan §5 "unicode title kept intact", audit finding 1) | P1 | Auto (API) |
| TC-ENC-002 | R2, R6 | ENC | List a store that contains `☕` on a cp1252 console: no traceback, exit 0 | Data file with a task titled `Buy coffee ☕` (UTF-8); cp1252 console | 1. Run `list` | stored title with ☕ | Exit 0; table printed (characters may be replaced); no traceback | P1 | Auto (API) |
| TC-ENC-003 | R1, R2 | ENC | Workaround check: with PYTHONUTF8=1 the same add/list works | PYTHONUTF8=1 | 1. `add "Buy coffee ☕"`<br>2. `list` | title=Buy coffee ☕ | Both exit 0; list shows ☕ | P2 | Auto (API) |
| TC-ENC-004 | R1, R2 | ENC | Accented title that cp1252 can print works end to end | cp1252 console | 1. `add Café`<br>2. `list` | title=Café | Both exit 0; list shows `Café` | P2 | Auto (API) |
| TC-ENC-005 | R1 | ENC | Real interactive terminal (Windows Terminal / cmd with `chcp 65001`): ☕ title add and list | Interactive terminal controlled by the user | 1. Open the user's terminal<br>2. Run add and list with ☕ | title=Buy coffee ☕ | No traceback; characters render | P3 | Manual |
| TC-CLI-001 | R5 | CLI | No sub-command prints usage and exits 2 | None | 1. Run `python -m taskbox` | none | Exit 2; usage on stderr | P3 | Auto (API) |
| TC-CLI-002 | R1 | CLI | --version prints `taskbox 0.1.0` | None | 1. Run `--version` | none | Exit 0; `taskbox 0.1.0` | P3 | Auto (API) |

## 3. RTM (Requirement Traceability Matrix)
| Req/UC ID | Requirement | TC ID (Happy) | TC ID (Negative) | TC ID (Permission) | Coverage |
|---|---|---|---|---|---|
| R1 | add creates task, default med/todo, prints id | TC-ADD-001, TC-ADD-002, TC-ADD-003, TC-ADD-004, TC-ADD-005, TC-ADD-006, TC-ADD-008, TC-ENC-003, TC-ENC-004, TC-ENC-005, TC-CLI-002 | TC-ADD-007, TC-VAL-001, TC-VAL-002, TC-VAL-004, TC-VAL-007, TC-VAL-009, TC-VAL-010, TC-VAL-011, TC-VAL-013, TC-VAL-014, TC-ENC-001 | N/A (single-user local tool, no roles; plan §2 "no authorization") | Full (Permission N/A: no roles) |
| R2 | list with filters (AND) and --sort due | TC-LIST-001, TC-LIST-002, TC-LIST-003, TC-LIST-004, TC-LIST-005, TC-LIST-006, TC-LIST-007, TC-LIST-008, TC-LIST-009, TC-LIST-012, TC-ENC-003, TC-ENC-004 | TC-LIST-010, TC-LIST-011, TC-ENC-002 | N/A (single-user local tool, no roles; plan §2 "no authorization") | Full (Permission N/A: no roles) |
| R3 | done sets status; unknown id exit 1 | TC-DONE-001, TC-DONE-002 | TC-DONE-003, TC-DONE-004, TC-DONE-005, TC-DONE-006 | N/A (single-user local tool, no roles; plan §2 "no authorization") | Full (Permission N/A: no roles) |
| R4 | delete removes; unknown id exit 1 | TC-ADD-004, TC-DEL-001, TC-DEL-004, TC-DEL-005 | TC-DEL-002, TC-DEL-003 | N/A (single-user local tool, no roles; plan §2 "no authorization") | Full (Permission N/A: no roles) |
| R5 | validation: title, priority, due; exit codes; file unchanged | TC-ADD-008, TC-VAL-003, TC-VAL-005, TC-VAL-006, TC-VAL-008, TC-VAL-012, TC-VAL-015 | TC-VAL-001, TC-VAL-002, TC-VAL-004, TC-VAL-007, TC-VAL-009, TC-VAL-010, TC-VAL-011, TC-VAL-013, TC-VAL-014, TC-VAL-016, TC-STORE-014, TC-ENC-001, TC-CLI-001 | N/A (single-user local tool, no roles; plan §2 "no authorization") | Full (Permission N/A: no roles) |
| R6 | persistence: JSON file, atomic write, corrupt file not overwritten | TC-ADD-005, TC-LIST-012, TC-DEL-005, TC-STORE-001, TC-STORE-002, TC-STORE-003, TC-STORE-011, TC-STORE-012, TC-STORE-013, TC-STORE-015 | TC-VAL-016, TC-STORE-004, TC-STORE-005, TC-STORE-006, TC-STORE-007, TC-STORE-008, TC-STORE-009, TC-STORE-010, TC-STORE-014, TC-STORE-016, TC-ENC-002 | N/A (single-user local tool, no roles; plan §2 "no authorization") | Full (Permission N/A: no roles) |

Totals: requirements 6 | Full 6 | coverage 6/6 = 100% (computed from the table above; Permission column is N/A for every requirement, with the reason shown).
Orphan cases (no requirement): none.

## 4. Uncovered requirements / Contradictions / Notes
- No requirement is uncovered.
- Technique used: EP + BVA for R5 (title 0/1/200/201, priority, due formats and leap days), decision table for R2 filters, state transition for `todo -> done` (R3), error guessing for R6 and console encoding.
- Contradiction found while designing (code vs spec): spec says unicode titles are kept intact and commands print their result, but the code crashes on output for characters outside the console code page (TC-ENC-001/002). Recorded as audit finding 1; expected result follows the spec, so these cases are expected to expose a defect.
- TC-ADD-008, TC-STORE-008 and TC-ADD-007 have no spec oracle for exact behaviour/message: marked `[Needs input]` in Expected Result.
- Not covered on purpose: HTTP/API (none), browser/UI (none), accessibility (none). Non-functional cases (10k-task performance, data safety) are designed separately in `02b-nonfunctional.md`.

> **QA Advisor**
> - *Why these groups:* one module per requirement (ADD, LIST, DONE, DEL, VAL, STORE) plus ENC for the console-encoding finding and CLI for the entry point.
> - *Blind spots covered:* boundary data (0/1/200/201 chars, leap day, past date), Unicode, repeated commands (done twice, delete twice), two processes (TC-STORE-015). *Not covered:* permissions and sessions (N/A), network drop (N/A), a real interactive terminal (TC-ENC-005 stays Manual).
> - *Default I will choose if you do not reply:* run all `Auto (API)` cases now, run Manual cases that I can execute from a shell myself and mark TC-ENC-005 `Not Run`.

(Hard stop passed: approved by the user, see Status.)

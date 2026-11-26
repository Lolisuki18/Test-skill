# Execution Notes — taskbox 0.1.0 (CLI task tracker)
- **Phase:** 3/5 — Execution & Automation
- **Date:** 2026-11-26
- **Version:** v0.1
- **Status:** Draft (round 1 complete)
- **Requirement source:** `qa-artifacts/02-test-matrix.md` v0.1 (Approved), `qa-artifacts/02b-nonfunctional.md` v0.1 (Approved)
- **Approver:** n/a (no hard stop in Phase 3)

## 1. Run info
- Round: 1 | Date: 2026-11-26 | Build/commit: `ac9ee0a` (branch `fix/list-bad-path`; `taskbox/` and `tests/` unmodified) | Environment: Windows 11 10.0.26200, Python 3.14.6, stdout/stderr redirected to pipes (code page cp1252), a temp `TASKBOX_FILE` per case | Runner: QA agent (Auto cases through `qa-artifacts/tools/matrix_cases.py run`; Manual cases typed into a shell by the QA agent)
- Type counts: Manual 4 (3 run by the QA agent, 1 left `Not Run`), Auto (browser) 0 (no UI), Auto (API) 66. `qa-api-tester` and `qa-accessibility-auditor` not used (no HTTP API, no UI).

## 2. Results per test case
Summary: Total 70 | Pass 66 | Fail 3 | Blocked 0 | Not Run 1

| TC ID | Execution Type | Result | Run date | Defect ID | Evidence/Notes |
|---|---|---|---|---|---|
| TC-ADD-001 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-ADD-002 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-ADD-003 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-ADD-004 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-ADD-005 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-ADD-006 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-ADD-007 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-ADD-008 | Manual | Fail | 2026-11-26 | DEF-002 | Run by QA agent in a shell. `add $'line1\nline2'` -> `Added task 1: line1<LF>line2`, exit 0; `list` prints the second line outside the table. Expected (plan section 8 item 2, default accepted by the user): reject control characters. |
| TC-VAL-001 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-002 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-003 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-004 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-005 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-006 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-007 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-008 | Auto (API) | Pass | 2026-11-26 | — | all checks met (3 commands) |
| TC-VAL-009 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-010 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-011 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-012 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-013 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-014 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-015 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-VAL-016 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-LIST-001 | Auto (API) | Pass | 2026-11-26 | — | all checks met (8 commands) |
| TC-LIST-002 | Auto (API) | Pass | 2026-11-26 | — | all checks met (6 commands) |
| TC-LIST-003 | Auto (API) | Pass | 2026-11-26 | — | all checks met (6 commands) |
| TC-LIST-004 | Auto (API) | Pass | 2026-11-26 | — | all checks met (6 commands) |
| TC-LIST-005 | Auto (API) | Pass | 2026-11-26 | — | all checks met (6 commands) |
| TC-LIST-006 | Auto (API) | Pass | 2026-11-26 | — | all checks met (6 commands) |
| TC-LIST-007 | Auto (API) | Pass | 2026-11-26 | — | all checks met (5 commands) |
| TC-LIST-008 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-LIST-009 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-LIST-010 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-LIST-011 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-LIST-012 | Auto (API) | Pass | 2026-11-26 | — | all checks met (7 commands) |
| TC-DONE-001 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-DONE-002 | Auto (API) | Pass | 2026-11-26 | — | all checks met (3 commands) |
| TC-DONE-003 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-DONE-004 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-DONE-005 | Auto (API) | Pass | 2026-11-26 | — | all checks met (3 commands) |
| TC-DONE-006 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-DEL-001 | Auto (API) | Pass | 2026-11-26 | — | all checks met (3 commands) |
| TC-DEL-002 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-DEL-003 | Auto (API) | Pass | 2026-11-26 | — | all checks met (3 commands) |
| TC-DEL-004 | Auto (API) | Pass | 2026-11-26 | — | all checks met (3 commands) |
| TC-DEL-005 | Auto (API) | Pass | 2026-11-26 | — | all checks met (3 commands) |
| TC-STORE-001 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-STORE-002 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-STORE-003 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-STORE-004 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-005 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-006 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-007 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-008 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-009 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-010 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-STORE-011 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-STORE-012 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-STORE-013 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-014 | Auto (API) | Pass | 2026-11-26 | — | all checks met (4 commands) |
| TC-STORE-015 | Manual | Pass | 2026-11-26 | — | Run by QA agent: 10 parallel `add` processes. Exit codes: nine 0, one 1 (`error: cannot write ... [WinError 5] Access is denied`, clean message). File stayed valid JSON, ids 1-6 unique, next_id 7. Only 6 titles stored although 9 processes printed success, so 3 updates were silently lost: known limitation accepted in plan section 8, listed under residual risks. |
| TC-STORE-016 | Manual | Pass | 2026-11-26 | — | Run by QA agent: `attrib +R` on the data file, `add x` -> `error: cannot write ... [WinError 5] Access is denied: '.taskbox-...tmp' -> 'm16.json'`, exit 1, bytes identical (`cmp`), no `.taskbox-*.tmp` left. |
| TC-ENC-001 | Auto (API) | Fail | 2026-11-26 | DEF-001 | exit 1; traceback printed: UnicodeEncodeError: 'charmap' codec can't encode character '\u2615' in position 25: charac |
| TC-ENC-002 | Auto (API) | Fail | 2026-11-26 | DEF-001 | exit 1; traceback printed: UnicodeEncodeError: 'charmap' codec can't encode character '\u2615' in position 40: charac |
| TC-ENC-003 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-ENC-004 | Auto (API) | Pass | 2026-11-26 | — | all checks met (2 commands) |
| TC-ENC-005 | Manual | Not Run | 2026-11-26 | — | Needs the user's own interactive terminal (Windows Terminal / cmd with `chcp 65001`); not run by the QA agent. [Needs input: user to run and report] |
| TC-CLI-001 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |
| TC-CLI-002 | Auto (API) | Pass | 2026-11-26 | — | all checks met (1 commands) |

## 3. Automation
- Test files: existing `tests/test_*.py` (unchanged) and the QA script `qa-artifacts/tools/matrix_cases.py` (machine-readable output `qa-artifacts/tools/results.json`).
- Commands: `python -W error -m unittest discover -s tests -t .` and `python qa-artifacts/tools/matrix_cases.py run`.
- Raw output, repo unit suite:
```text
............................................................
----------------------------------------------------------------------
Ran 60 tests in 0.315s

OK
```
- Raw output, QA matrix run (stdout of the script; the script cuts the evidence column at 150 characters):
```text
TC-ADD-001 Pass | all checks met (1 commands)
TC-ADD-002 Pass | all checks met (1 commands)
TC-ADD-003 Pass | all checks met (2 commands)
TC-ADD-004 Pass | all checks met (4 commands)
TC-ADD-005 Pass | all checks met (1 commands)
TC-ADD-006 Pass | all checks met (1 commands)
TC-ADD-007 Pass | all checks met (1 commands)
TC-ADD-008 Not Run | Manual case, not executed by the script
TC-VAL-001 Pass | all checks met (1 commands)
TC-VAL-002 Pass | all checks met (1 commands)
TC-VAL-003 Pass | all checks met (1 commands)
TC-VAL-004 Pass | all checks met (1 commands)
TC-VAL-005 Pass | all checks met (1 commands)
TC-VAL-006 Pass | all checks met (1 commands)
TC-VAL-007 Pass | all checks met (1 commands)
TC-VAL-008 Pass | all checks met (3 commands)
TC-VAL-009 Pass | all checks met (1 commands)
TC-VAL-010 Pass | all checks met (1 commands)
TC-VAL-011 Pass | all checks met (1 commands)
TC-VAL-012 Pass | all checks met (1 commands)
TC-VAL-013 Pass | all checks met (1 commands)
TC-VAL-014 Pass | all checks met (1 commands)
TC-VAL-015 Pass | all checks met (1 commands)
TC-VAL-016 Pass | all checks met (4 commands)
TC-LIST-001 Pass | all checks met (8 commands)
TC-LIST-002 Pass | all checks met (6 commands)
TC-LIST-003 Pass | all checks met (6 commands)
TC-LIST-004 Pass | all checks met (6 commands)
TC-LIST-005 Pass | all checks met (6 commands)
TC-LIST-006 Pass | all checks met (6 commands)
TC-LIST-007 Pass | all checks met (5 commands)
TC-LIST-008 Pass | all checks met (1 commands)
TC-LIST-009 Pass | all checks met (2 commands)
TC-LIST-010 Pass | all checks met (1 commands)
TC-LIST-011 Pass | all checks met (1 commands)
TC-LIST-012 Pass | all checks met (7 commands)
TC-DONE-001 Pass | all checks met (2 commands)
TC-DONE-002 Pass | all checks met (3 commands)
TC-DONE-003 Pass | all checks met (2 commands)
TC-DONE-004 Pass | all checks met (1 commands)
TC-DONE-005 Pass | all checks met (3 commands)
TC-DONE-006 Pass | all checks met (2 commands)
TC-DEL-001 Pass | all checks met (3 commands)
TC-DEL-002 Pass | all checks met (2 commands)
TC-DEL-003 Pass | all checks met (3 commands)
TC-DEL-004 Pass | all checks met (3 commands)
TC-DEL-005 Pass | all checks met (3 commands)
TC-STORE-001 Pass | all checks met (1 commands)
TC-STORE-002 Pass | all checks met (1 commands)
TC-STORE-003 Pass | all checks met (1 commands)
TC-STORE-004 Pass | all checks met (4 commands)
TC-STORE-005 Pass | all checks met (4 commands)
TC-STORE-006 Pass | all checks met (4 commands)
TC-STORE-007 Pass | all checks met (4 commands)
TC-STORE-008 Pass | all checks met (4 commands)
TC-STORE-009 Pass | all checks met (4 commands)
TC-STORE-010 Pass | all checks met (1 commands)
TC-STORE-011 Pass | all checks met (1 commands)
TC-STORE-012 Pass | all checks met (1 commands)
TC-STORE-013 Pass | all checks met (4 commands)
TC-STORE-014 Pass | all checks met (4 commands)
TC-STORE-015 Not Run | Manual case, not executed by the script
TC-STORE-016 Not Run | Manual case, not executed by the script
TC-ENC-001 Fail | exit 1; traceback printed: UnicodeEncodeError: 'charmap' codec can't encode character '\u2615' in position 25: charac
TC-ENC-002 Fail | exit 1; traceback printed: UnicodeEncodeError: 'charmap' codec can't encode character '\u2615' in position 40: charac
TC-ENC-003 Pass | all checks met (2 commands)
TC-ENC-004 Pass | all checks met (2 commands)
TC-ENC-005 Not Run | Manual case, not executed by the script
TC-CLI-001 Pass | all checks met (1 commands)
TC-CLI-002 Pass | all checks met (1 commands)
```

## 3b. Non-functional track (cases from `02b-nonfunctional.md`)
Tool: Python 3.14.6 standard library (`subprocess`, `time.perf_counter`), script `qa-artifacts/tools/nf_run.py`; environment: local temp folder. Thresholds: 1.0 s is the user-accepted suggestion (no SLA).

Raw output:
```text
baseline: list on empty store, median of 5 = 0.172 s
n=1000   size=  95.3 KB  list                           median 0.152 s  max 0.165 s  exit codes [0]
n=1000   size=  95.3 KB  add                            median 0.169 s  max 0.351 s  exit codes [0]
n=1000   size=  95.3 KB  list --sort due --status todo  median 0.145 s  max 0.157 s  exit codes [0]
n=10000  size= 971.8 KB  list                           median 0.182 s  max 0.195 s  exit codes [0]
n=10000  size= 971.8 KB  add                            median 0.255 s  max 0.262 s  exit codes [0]
n=10000  size= 971.8 KB  list --sort due --status todo  median 0.180 s  max 0.191 s  exit codes [0]
n=10000 done(last id) 0.196 s exit [0] ; delete(first id) 0.275 s exit [0]
n=50000  size=4945.8 KB  list                           median 0.408 s  max 0.418 s  exit codes [0]
n=50000  size=4945.8 KB  add                            median 0.705 s  max 0.746 s  exit codes [0]
n=50000  size=4945.8 KB  list --sort due --status todo  median 0.426 s  max 0.481 s  exit codes [0]
NF-SEC-01: 40 kill iterations on a 5000-task store; invalid/inconsistent files: 0; stray .taskbox-*.tmp left: 4; final tasks 5004
NF-SEC-04: real ~/.taskbox/tasks.json before=(False, None) after=(False, None) -> unchanged
```

| NF ID | Result | Evidence/Notes |
|---|---|---|
| NF-PERF-01 | Pass | `list` at 10,000 tasks: median 0.182 s, max 0.195 s (< 1.0 s). Empty-store baseline 0.172 s (interpreter start-up dominates). |
| NF-PERF-02 | Pass | `add` at 10,000 tasks: median 0.255 s (< 1.0 s). |
| NF-PERF-03 | Pass | `done` last id 0.196 s, `delete` first id 0.275 s. Deviation: one run each, not median of 5, because both change the store. |
| NF-PERF-04 | No status | Report only (no threshold, `[Needs input: target]`): `list` 0.152 s / 0.182 s / 0.408 s and `add` 0.169 s / 0.255 s / 0.705 s at 1,000 / 10,000 / 50,000 tasks; time grows roughly with file size (4.9 MB at 50,000). |
| NF-PERF-05 | Pass | `list --sort due --status todo` at 10,000: median 0.180 s. |
| NF-SEC-01 | Pass | 40 kill iterations on a 5,000-task store: 0 invalid or inconsistent files. 4 stray `.taskbox-*.tmp` files were left behind by killed processes (reported, not a failure by the case definition). |
| NF-SEC-02 | Pass | Same evidence as TC-STORE-016 (read-only file: exit 1, `error: cannot write`, bytes unchanged, no temp left). |
| NF-SEC-03 | Pass | The only tracebacks in the whole run are the two cases of DEF-001 (TC-ENC-001/002), counted there. All other failing-path cases show `error:` lines and no `Traceback`. |
| NF-SEC-04 | Pass | `~/.taskbox/tasks.json` did not exist before or after the NF run; TC-STORE-012 used a redirected temp home. |
| NF-COMP-01 | Not Run | Only Python 3.14.6 is usable here; other Python versions and other OSes are not available. [Needs input: supported versions] |
| NF-USA-01 | Pass | Read by the QA agent: corrupt JSON, wrong version, UTF-16 and directory messages each name the file path and a cause. Note: for a directory the cause shown is `Permission denied` (Windows wording), which is misleading but does name the path. |

## 4. Findings from exploratory testing
- A title starting with `-` (`add "-dash"`) fails with argparse `the following arguments are required: title` (exit 2); `add -- -dash` works. Not logged as a defect: standard argparse behaviour and TC-ADD-007 expects exactly this; the wording may confuse users.
- `done " 2"` and `done +2` are accepted (Python `int()` leniency). Not logged: spec silent, harmless.
- Concurrency: 3 of 9 reported-successful parallel adds were lost silently (TC-STORE-015). Known limitation, plan section 8.

## 5. Blockers and causes
- TC-ENC-005: needs the user's interactive terminal. Not Run.
- NF-COMP-01: no other Python versions installed.
- Process note: the first full run of the automated cases happened before the `02-test-matrix.md` status line was changed to Approved (the user had already said "approved"); the whole set was re-run afterwards and only the second run is recorded here.

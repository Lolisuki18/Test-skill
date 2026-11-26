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

## Stage 3 - QA (round 2) - 2026-11-26 - status: Done, verdict Conditional Go
Artifacts: qa-artifacts/03-execution-notes.md (R2 section, v0.2), 04-defects.md (re-test history, v0.2), 04b-regression-plan.md (round 2 section), 05-summary-report.md (Round 2 appended, v0.2), qa-artifacts/tools/results.json (round 2) and results-round1.json (kept), tools/matrix_cases.py (harness fix).
QA Phases 1-2 (plan, matrix) not repeated: approved in round 1, no requirement changed (R1..R6 unchanged). Phase 3-5 re-run as "Re-test round 2".
Real results (build 81d0868, Windows, Python 3.14.6, cp1252 pipes):
- `python qa-artifacts/tools/matrix_cases.py run` -> 70 results: Pass 66, Not Run 4 (the 4 are Manual cases).
- TC-ENC-001/002 Pass (were Fail), TC-ADD-008 Pass by hand (was Fail): `error: title must not contain control characters`, exit 1.
- Totals: 70 | Pass 69 (67 run on 81d0868 + 2 Manual carried over from ac9ee0a: TC-STORE-015/016) | Fail 0 | Blocked 0 | Not Run 1.
- Unit suite: `Ran 66 tests in 1.093s OK`.
Verdict: Conditional Go (Executed Rate 69/70 = 98.6% < 100% because TC-ENC-005 is Not Run).
Open items: TC-ENC-005 NOT RUN (needs the user's real interactive terminal; failing it would make the verdict No-Go); DEF-001 and DEF-002 are in status Re-test, not Closed (QA never closes defects itself); NF-* cases not re-run; NF-COMP-01 Not Run; U+2028 title accepted; harness edit (matrix_cases.py) was needed and is committed with the QA artifacts; the scripted pass ran before the regression plan was confirmed.

## Stage 4 - Docs - 2026-11-26 - status: Done (branch A, Phase 4 checklist; docs-sync-auditor not run as a separate audit)
Artifacts: README.md (title rule, replace-on-print note, exit code 1 row, 66 tests, line ref), docs/diagrams/sequence-add-task.md (+_make_output_safe step, new line refs), docs/_evidence.md (new facts, 66 tests). Not touched: ADRs (no new decision recorded; deciders/alternatives unknown), docs/api, docs/runbook.md.
Real results (Docs Phase 4 anti-drift): every README command re-run in a temp data file: `--version` -> `taskbox 0.1.0`; add/list --sort due/done (twice)/delete/list -> outputs as documented; `PYTHONUTF8=1 add "Coffee <emoji>"` + list shows the emoji; `python -m unittest discover -s tests -t .` -> `Ran 66 tests in 0.834s OK`. `file:line` refs re-read against the source (cli.py:105-110, 113-121; models.py:60-70, 86).
Open items: `[Cần bổ sung: minimum Python version]` and `[Cần bổ sung: license]` remain in README; sequence diagram not rendered (no Mermaid renderer); `docs-sync-auditor` not run; real interactive terminal behaviour is documented as "not checked".

## Stage 5 - Release - 2026-11-26 - status: Done as preparation only (no tag, no deploy, no push); release verdict: Conditional Go, not released
Artifacts: CHANGELOG.md (Unreleased: +Changed, +Fixed entry citing 81d0868), docs/release-notes.md (draft). `runbook-writer` and `ci-cd-setup` not used: local CLI, no Dockerfile/CI/infra in the repo (docs/runbook.md absent).
Real results: range `fix/list-bad-path..HEAD` = 4 commits read (81d0868 fix; 3b20b50, e4590e0, b942a83 docs/qa/notes: omitted from the changelog on purpose). Last test run: `Ran 66 tests in 0.834s OK`.
Open items: version and date `[Needs input]` (`__version__` = 0.1.0, no tag); PR base branch `[Needs input]`; TC-ENC-005 Not Run (user's interactive terminal; failing it = No-Go); NF-COMP-01 Not Run; minimum Python version and license `[Cần bổ sung]`; lost-update risk accepted in plan; U+2028 title accepted; PR not opened and nothing pushed (user's decision).
Release verdict (QA recommendation, decision belongs to the user): Conditional Go. Condition left: user runs TC-ENC-005 and reports.


## Decisions
| Date | Decision | By |
|---|---|---|
| 2026-11-26 | Continue from existing plan/qa-artifacts/docs; all four sets installed | user |
| 2026-11-26 | Fix = errors="replace" on stdout/stderr + reject control chars in titles | user (ok at bug-investigator hard stop) |
| 2026-11-26 | Keep DEF-001 and DEF-002 in one commit; accept the Notes-level risks | user |
| 2026-11-26 | Close DEF-001 and DEF-002 after round-2 Pass; accept Conditional Go with TC-ENC-005 Not Run | user |

# Test Plan — taskbox 0.1.0 (CLI task tracker)
- **Phase:** 1/5 — Test Plan
- **Date:** 2026-11-26
- **Version:** v0.2
- **Status:** Approved (approved on: 2026-11-26, user said "approved"; changes: data-loss risk raised to P0, defaults for open questions 1-4 accepted)
- **Requirement source:** `plan/001-taskbox.md` §1 (R1–R6), §5 edge cases; `README.md`; code in `taskbox/` (read for cross-checking only)
- **Approver:** project owner (user)

## 1. Requirement Audit
IDs are the plan's own (R1–R6). Blockers first.

| # | Requirement (ID) | Issue | Type | Clarifying question | Suggested default |
|---|---|---|---|---|---|
| 1 | R1/R2 (output) | Spec says "prints its id" / "prints tasks" but never says what happens when stdout cannot encode the title. Code saves the task, then `print()` raises `UnicodeEncodeError` on a cp1252 console (traceback, exit 1) and `list` then crashes on every later call. [Inferred from code — needs confirmation] Why it bites: a command that changes state and then fails looks like "nothing happened", so the user retries. | Missing error flow (BLOCKER) | Must `add`/`list` work on non-UTF-8 consoles (default Windows)? | Yes: never a traceback; replace unencodable characters or reconfigure stdout. |
| 2 | R5 (title) | "non-empty after trim (max 200 chars)": is 200 counted before or after trim? Are newline / control characters allowed? Code trims first and accepts embedded newlines, which break the `list` table. | Ambiguity | Count after trim? Allow `\n`/`\t`? | Count after trim; reject control characters. |
| 3 | R1 (CLI parsing) | A title that starts with `-` (e.g. `add "-urgent"`) is rejected by argparse as "title is required" (exit 2). Not mentioned in spec. | Missing error flow | Should such titles be addable? | Accept via `--`, and document it. |
| 4 | R5 (exit codes) | "exit code 2 (argparse) or 1 (domain)" does not say which violation gets which. Observed: bad priority → 2, bad due → 1, empty title → 1. | Ambiguity | Is the per-violation code fixed? | Treat the current split as intended; matrix expects it. |
| 5 | R2 (output format) | Column layout, header and default order of `list` unspecified. Code: header line, fixed-width columns, id order. | Ambiguity | Is header/columns a contract? | Header + id order are; tests assert on ids, not spacing. |
| 6 | R3/R4 (ids) | `done abc` → 2; `done -1`, `done 0`, `done 99999999999999999999` → 1 "no task"; `done " 2"` and `+2` are accepted by `int()`. Spec only lists unknown and non-integer. | Ambiguity | Reject ids < 1 at parse time? | Keep as is (exit 1), low priority. |
| 7 | R6 (concurrency) | No locking: two processes can lose an update (accepted in plan §8). No spec for `os.replace` failing on Windows when the file is held. | Missing error flow | Is "last write wins" acceptable? | Yes (documented); test once to know real behaviour. |
| 8 | R6 (path) | `--file` pointing at a directory gives `Permission denied` text on Windows; read-only file / folder behaviour unspecified. | Missing error flow | Expected message? | Any `error: cannot read/write ...`, exit 1, never a traceback. |
| 9 | R6 (data safety) | Default path is the real `~/.taskbox/tasks.json`. A run without `TASKBOX_FILE`/`--file` would touch the user's real data. | Data | — | All runs use `TASKBOX_FILE` in a temp folder. |
| 10 | Non-functional | No performance target for large stores (every command rewrites the whole file). | Non-functional | Target for 10k tasks? | `[Needs input: target]`; suggestion only: list/add under 1 s at 10k tasks. |
| 11 | Docs vs code | Plan §9 says "56 tests"; suite now has 60 after two fixes (UTF-16/BOM, deep nesting). Branch is `fix/list-bad-path` but its commits concern storage decoding, not `list` paths. | Contradiction (documentation) | Which is current? | Code + commits are truth; 60 tests. |
| 12 | Permissions / Abuse / Observability / Missing states | Single-user local tool: no roles, no rate limit, no audit log. Lifecycle is only `todo -> done`, no reopen (edit command out of scope). | N/A | — | Recorded as N/A with reason (RTM). |

All 10 audit groups walked: Ambiguity (2,4,5,6), Missing error flows (1,3,7,8), Permissions (N/A, #12), Contradictions (11), Missing states (12), Data (2,9), Non-functional (10), Dependencies (none: stdlib only), Abuse protection (N/A), Observability (N/A).

## 2. Scope
- **In-scope:** R1 add, R2 list (filter/sort), R3 done, R4 delete, R5 validation + exit codes, R6 persistence (JSON, atomic write, corrupt/missing/UTF-8 handling); console output encoding on Windows; data safety and performance (10k tasks) as non-functional.
- **Out-of-scope:** edit command, tags, recurring tasks, multi-user, colours (plan "Out of scope"); developer unit tests (the 60 unittest tests are run as evidence, not redesigned); browser UI, HTTP API, accessibility audit (a CLI has none, so `qa-api-tester` and `qa-accessibility-auditor` do not apply).

## 3. Risk Analysis
| Risk | Likelihood | Impact | Test priority | Mitigation |
|---|---|---|---|---|
| Data loss / overwrite of the data file (R6) | M | H | P0 (raised by user at approval; derivation rule alone gives P1) | corrupt/UTF-16/BOM/wrong-version cases assert file bytes unchanged |
| Non-ASCII titles on Windows console (finding 1) | H | M | P1 | explicit cases with `☕`, accents; run with and without `PYTHONUTF8` |
| Validation gaps let bad data into the file (R5) | M | M | P2 | EP + BVA on title/priority/due |
| Wrong filter/sort result (R2) | M | M | P2 | decision table status x priority x sort |
| Lost update with two processes | L | M | P2 | one exploratory case, recorded as known limitation |
| Slow with large store | L | L | P3 | NF case at 10k tasks |

## 4. Test Strategy
| Area/Module | Manual | Auto (browser) | Auto (API) | Reason |
|---|---|---|---|---|
| add / R1 | exploratory (odd titles) | N/A (no UI) | main cases* | repeatable, deterministic |
| list / R2 | one visual check of the table | N/A | main cases* | assert ids, not spacing |
| done, delete / R3, R4 | — | N/A | all* | trivial, deterministic |
| validation / R5 | — | N/A | all* | many data combinations |
| persistence / R6 | file-system tricks (directory as file, locked file) | N/A | corrupt/missing/version* | needs temp files |
| console encoding | real terminal run | N/A | — | depends on host code page |

\* **Mapping note:** the strategy vocabulary has no value for "automated command-line run". `Auto (API)` is used as the nearest slot and means: call `taskbox.cli.main()` or run `python -m taskbox ...` against a temp `TASKBOX_FILE`, using the repo's existing `unittest` tooling. `Auto (browser)` is N/A everywhere. [Proposed — user to confirm]

## 5. Test Environment & Data
- Environment: local Windows 11 (10.0.26200), Python 3.14.6, taskbox 0.1.0, git commit `ac9ee0a` on branch `fix/list-bad-path`; console code page cp1252 (observed). No network, accounts or roles.
- Data: every run sets `TASKBOX_FILE` to a temp folder; fixture files created by the cases (corrupt, UTF-16, BOM, v2, 10k tasks). Never the real `~/.taskbox/`.
- Tooling in repo: `python -W error -m unittest discover -s tests -t .` (60 tests). No Playwright, no API tooling.

## 6. Entry / Exit Criteria
- Entry: suite green on the build; build identified by commit; temp data folder available.
- Exit (Proposed — user to confirm): 100% of P0 pass; no open Blocker/Critical; RTM covers 100% of in-scope requirements; every Fail has a logged defect.

## 7. Schedule & assignment
[Needs input: none required — single tester]

## 8. Open questions / Assumptions
1. Finding 1 (unicode on cp1252 console): treat as an in-scope defect candidate. Default: yes.
2. Title limit counted after trim; control characters rejected? Default: after trim; expected result written with `[Needs input: exact error message]`.
3. Mapping of "Auto (API)" to CLI runs. Default: yes (see §4).
4. Are exact error message strings part of the contract? Default: no, assert exit code + substring.

> **QA Advisor**
> - *Why it matters:* a CLI that writes and then crashes on output is a classic "state changed but the user thinks it failed" bug.
> - *Blind spots to watch:* boundary data (empty, 200/201 chars, Unicode, leading dash), repeated runs (idempotent `done`, ids after delete), two processes at once. Permissions, session expiry and network drop are N/A.
> - *Default I will choose if you do not reply:* the answers above, `qa-artifacts/` kept in the repo, every test through a temp `TASKBOX_FILE`.

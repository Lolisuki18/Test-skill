# Test Summary Report — taskbox 0.1.0 (CLI task tracker)
- **Phase:** 5/5 — Summary Report
- **Date:** 2026-11-26
- **Version:** v0.1
- **Status:** Draft
- **Requirement source:** `qa-artifacts/02-test-matrix.md`, `03-execution-notes.md` (round 1), `04-defects.md`, `04b-regression-plan.md`, `02b-nonfunctional.md`
- **Build/commit:** `ac9ee0a` on branch `fix/list-bad-path` | **Environment:** Windows 11 10.0.26200, Python 3.14.6, console code page cp1252 (pipes), temp data files
- **Approver:** [Needs input: PO / release owner]

## 1. Executive Verdict: Conditional Go
**Applied thresholds:** the plan's exit criteria (`01-test-plan.md` section 6, proposed, approved with the plan) plus the default thresholds of `release-gate-criteria.md` (default, not otherwise adjusted; no context relaxation applied).

| Criterion | Go | Conditional | No-Go | Actual | Met? |
|---|---|---|---|---|---|
| P0 Pass Rate | 100% | 100% | < 100% | 8/8 = 100% | Go |
| P1 Pass Rate | ≥ 95% | ≥ 90% | < 90% | 21/23 = 91.3% | Conditional |
| Overall Pass Rate | ≥ 95% | ≥ 90% | < 90% | 66/70 = 94.3% | Conditional |
| Executed Rate (Pass+Fail)/Total | 100% | ≥ 95% | < 95% | 69/70 = 98.6% | Conditional |
| Blocked cases | 0 | ≤ 5%, none P0 | > 5% or P0 | 0 | Go |
| Open Blocker / Critical | 0 / 0 | 0 / 0 | ≥ 1 | 0 / 0 | Go |
| Open Major | 0 | ≤ 3 with workaround and fix plan | > 3 or no workaround | 1 (DEF-001, workaround `PYTHONUTF8=1`, fix plan `[Needs input]`) | Conditional |
| RTM coverage (requirements with cases) | 100% | ≥ 95% | < 95% | 6/6 = 100% | Go |
| Fixed but not re-tested | 0 | Minor/Trivial only | at Major+ | 0 | Go |
| Permissions/security cases | all run and pass | same | any failing/unrun | no permission cases exist (N/A, single-user tool); NF-SEC-01..04 Pass | Go (N/A) |

No No-Go cell is true; four Go cells are not met, so the verdict is **Conditional Go**.

**Conditions** (each is verifiable; if unmet the verdict becomes No-Go):
1. DEF-001 fixed and re-tested: TC-ENC-001/002 Pass on a Windows cp1252 console, plus regression of TC-ADD-001, TC-LIST-001, TC-STORE-004 on the next build. Owner `[Needs input]`, due `[Needs input]`.
2. DEF-002 fixed, or the PO records that line breaks in titles are allowed (then close it as Won't Fix with the decision maker named). Owner `[Needs input]`, due `[Needs input]`.
3. TC-ENC-005 run by the user in a real interactive terminal and reported. Owner: user, due `[Needs input]`.

This is QA's recommendation; the release decision belongs to the user/PO.

## 2. Execution Summary
Source: `03-execution-notes.md` section 2 (70 rows). Pass Rate = Passed / Total; Not Run and Blocked are not counted as Pass.

| Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|
| 70 | 66 | 3 | 0 | 1 | 94.3% (95.7% of the 69 executed) |

By priority:
| Priority | Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|---|
| P0 | 8 | 8 | 0 | 0 | 0 | 100% |
| P1 | 23 | 21 | 2 | 0 | 0 | 91.3% |
| P2 | 31 | 31 | 0 | 0 | 0 | 100% |
| P3 | 8 | 6 | 1 | 0 | 1 | 75.0% |

Other tracks: repo unit suite 60/60 OK (0.315 s, `python -W error -m unittest discover -s tests -t .`). Non-functional (`03-execution-notes.md` section 3b): 9 Pass, 1 Not Run (NF-COMP-01), 1 report-only (NF-PERF-04); not included in the table above.

Failed cases: TC-ENC-001, TC-ENC-002 (DEF-001); TC-ADD-008 (DEF-002). Not Run: TC-ENC-005.

## 3. Defect Statistics
| Severity \ Status | New | Open | Fixed | Re-test | Closed | Reopened | Won't Fix |
|---|---|---|---|---|---|---|---|
| Blocker | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Critical | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Major | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Minor | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| Trivial | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Open defects with Severity >= Major: DEF-001 (Major, proposed P1). Both defects are still `New`: QA has not yet confirmed them with the developer, and `New` counts as open.

## 4. Requirement Coverage (RTM)
Total in-scope requirements: 6 | Fully covered (cases for happy and negative): 6 | With a Failed case: 4 (R1, R2, R5, R6) | With a Not Run case: 1 (R1) | Without cases: 0 | Requirements whose cases all Pass: R3 (6/6), R4 (6/6).
Per requirement (cases tagged to it, may overlap): R1 22 (19 Pass, 2 Fail, 1 Not Run); R2 15 (14 Pass, 1 Fail); R3 6 (6 Pass); R4 6 (6 Pass); R5 20 (18 Pass, 2 Fail); R6 21 (20 Pass, 1 Fail).
Risky requirements: R1/R2 (console output of non-cp1252 titles, DEF-001).

## 5. Residual risks
- DEF-001 and DEF-002 open; DEF-001 affects any Windows user with emoji or non-Latin titles.
- Lost updates under concurrent runs: 3 of 9 successful parallel adds vanished silently with exit 0 (TC-STORE-015). Accepted in plan section 8, but the tool gives no warning.
- Killed processes leave `.taskbox-*.tmp` files (4 after 40 kills); harmless but unreported.
- Real interactive terminal never exercised (TC-ENC-005); only piped output was tested.
- Only one Python version and one OS tested (NF-COMP-01 Not Run).
- Plan section 9 still says "56 unit tests" while the suite has 60: documentation drift, not a product defect.
- Light coverage: other exceptions from `json.loads`, extremely large id/number values in stored JSON, file locked by another program (only simulated with read-only).

## 6. Next actions
| Action | Owner | Due |
|---|---|---|
| Fix DEF-001 and DEF-002 (or decide DEF-002 is not a defect), report the build | `[Needs input]` | `[Needs input]` |
| Re-test DEF-001/002 with the regression list in `04-defects.md` mode 2 (not yet created: no fix reported) | QA | after fix |
| Run TC-ENC-005 in a real terminal | user | `[Needs input]` |
| Decide whether lost updates need a lock or a warning | PO | `[Needs input]` |
| Update plan 001 test count (56 -> 60) | developer | `[Needs input]` |

## 7. Missing data
| Item | Status |
|---|---|
| Result of TC-ENC-005 (interactive terminal) | no data yet |
| Owner and due dates for conditions | no data yet |
| Agreed performance SLA | none; 1.0 s suggestion accepted by the user was used |
| Supported Python versions / OSes | no data yet |
| Exact wall-clock time of the full scripted run | not measured |

> **QA Advisor**
> - *Why thresholds, not gut feeling:* with 94.3% overall and 91.3% on P1 the numbers sit between Go and No-Go, so only the written gate gives a repeatable answer.
> - *Not Run is a risk:* the only unexecuted case is the one that looks at a real console, which is exactly where DEF-001 lives.
> - *Blind spots still open:* permissions and sessions are N/A; network drop is N/A; double-click maps to two processes at once (lost updates); boundary data is covered.
> - *Default I recommend:* Conditional Go with conditions 1-3. Choose "postpone one round" if you prefer to be safe.

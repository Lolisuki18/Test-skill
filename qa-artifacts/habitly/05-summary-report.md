# Test Summary Report — habitly 1.0.0
- **Phase:** 5/5 — Summary Report
- **Date:** 2026-11-27
- **Version:** v0.2 (Round 2 appended; Round 1 kept unchanged above)
- **Status:** Round 1: Approved (approved on: 2026-11-27, user said "ok, finalize"; no defects in Re-test to close; ratings kept). Round 2: Approved (2026-11-27, user said "approved" at the Stage 3 stop and closed DEF-001..DEF-004)
- **Requirement source:** `qa-artifacts/habitly/02-test-matrix.md` (v0.3), `03-execution-notes.md` (round 1), `03c-accessibility.md`, `04-defects.md`
- **Approver:** project owner (user)
- Build/commit: 8ec8923 (`feat/habitly`). Environment: Windows 11, Node v22.23.2, Chromium 159.0.8154.6 (Playwright) and built-in pane Chrome/156.0.8078.100, static server on localhost:8765.
- Applied thresholds: plan exit criteria (100% P0, no open Blocker/Critical, RTM 100%; confirmed by the user with the Phase 1 defaults) plus the default release gate in `release-gate-criteria.md` (default thresholds, not separately confirmed); where they differ the stricter applies.

## 1. Executive Verdict: No-Go
- Open Blocker is 1 (DEF-001, No-Go cell: ≥ 1) and Executed Rate is 94.8% (55/58, No-Go cell: < 95%).
- Met: P0 pass 100% (8/8), P1 pass 95.8% (23/24), Blocked 0, open Critical 0, RTM coverage 100% (8/8), nothing Fixed-but-not-re-tested.
- Not meeting the Go column: overall pass rate 93.1% (54/58, needs ≥ 95%), open Major 1 (DEF-003, needs 0), Executed Rate.
- What would change it: DEF-001 is rated Blocker by the severity decision tree (the page is dead in the affected configuration) but Priority P2 (rare configuration). If the user re-rates DEF-001 to Major, the Blocker cell clears; the 3 `Not Run` cases (a real person, a real device and a midnight wait) still hold Executed Rate at 94.8% until the user reports them.
This is QA's recommendation; the release decision belongs to the user/PO.

## 2. Execution Summary
Source: `03-execution-notes.md` section 2 (59 cases). Informational (1: TC-ADD-012) is excluded from every rate.

| Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|
| 58 | 54 | 1 | 0 | 3 | 54/58 = 93.1% (of executed: 54/55 = 98.2%) |

Executed Rate = (54 + 1)/58 = 94.8%.

| Priority | Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|---|
| P0 | 8 | 8 | 0 | 0 | 0 | 100% |
| P1 | 24 | 23 | 1 | 0 | 0 | 95.8% |
| P2 | 19 | 18 | 0 | 0 | 1 | 94.7% |
| P3 | 7 | 5 | 0 | 0 | 2 | 71.4% |

Informational: TC-ADD-012 (30 emoji accepted, no oracle). Non-functional track (separate from the matrix counts): NF-PERF-02, NF-PERF-03 (x2), NF-SEC-01, NF-COMP-01 (x3) Pass; NF-PERF-01 Informational (187 ms render, 159 ms toggle for 50 habits x 1095 days, thresholds were only Proposed).
Round: 1 (only one round exists).

## 3. Defect Statistics
| Severity \ Status | New | Open | Fixed | Re-test | Closed | Reopened | Won't Fix |
|---|---|---|---|---|---|---|---|
| Blocker | 1 (DEF-001) | 0 | 0 | 0 | 0 | 0 | 0 |
| Critical | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Major | 1 (DEF-003) | 0 | 0 | 0 | 0 | 0 | 0 |
| Minor | 2 (DEF-002, DEF-004) | 0 | 0 | 0 | 0 | 0 | 0 |
| Trivial | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Re-test (awaiting user close): none. Open defects with Severity ≥ Major: DEF-001 (Blocker, P2 proposed), DEF-003 (Major, P2 proposed).

## 4. Requirement Coverage (RTM)
Total in-scope requirements 8 | with full case coverage in the RTM 8 (100%) | with a Failed case 1 (R7: TC-STO-006) | with a Not Run case 3 (R4: TC-WEEK-005; R6: TC-BKP-010; R8: TC-A11Y-005) | without cases 0.
Requirements whose cases all Pass: R1, R2, R3, R5 (4/8). Risky: R7 (data/storage edge), R8 (3 accessibility defects, screen reader not run).

## 5. Residual risks
- DEF-001: storage-unavailable configurations get a dead page (R7 edge); DEF-003/DEF-002/DEF-004: accessibility (R8).
- Not Run: midnight rollover, native file dialogs, screen reader; only Chromium tested; no other browser, no real phone.
- Unconfirmed: the 02b timing thresholds (Proposed), the WCAG AA level default, oracles of `approved default` cases.
- Observation not rated: after a double click on Add habit the status ends as `Name is required.` (habit was added).

## 6. Next actions
| # | Action | Owner | Due | Verify |
|---|---|---|---|---|
| 1 | Decide DEF-001 severity/priority (Blocker vs Major, P1 vs P2) | user/PO | [Needs input: due date] | updated `04-defects.md` |
| 2 | Fix DEF-001, DEF-003, then DEF-002/DEF-004 | developer [Needs input: owner] | [Needs input] | re-test TC-STO-006 + `03c` + regression of R7/R8 (`qa-regression-planner`) |
| 3 | Run the 3 manual cases from `03-execution-notes.md` section 6 and report Pass/Fail/Blocked | user | [Needs input] | results recorded |

## 7. Missing data / Assumptions
| Item | Status |
|---|---|
| Approver name, owners, due dates | N/A — no data yet |
| User's own browser/version | N/A — no data yet (Chromium only was run) |
| Confirmed thresholds for NF timings | N/A — Proposed only |
| Screen reader result (TC-A11Y-005) | N/A — no data yet |
| Real environment where `localStorage` throws (DEF-001) | N/A — simulated by init script |

> **QA Advisor**
> - *Why it matters:* the verdict follows thresholds, not feel; `Not Run` is risk, not "probably fine".
> - *Blind spots left:* other browsers, real device, screen reader, midnight, a user's own corrupt data.
> - *Default I will choose if you do not reply:* keep No-Go as written and offer the alternative of Conditional Go after DEF-001 is re-rated and the 3 manual cases are reported.

---

# Round 2 — Test Summary Report (build 1a50381)
- Date: 2026-11-27. Build: 1a50381 (`feat/habitly`). Environment: Windows 11, Node v22.23.2, Playwright 1.65.1 Chromium (headless) and built-in pane; static server on localhost:8791. Sources: `03-execution-notes.md` Round 2 (R2.3), `04-defects.md` Round 2, `03c-accessibility.md` Round 2, `04b-regression-plan.md`.
- Applied thresholds: same as Round 1 (plan exit criteria plus default release-gate thresholds, not separately confirmed; stricter applies).

## R2.1 Executive Verdict: Conditional Go
- Met: P0 Pass 100% (8/8), P1 Pass 100% (24/24), Blocked 0, open Critical 0, RTM coverage 100% (8/8), nothing Fixed-but-not-re-tested (all four defects were re-tested), no new defect.
- Not meeting the Go column: overall Pass Rate 94.8% (55/58, needs 95%), Executed Rate 94.8% (55/58, needs 100%). Both gaps come only from the 3 `Not Run` cases that need a person or device ("Not run: needs person": TC-WEEK-005 midnight, TC-BKP-010 OS file dialog, TC-A11Y-005 screen reader). Per `release-gate-criteria.md` such cases cap the verdict at Conditional Go and do not force No-Go through the Executed Rate.
- Defects: DEF-001 (Blocker), DEF-003 (Major), DEF-002 and DEF-004 (Minor) were re-tested Pass and were then closed by the user on 2026-11-27 ("close DEF-001, DEF-002, DEF-003, DEF-004"): open Blocker 0, open Major 0. Before the closure the Open Defect definition (which lists `Re-test` as open) would have read Blocker 1 and Major 1, so the draft was provisional.
- Conditions: (1) [done 2026-11-27: the user closed DEF-001..DEF-004]; (2) the user runs the 3 manual cases in `03-execution-notes.md` section 6 and reports Pass/Fail/Blocked (owner: user; due: [Needs input]); consequence: a Fail in (2) turns the verdict into No-Go.
This is QA's recommendation; the release decision belongs to the user/PO.

## R2.2 Execution Summary
Source: `03-execution-notes.md` R2.3 (59 cases). Informational (1: TC-ADD-012) excluded from every rate.
| Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|
| 58 | 55 | 0 | 0 | 3 | 55/58 = 94.8% (of executed: 55/55 = 100%) |
Executed Rate = (55 + 0)/58 = 94.8%.
| Priority | Total | Passed | Failed | Blocked | Not Run | Pass Rate |
|---|---|---|---|---|---|---|
| P0 | 8 | 8 | 0 | 0 | 0 | 100% |
| P1 | 24 | 24 | 0 | 0 | 0 | 100% |
| P2 | 19 | 18 | 0 | 0 | 1 | 94.7% |
| P3 | 7 | 5 | 0 | 0 | 2 | 71.4% |
Round: 2 of 2. Change from round 1: Passed 54 -> 55, Failed 1 -> 0 (TC-STO-006). Non-functional track: all NF specs in the 53 Playwright passes; the 3 `NF-A11Y-01 (round 2)` specs Pass; NF-PERF-01 timings stay Informational (thresholds only Proposed).

## R2.3 Defect Statistics
| Severity \ Status | New | Open | Fixed | Re-test | Closed | Reopened | Won't Fix |
|---|---|---|---|---|---|---|---|
| Blocker | 0 | 0 | 0 | 0 | 1 (DEF-001) | 0 | 0 |
| Critical | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Major | 0 | 0 | 0 | 0 | 1 (DEF-003) | 0 | 0 |
| Minor | 0 | 0 | 0 | 0 | 2 (DEF-002, DEF-004) | 0 | 0 |
| Trivial | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
Re-test (awaiting user close): none (closed by the user on 2026-11-27).

## R2.4 Requirement Coverage (RTM)
Total in-scope requirements 8 | full coverage 8 (100%) | with a Failed case 0 | with a Not Run case 3 (R4: TC-WEEK-005; R6: TC-BKP-010; R8: TC-A11Y-005) | without cases 0. Requirements whose cases all Pass: R1, R2, R3, R5, R7 (5/8; R7 now Pass).

## R2.5 Residual risks
- Not Run: midnight rollover, native file dialogs, screen reader; Chromium only; no real phone.
- DEF-001 was verified with an init-script simulation, not a real browser setting (unchanged from round 1).
- Unconfirmed: the 02b timing thresholds (Proposed), the WCAG AA default level and the oracles of `approved default` cases, the contrast of the invalid-field border was computed from tokens, not measured in the page.
- Observation not rated: double click on Add habit ends with `Name is required.` although the habit was added.

## R2.6 Next actions
| # | Action | Owner | Due | Verify |
|---|---|---|---|---|
| 1 | Close DEF-001..DEF-004 | user | done 2026-11-27 | `04-defects.md` status |
| 2 | Run the 3 manual cases and report | user | [Needs input] | `03-execution-notes.md` section 6 |

## R2.7 Missing data / Assumptions
| Item | Status |
|---|---|
| User's own browser/version | N/A — no data yet |
| Screen reader, midnight and file-dialog results | N/A — no data yet |
| Confirmed NF timing thresholds | N/A — Proposed only |

> **QA Advisor**
> - *Why it matters:* the four fixes pass in Chromium and the P0/P1 sets are at 100%; the open risk is what only a person can check.
> - *Blind spots left:* screen reader, other browsers, real devices, the real blocked-storage setting.
> - *Default I will choose if you do not reply:* keep Conditional Go with the 3 manual cases as its condition.

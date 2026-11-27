# Execution Notes — habitly 1.0.0
- **Phase:** 3/5 — Execution
- **Date:** 2026-11-27
- **Version:** v0.1 (round 1)
- **Status:** Draft
- **Requirement source:** `qa-artifacts/habitly/02-test-matrix.md` (v0.3, Approved), `02b-nonfunctional.md` (Approved)
- **Approver:** [Needs input: approver name]

## 1. Run info
- Round: 1 | Date: 2026-11-27 | Build/commit: 8ec8923 (branch `feat/habitly`; the working tree also holds other people's uncommitted docs; QA changed no source) | Runner: Claude (QA agent)
- Environment actually used: Windows 11 Pro 10.0.26200; Git Bash and PowerShell; Node v22.23.2; Python 3.14.6 (`python -m http.server 8765` run from `habitly/`); Playwright 1.65.1 with Chromium 159.0.8154.6 (headless, installed in a scratch folder outside the repo; nothing added to `habitly/`); built-in browser pane (Chrome/156.0.8078.100 user agent) for the manual case and the accessibility audit. The user's own browser: `[Needs input]`.
- Browser tool choice: Playwright for the `Auto (browser)` specs; built-in browser pane for `TC-EDIT-006` and `03c`. Both worked.

## 2. Results per test case
| TC ID | Execution Type | Result (Pass/Fail/Blocked/Not Run/Informational) | Run date | Defect ID | Evidence/Notes |
|---|---|---|---|---|---|
| TC-ADD-001 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-001` |
| TC-ADD-002 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-002` |
| TC-ADD-003 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-003` |
| TC-ADD-004 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-004` |
| TC-ADD-005 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-005` |
| TC-ADD-006 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R1 negative: invalid name or target rejected, state not mutated |
| TC-ADD-007 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-007` |
| TC-ADD-008 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-008` |
| TC-ADD-009 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-009` |
| TC-ADD-010 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-010` |
| TC-ADD-011 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-ADD-011`; observed: final status after double click: "Name is required." class=error |
| TC-ADD-012 | Auto (browser) | Informational | 2026-11-27 | - | Playwright `TC-ADD-012`; observed: status: "Habit added.", rows: 1 |
| TC-EDIT-001 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-EDIT-001` |
| TC-EDIT-002 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-EDIT-002` |
| TC-EDIT-003 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-EDIT-003` |
| TC-EDIT-004 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R2 negative: unknown id and duplicate rename rejected |
| TC-EDIT-005 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R2 boundary: renaming to its own name is allowed |
| TC-EDIT-006 | Manual | Pass | 2026-11-27 | - | built-in browser pane: Edit Meditate, typed `lost` (field `Meditatelost`, button `Save changes`), reloaded: field empty, button `Add habit`, both habits intact in localStorage. No unsaved-edit warning shown (Informational) |
| TC-EDIT-007 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-EDIT-007` |
| TC-TOG-001 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-TOG-001` |
| TC-TOG-002 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-TOG-002` |
| TC-TOG-003 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-TOG-003` |
| TC-TOG-004 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-TOG-004` |
| TC-TOG-005 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R3 boundary: today allowed, tomorrow rejected, log kept sorted; R3 negative: bad date or unknown habit rejected |
| TC-TOG-006 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-TOG-006` |
| TC-TOG-007 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-TOG-007` |
| TC-TOG-008 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-TOG-008` |
| TC-WEEK-001 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-WEEK-001` |
| TC-WEEK-002 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-WEEK-002` |
| TC-WEEK-003 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R4 happy: week of Fri 2026-11-27 runs Mon 11-23 to Sun 11-29; R4 boundary: Sunday belongs to the previous Monday; month and leap-year math |
| TC-WEEK-004 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R4 boundary: weekCount counts only days inside the viewed week, ignoring duplicates; R4 negative: invalid dates throw / are detected |
| TC-WEEK-005 | Manual | Not Run | 2026-11-27 | - | needs the tab to stay open across local midnight (not run by the agent) |
| TC-STRK-001 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R5 happy: 3-day run ending today |
| TC-STRK-002 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R5 boundary: today not yet done keeps the run alive; a missed day resets it |
| TC-STRK-003 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-STRK-003` |
| TC-STRK-004 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-STRK-004` |
| TC-STRK-005 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-STRK-005` |
| TC-BKP-001 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R6 happy: export then import round-trips equal state |
| TC-BKP-002 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-BKP-002` |
| TC-BKP-003 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-BKP-003` |
| TC-BKP-004 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-BKP-004` |
| TC-BKP-005 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-BKP-005` |
| TC-BKP-006 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-BKP-006` |
| TC-BKP-007 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-BKP-007` |
| TC-BKP-008 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R6 negative: malformed backups are rejected with a specific message |
| TC-BKP-009 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R6 boundary: empty state and archived flag survive; unknown extra fields are dropped |
| TC-BKP-010 | Manual | Not Run | 2026-11-27 | - | needs the real OS file chooser / download dialog (not drivable by the agent); run script below |
| TC-STO-001 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R7 happy: save then load round-trips |
| TC-STO-002 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-STO-002` |
| TC-STO-003 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-STO-003` |
| TC-STO-004 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-STO-004` |
| TC-STO-005 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-STO-005` |
| TC-STO-006 | Auto (browser) | Fail | 2026-11-27 | DEF-001 | Playwright `TC-STO-006`; FAILED: Error: expect(locator).toHaveClass(expected) failed / Locator: getByRole('status') |
| TC-STO-007 | Auto (API) | Pass | 2026-11-27 | - | node:test (JUnit): R7 negative: corrupt data is kept under a backup key, not lost; R7 negative: invalid-but-parseable stored data is treated as corrupt; R7 negative: throwing storage degrades without throwing |
| TC-A11Y-001 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-A11Y-001` |
| TC-A11Y-002 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-A11Y-002` |
| TC-A11Y-003 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-A11Y-003` |
| TC-A11Y-004 | Auto (browser) | Pass | 2026-11-27 | - | Playwright `TC-A11Y-004` |
| TC-A11Y-005 | Manual | Not Run | 2026-11-27 | - | needs a real screen reader on a real device; not available to the agent |

Totals (computed by `tools/build_notes.py` from the reports): {"total": 59, "Pass": 54, "Informational": 1, "Not Run": 3, "Fail": 1, "byPrio": {"P0/Pass": 8, "P1/Fail": 1, "P1/Pass": 23, "P2/Not Run": 1, "P2/Pass": 18, "P3/Informational": 1, "P3/Not Run": 2, "P3/Pass": 5}}

Formula: Total 59; Informational (1) excluded from rates; Pass rate = 54/58 = 93.1%.

## 3. Automation
- Test files: `qa-artifacts/habitly/tools/e2e/habitly.spec.js`, `nonfunctional.spec.js`, page object `pages/HabitlyPage.js`, config `playwright.config.js`, fixtures `tools/fixtures/*.json`. Locators come from `index.html` and `src/ui/app.js` (labels, roles, `aria-label` at `app.js:62-64`); the only CSS selectors are the negative checks `tbody img` and `tbody b`.
- Command: `NODE_PATH=<scratch>/pw/node_modules playwright test -c qa-artifacts/habitly/tools/e2e --workers=1 --reporter=json,list` (static server on 8765 running).
- Machine-readable reports: `qa-artifacts/habitly/tools/results-pw-round1.json` (stats: expected 49, unexpected 1, flaky 0, skipped 0; this includes the 8 non-functional specs) and `tools/results-node-round1.xml` (JUnit, 26 testcases, 0 failures).
- Raw output of the failing test (verbatim from the JSON report, truncated to 700 characters):
```text
TC-STO-006: page opens when reading localStorage throws
Error: expect(locator).toHaveClass(expected) failed

Locator: getByRole('status')
Expected pattern: /error/
Received string:  ""
Timeout: 5000ms

Call log:
  - Expect "toHaveClass" getByRole('status') with timeout 5000ms
  - waiting for getByRole('status')
    14 × locator resolved to <p id="status" role="status" aria-live="polite"></p>
       - unexpected value ""

```
- Raw output of `node --test --test-reporter=spec` in `habitly/` (last 45 lines of the run; the JUnit file has all 26):
```text
✔ R1 happy: add habit trims name and assigns id (2.0043ms)
✔ R1 boundary: 60-char name and targets 1 and 7 accepted (0.2378ms)
✔ R1 negative: invalid name or target rejected, state not mutated (0.6522ms)
✔ R1 negative: duplicate name is case-insensitive (0.1953ms)
✔ R2 happy: edit, archive and restore keep data (0.2816ms)
✔ R2 boundary: renaming to its own name is allowed (0.2221ms)
✔ R2 negative: unknown id and duplicate rename rejected (0.3833ms)
✔ R3 happy: toggle twice returns to the original state (0.4663ms)
✔ R3 boundary: today allowed, tomorrow rejected, log kept sorted (0.5192ms)
✔ R3 negative: bad date or unknown habit rejected (0.4921ms)
✔ R4 happy: week of Fri 2026-11-27 runs Mon 11-23 to Sun 11-29 (0.5425ms)
✔ R4 boundary: Sunday belongs to the previous Monday; month and leap-year math (0.1489ms)
✔ R4 boundary: weekCount counts only days inside the viewed week, ignoring duplicates (0.1662ms)
✔ R4 negative: invalid dates throw / are detected (0.1266ms)
✔ R4 happy: localDateString formats local date with padding (0.9052ms)
✔ R5 happy: 3-day run ending today (0.2067ms)
✔ R5 boundary: today not yet done keeps the run alive; a missed day resets it (0.1373ms)
✔ R5 negative: no logs gives 0 and 0; duplicates not double counted (0.1047ms)
✔ R6 happy: export then import round-trips equal state (3.4425ms)
✔ R6 boundary: empty state and archived flag survive; unknown extra fields are dropped (0.4703ms)
✔ R6 negative: malformed backups are rejected with a specific message (1.1498ms)
✔ R7 happy: save then load round-trips (0.4469ms)
✔ R7 boundary: empty storage gives empty state and no notice (0.1609ms)
✔ R7 negative: corrupt data is kept under a backup key, not lost (0.1689ms)
✔ R7 negative: invalid-but-parseable stored data is treated as corrupt (0.2408ms)
✔ R7 negative: throwing storage degrades without throwing (0.1957ms)
ℹ tests 26
ℹ suites 0
ℹ pass 26
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
ℹ todo 0
ℹ duration_ms 118.4796
```
- Test defects found and fixed (not product defects): (1) the first run used 4 parallel workers and 5 tests failed (`net::ERR_CONNECTION_REFUSED` or missing handlers) against the single `python -m http.server`; with `--workers=1` the same tests passed (2/2 repeats, then the full run). Cause not investigated further: environment flake, not product. (2) `TC-A11Y-001` first expected the name field and 7 cells as Tab stops; the test did not reload after `add()` and the Sat/Sun cells are disabled today. Test fixed, assertion not loosened. (3) matrix step error in `TC-TOG-006` (dates share one week) fixed in matrix v0.3.

## 3b. Non-functional track (02b; thresholds were Proposed)
| NF ID | Result | Evidence |
|---|---|---|
| NF-PERF-01: 50 habits x 1095 days renders and toggles (Proposed < 1000 ms each) | Informational (timing vs Proposed threshold) | state 716355 chars; reload to last row visible 187 ms; toggle to status 159 ms (proposed limit 1000 ms, unconfirmed -> Informational) |
| NF-PERF-02: storage quota reached -> error shown, page keeps working | Pass | filler keys written until quota: 13 |
| NF-PERF-03: import of 1999000 chars is accepted | Pass | import handled in 215 ms (proposed limit 3000 ms, unconfirmed) |
| NF-PERF-03: import of 2000100 chars is rejected as too large | Pass | import handled in 219 ms (proposed limit 3000 ms, unconfirmed) |
| NF-SEC-01: hostile names stay text; __proto__ log key rejected | Pass | assertions passed |
| NF-COMP-01: no page-level horizontal scroll at 360x740 | Pass | assertions passed |
| NF-COMP-01: no page-level horizontal scroll at 768x1024 | Pass | assertions passed |
| NF-COMP-01: no page-level horizontal scroll at 1280x800 | Pass | assertions passed |
| NF-A11Y-01 | see `03c-accessibility.md` | 3 findings (1 Major, 2 Minor) |

Timings are `Informational`: the 02b thresholds were `Proposed`, and the user's approval of the table did not say they were confirmed.

## 4. Findings from exploratory testing
- `TC-ADD-011` (double-click Add habit): one habit is added, but the status line ends as `Name is required.` in error style because the second submit sees the cleared form. The habit exists, the message suggests it failed. Oracle was `code behavior`, so the case is Pass and this is an observation for the user to rate.
- `TC-ADD-012`: 30 emoji (60 UTF-16 units) is accepted (`Habit added.`).
- `TC-EDIT-006` (manual, executed in the built-in pane): Edit Meditate, typed `lost` (field value `Meditatelost`, button `Save changes`), reloaded: field empty, button `Add habit`, both habits intact in `localStorage`. No warning about the lost edit. Pass; whether a warning is wanted is an open question only.
- Probe for `TC-STO-006` (see DEF-001): with a throwing `window.localStorage` getter the run printed `PAGEERROR: denied`; `#status` stayed empty, the grid header had 0 rows and the form did nothing (`after add -> URL http://localhost:8765/ rows 0`).

## 5. Blockers and causes
- `TC-WEEK-005`: needs the tab open across midnight (Not Run).
- `TC-BKP-010`: real OS file chooser and download dialog (Not Run).
- `TC-A11Y-005`: real screen reader (Not Run).
- Other browsers and a real phone: outside the plan (Chromium only).

## 6. Manual run script for the user (leave the result cells blank)
### Group: Backup dialogs — setup: `python -m http.server 8765` in `habitly/`, open http://localhost:8765/
| # | TC ID | Steps | Data | Expected result | Result (Pass/Fail/Blocked) | Notes/Evidence |
|---|---|---|---|---|---|---|
| 1 | TC-BKP-010 | 1. Click Export JSON and save the file 2. Use the Import JSON file control and pick the saved file in the OS dialog | any habit | file saved as `habitly-backup-<date>.json`; import works | ☐ | |
### Group: Time and assistive tech
| # | TC ID | Steps | Data | Expected result | Result (Pass/Fail/Blocked) | Notes/Evidence |
|---|---|---|---|---|---|---|
| 2 | TC-WEEK-005 | 1. Leave the page open across local midnight 2. Look at the grid | - | observe only | ☐ | |
| 3 | TC-A11Y-005 | 1. Turn on a screen reader 2. Toggle a cell and add a habit | - | cell name and state announced, status announced | ☐ | |

> Have you finished a group? Tell me Pass / Fail / Blocked per TC and, for Fail, the symptom. Cases not run stay `Not Run`.

> **QA Advisor**
> - *Why it matters:* all 8 P0 cases passed (persistence, toggle, import safety held in Chromium); the one failure is the storage-unavailable edge.
> - *Blind spots left:* other browsers, real devices, screen reader, midnight rollover.
> - *Default I will choose if you do not reply:* log the failure and the 3 accessibility findings as defects (Phase 4).

## 7. Skills considered and skipped (handover note)
- `qa-api-tester`: Not applicable: no endpoints. habitly is a static page that talks only to `localStorage` (no router, no OpenAPI, no `fetch`); `python -m http.server` only serves the files. The 13 `Auto (API)` cases are the developer's `node --test` suites ("automated non-UI run") and were run here through the repo's own tooling.
- `qa-regression-planner`: skipped, no defect has been fixed yet (it needs a new build to select a regression set).
- `qa-nonfunctional-writer`: used (02b design, section 3b results). `qa-accessibility-auditor`: used (`03c-accessibility.md`).

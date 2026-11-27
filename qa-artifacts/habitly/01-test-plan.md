# Test Plan — habitly 1.0.0 (browser habit tracker)
- **Phase:** 1/5 — Test Plan
- **Date:** 2026-11-27
- **Version:** v0.2
- **Status:** Approved (approved on: 2026-11-27, user said "approved"; defaults for questions 1-7 accepted)
- **Requirement source:** `plan/003-habitly.md` §1 (R1–R8), §5 edge cases, §6; `habitly/README.md`; code in `habitly/` (cross-check only). Commit 8ec8923, branch `feat/habitly`.
- **Approver:** project owner (user)

Module namespace: this module's artifacts live in `qa-artifacts/habitly/` because the root `qa-artifacts/` holds taskbox files. IDs `R1`–`R8` are scoped to plan 003 (the plan itself cites them as `003:Rn`).
Language: English. Advisor: see end of file.

## 1. Requirement Audit
Skipped N/A groups: Missing permissions (single user, no accounts), Dependencies (no external services), Abuse protection, Observability, Output & console (not a CLI).

| # | Requirement (ID) | Issue | Type | Clarifying question | Suggested default |
|---|---|---|---|---|---|
| 1 | R7 / plan §5 "localStorage unavailable -> in-memory fallback with message" | `load()` handles a throwing `getItem`, but `app.js:24` and `app.js:174` reference the global `localStorage` directly; in a browser where merely reading `window.localStorage` throws (some private/blocked modes), the module throws before `load()` runs. [Inferred from code — needs confirmation] | Missing error flow | Must the page still open when `localStorage` access itself throws? | Yes: page opens empty with the "Storage is unavailable" notice |
| 2 | R3 | No lower bound on the date: can a day before the habit's `createdAt` (or years ago) be toggled? Code allows it (`habits.js:64-73`). | Ambiguity | Allow past days before creation? | Allow (backfilling is normal); `Informational` if unsure |
| 3 | R4 | "Today" is read from the clock at render; a tab left open across midnight keeps showing yesterday as today until a re-render. | Missing states / Data | Must the grid refresh at midnight? | No; accepted limitation, observe only |
| 4 | R4/R5 | "Per-week count vs target": does the count include days the habit was archived/restored, and what shows when count exceeds target (e.g. 5/3)? | Ambiguity | Show raw count, no cap | Show raw count (`5/3 this week`) |
| 5 | R8 | "usable at 360px width without horizontal page scroll": the grid sits in a scroll region (`index.html:37`). Is horizontal scroll inside the grid region acceptable? | Ambiguity | Is only page-level h-scroll forbidden? | Yes: region scroll is acceptable, page scroll is not |
| 6 | R2 | Duplicate-name check includes archived habits (`habits.js:26-31`): restoring or re-adding a name equal to an archived habit is rejected. Not stated in the plan. | Contradiction / missing rule | Should an archived name block a new habit with the same name? | Yes (current behavior), message tells the user |
| 7 | R6 | Import replaces all habits after `window.confirm` when data exists (plan §9 mentions the confirm; R6 does not). | Ambiguity | Is a replace-all confirm the intended rule? | Yes |
| 8 | R8 | "all controls reachable/operable": the Import control is a native file input; the file chooser cannot be driven or verified by keyboard alone in an automated run. | Data / Dependencies | Is the native file picker in scope for a11y verification? | Reachability and label only; picker dialog is `Not Run` |
| 9 | R1 | Name length counted in UTF-16 code units (`name.length`), so an emoji counts as 2. Boundary for non-BMP text not specified. | Data | Count characters or code units? | Code units (current behavior) — `Informational` |
| 10 | Non-functional | No threshold for data volume or storage size; browser localStorage quota is about 5 MB (varies). | Non-functional | Target size (habits x days) and acceptable render time? | [Needs input: thresholds]; propose 50 habits x 3 years, render < 1 s, as `Proposed` |

## 2. Scope
- In-scope: R1–R8 in the browser UI served statically; Chromium via the built-in browser pane (and Playwright Chromium if installed); desktop width and 360px viewport; light theme (dark theme contrast checked in the accessibility audit).
- Out-of-scope: accounts/sync, notifications, charts, i18n, PWA (plan §1 out of scope); other browsers (Firefox/Safari) — `[Needs input: required browsers]`, not run; real screen readers — need a user/device (`Not Run` until reported); native file-picker dialog and file download dialog (OS UI, cannot be driven).
- Developer tests (`node --test`, 26 tests) are the developer's; QA runs them for evidence and maps them to cases, but does not write new unit tests.

## 3. Risk Analysis
| Risk | Likelihood (H/M/L) | Impact (H/M/L) | Test priority | Mitigation |
|---|---|---|---|---|
| R7/R6 data loss (corrupt storage overwritten, bad import wipes data) | M | H | P0 | Negative and corrupt-data cases, import with confirm cancel |
| R3 toggle correctness and persistence (core flow) | M | H | P0 | Happy + reload persistence + future-day block |
| R1 add/validate (entry point of all data) | M | M | P1 | EP + BVA on name/target |
| R5 streak math (month/year boundary, today-not-done) | M | M | P1 | BVA on dates, gaps |
| R4 week grid / navigation | L | M | P2 | Week of 2026-11-27 starts 2026-11-23 |
| R8 keyboard + 360px | M | M | P1 | Keyboard walk, 360px reflow (see 03c) |
| R2 edit/archive/restore | L | M | P2 | State transitions |

## 4. Test Strategy
Auto (API) = automated non-UI run (the repo's `node --test` domain tests; there is no HTTP API, so `qa-api-tester` does not apply).

| Area/Module | Manual | Auto (browser) | Auto (API) | Reason |
|---|---|---|---|---|
| Add/edit/archive habit UI (R1, R2) | exploratory (double submit, emoji) | yes | domain validation (existing node tests) | Main CRUD, repeated every release |
| Toggle, persistence (R3, R7) | reload mid-flow | yes | storage tests (fake store) | Core flow |
| Week grid/streak (R4, R5) | visual check | week navigation | date/streak math (node) | Math is pure, UI shows it |
| Backup export/import (R6) | file picker, download | import via file input with a fixture | backup parse/validate (node) | Native dialogs are manual |
| Keyboard/360px (R8) | screen reader (user) | keyboard + viewport checks | — | See `03c-accessibility.md` |
| Storage limits, large data | — | script run in browser | — | See `02b-nonfunctional.md` |

Tooling: Playwright if it can be installed outside the project; otherwise the built-in browser pane with scripted steps. [Needs input: permission to add Playwright (dev dependency) — default: install only in a scratch folder outside `habitly/`, nothing added to the repo.]

## 5. Test Environment & Data
- Environment: static server `python -m http.server <port>` run from `habitly/`, URL `http://localhost:<port>/` [Needs input: port — default 8765; `package.json` "serve" uses 8080]
- Browser/device: [Needs input: browser and version — will be recorded from the real run]
- Accounts/roles: none (single local user)
- Data to prepare: empty localStorage; name of 60 and 61 chars; targets 0,1,7,8,2.5; backup fixtures (valid, bad version, duplicate ids, non-JSON, huge) created under `qa-artifacts/habitly/tools/fixtures/`.
- Date: tests that depend on "today" use the real clock; the plan example date 2026-11-27 is only a reference.

## 6. Entry / Exit Criteria
- Entry: app serves on localhost, `node --test` passes, empty storage available.
- Exit (Proposed — user to confirm): 100% of P0 pass, no open Blocker/Critical defect, RTM covers 100% of in-scope requirements, every `Not Run` listed with a reason.

## 7. Open questions / Assumptions
1. Audit #1 (storage access throws): default "page must still open".
2. Audit #2/#4/#7/#9: defaults as in the table; cases whose oracle is only a proposed default are marked `proposed default`.
3. Browsers: default Chromium only.
4. Playwright: default install in scratch folder only (no repo change).
5. Port 8765 for the static server.
6. Non-functional thresholds (audit #10): default proposed values above.
7. Where artifacts go: `qa-artifacts/habitly/` (isolated from taskbox files).

> **QA Advisor**
> - *Why it matters:* all data lives in one localStorage key; one bad write or import loses everything, so R6/R7 get P0.
> - *Blind spots to watch:* corrupt/over-quota storage, double-click on a day cell, reload mid-edit, boundary text (empty, 60/61 chars, emoji), date boundaries (month/year, Sunday/Monday).
> - *Default I will choose if you do not reply:* answers 1–7 above as written.

# Delivery notes - habitly: fix of DEF-001..DEF-004 to release

Build under test (commit): 1a50381
Base branch: [Needs input: PR base branch; `main` and `origin/main` exist, `feat/habitly` is unmerged]
Version/tag: none (habitly/package.json:3 declares 1.0.0)

## Stage 0 - Kickoff - 2026-11-27
Existing artifacts kept (habitly artifacts are already module-namespaced; no question needed): plan/003-habitly.md (Done), qa-artifacts/habitly/01..05 (+02b, 03c, tools/), docs/habitly/, habitly/README.md, habitly/CHANGELOG.md. Root `delivery-notes.md` belongs to taskbox, so this file is `delivery-notes-habitly.md` (CONVENTIONS section 5). R-ids are cited as `003:Rn`.
Installed skill sets: all four (user). `plan/` is git-ignored (`.gitignore:1`); `qa-artifacts/habitly/` and `docs/habitly/` are tracked.
Entry point: Stage 1 as a bug-fix loop (QA round 1 is No-Go with DEF-001 Blocker and DEF-003 Major open). No new plan; plan 003 R7 and R8 cover the fixes.

## Stage 1 - Build (bug-fix loop) - 2026-11-27 - status: Done
Artifacts: habitly/src/storage.js (`getStore`), habitly/src/ui/app.js (`store`, `clearInvalid`, `markInvalid`), habitly/styles.css (`--control-line`, `--done-fg`, `[aria-invalid]`), habitly/tests/contrast.test.js (new), habitly/tests/persistence.test.js (+2 tests). Commit 1a50381 (user asked to commit at the root-cause stop).
Real results:
- Reproduced before the fix (Playwright 1.65.1 / Chromium, probe script + TC-STO-006): DEF-001 `PAGEERROR denied`, 0 rows, status "denied"; DEF-003 input/cell border 1.58 light, 1.61 dark; DEF-002 check mark 2.22 dark; DEF-004 `aria-invalid` null, `aria-describedby` null, focus on `habit-submit`.
- Regression tests failed before the fix: `node --test` -> `tests 24, pass 18, fail 6` (persistence.test.js could not load: `getStore` missing; 5 contrast tests failed). After: `tests 33, pass 33, fail 0` (baseline was 26).
- After the fix (same probe): border 3.49 light / 3.71 dark; check mark 5.35 light / 8.55 dark; `aria-invalid=true`, `aria-describedby=status`, focus on the offending field for name and target errors; DEF-001 page renders (1 header row, 1 body row), no page error; TC-STO-006 `1 passed`.
Open items: DEF-004 has no automated regression test in the dev suite (DOM behaviour; probe only); to be added to the QA Playwright spec in Stage 3. No formatter/linter configured in habitly/package.json.
Skipped skills (reason): feature-plan-writer (no new plan), test-case-writer (1-3 case lists inside bug-investigator), refactor-planner, migration-writer (not needed).

## Stage 2 - Pull Request - 2026-11-27 - status: Done (PR text drafted; PR not opened, nothing pushed)
Artifacts: commit 1a50381 on feat/habitly (on top of e033d36); PR text below. `commit-message-writer`: the message of 1a50381 already follows the conventional format; no split proposed (4 defects, 5 files, +80/-11 lines, one actor). `pr-splitter` not used (fix diff is small; the branch-vs-main diff is one unmerged feature plus QA files). Base: [Needs input: PR base branch].
Real results: `pre-pr-self-review` (traced + ran) verdict: ready to open. `node --test` -> `tests 33, pass 33, fail 0`. 003:R7 covered (app.js:13, storage.js:8-14, persistence.test.js getStore tests, TC-STO-006 passes); 003:R8 partial: contrast covered by contrast.test.js, error linkage (DEF-004) traced + probed, no automated test yet.
Accepted risks: DEF-004 has no automated regression test until the QA round 2 spec is added - user - 2026-11-27.
Worth considering: `markInvalid` picks the field from the message text (`/^Target/`, app.js) - breaks if domain messages are reworded; a `field` property on ValidationError would be sturdier (not done: out of scope of the bug fixes).

### PR text
Title: fix(habitly): blocked localStorage no longer kills the page; raise control and check contrast; link form errors to fields

**Problem**
QA round 1 found four defects. With `window.localStorage` throwing, the page is dead: no grid, Add does nothing (DEF-001, Blocker). Input and day-cell borders are 1.58:1 / 1.61:1 against the page (DEF-003, Major, WCAG 1.4.11), the check mark on a done cell is 2.22:1 in dark mode (DEF-002, Minor, 1.4.3), and an invalid submit is not tied to its field (DEF-004, Minor, 3.3.1).

**Cause**
`app.js` read the global `localStorage` at module top level and in `commit`; the property access itself throws, before `load()`'s guard is reached. One shared `--line` colour served both separators and control borders; the dark `--done` fill kept a white glyph; the single `#status` line had no field association.

**Fix**
`getStore()` returns `null` when the read throws, so the page runs in memory with the existing notices. New tokens `--control-line` (3.49:1 light, 3.71:1 dark) and `--done-fg` (8.55:1 dark, 5.35:1 light). A failed submit sets `aria-invalid` and `aria-describedby="status"` on the offending field and focuses it. Separator colour `--line` is unchanged.

**How to verify**
`cd habitly && node --test` -> 33 pass (new: `tests/contrast.test.js`, two `getStore` tests; they failed before the fix). In a browser with a throwing `localStorage` getter the page renders and Add works. Playwright TC-STO-006 passes. Manual: blank name, then target 9: the field is outlined, focused and announced with the message.

**Notes**
DEF-004 has no automated test yet (QA round 2 adds one). Closes DEF-001..DEF-004 (qa-artifacts/habitly/04-defects.md) once the user closes them after re-test. Tests: [CI result: no CI configured].

## Stage 3 - QA (round 2) - 2026-11-27 - status: Done, verdict Conditional Go (QA round: 2)
Verdict + gate source: Conditional Go (provisional only until the 3 person-needed cases run) - `qa-artifacts/habitly/05-summary-report.md` Round 2 (R2.1).
Artifacts: qa-artifacts/habitly/03-execution-notes.md (Round 2, v0.2), 03c-accessibility.md (Round 2, v0.2), 04-defects.md (Round 2 + re-test history, v0.2), 04b-regression-plan.md (new, Round 2), 05-summary-report.md (Round 2 appended, v0.2); tools/results-pw-round2.json, results-node-round2.xml, results-round2-table.md, results-round2-summary.json; tools/e2e/nonfunctional.spec.js (+3 NF-A11Y-01 specs), tools/build_notes.py (reads ROUND). Phases 1-2 not repeated (no requirement or case change; matrix v0.3 stays Approved).
Real results (build 1a50381): Playwright `53 passed (15.9s)`, stats expected 53, unexpected 0, flaky 0; `node --test` `tests 33 pass 33 fail 0`; table: Total 59 | Pass 55 | Fail 0 | Blocked 0 | Not Run 3 | Informational 1; Pass rate 55/58 = 94.8%, P0 8/8, P1 24/24. The 3 new specs fail on e033d36 (`3 failed`) and pass on 1a50381. Built-in pane 360x740 dark: borders 3.71, check mark 8.55, `aria-invalid="true"` + focus on field, scrollWidth 360/360, TC-EDIT-006 Pass.
Not run / failing items: TC-WEEK-005 (midnight, needs a person), TC-BKP-010 (OS file dialog, needs a person), TC-A11Y-005 (screen reader, needs a person/device). No failing case.
Defects: DEF-001..DEF-004 re-tested Pass and closed by the user ("close DEF-001, DEF-002, DEF-003, DEF-004"), 2026-11-27.
Skipped skills (reason): qa-api-tester (no endpoints), qa-nonfunctional-writer (no 02b change; NF checks ran inside the Playwright run), qa-test-plan-writer / qa-test-matrix-writer (no change).

## Decisions
| Date | Decision | By |
|---|---|---|

# Regression Plan — habitly 1.0.0
- **Phase:** 4/5 — Regression selection
- **Date:** 2026-11-27
- **Version:** v0.1 (first plan of this module; section "Round 2" is the re-test of build 1a50381)
- **Status:** Draft (layer confirmation is not an approval stop; proceeded with the stated default)
- **Requirement source:** `qa-artifacts/habitly/02-test-matrix.md` (v0.3, RTM), `04-defects.md` (DEF-001..DEF-004)

## Round 2 — build 1a50381 (base e033d36)
Change set (`git diff e033d36 1a50381 --stat -- habitly`): `src/storage.js` (+`getStore`), `src/ui/app.js` (`store`, `clearInvalid`, `markInvalid`, `guard(fn, onError)`), `styles.css` (tokens `--control-line`, `--done-fg`, invalid-field border), `tests/contrast.test.js`, `tests/persistence.test.js`; 5 files, +80/-11. Fixed defects: DEF-001, DEF-002, DEF-003, DEF-004.

| Changed area | Impacted requirements | Cases | Risk | Why |
|---|---|---|---|---|
| `getStore` and `store` in `app.js` (read of `localStorage`) | R7; every R that saves via `commit` (R1, R2, R3, R6) | TC-STO-001..007, TC-ADD-001, TC-TOG-001, TC-BKP-* | High | `commit` and startup now go through `store` (null when blocked) |
| Form submit path (`guard`, `markInvalid`, `clearInvalid`, `endEdit`) | R1, R2, R8 | TC-ADD-001..011, TC-EDIT-001..007 | High | defect DEF-004 and the edit/cancel flow share the code |
| `styles.css` tokens (borders, check mark, invalid border) | R8 and every visible control | TC-A11Y-001..004, NF-A11Y-01, NF-COMP-01 | Medium | colour and border changes only; focus outline untouched |

Layers: **Smoke** (P0 happy paths) and **Targeted** (the three rows above) are both inside **Full**. Chosen: **Full automated run** (all `Auto (browser)` and `Auto (API)` cases plus 3 new `NF-A11Y-01 (round 2)` specs; about 16 s measured in round 2) because the shared files touch every browser case and the run is cheap. **Manual**: `TC-EDIT-006` re-run by hand (edit flow code changed); `TC-WEEK-005`, `TC-BKP-010`, `TC-A11Y-005` need a person or device and stay `Not Run`.
Excluded with reason: none of the automated cases; the 3 Not Run cases above (not drivable by the agent).
Effort: automated about 16 s (Playwright, `--workers=1`) + 0.1 s (node); manual about 5 minutes.
Entry/exit: stop and report if any smoke (P0) case fails; exit when every selected case has a recorded result; a failure of a previously passing case means `Reopened` on the related defect.
Default I chose: full automated run now, since it is cheaper than reasoning about exclusions.

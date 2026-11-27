# Defects — habitly 1.0.0
- **Phase:** 4/5 — Defect Management
- **Date:** 2026-11-27
- **Version:** v0.3 (round 2: Re-test Pass on 1a50381, then closed by the user on 2026-11-27)
- **Status:** Draft
- **Requirement source:** `qa-artifacts/habitly/03-execution-notes.md` (round 1), `03c-accessibility.md`
- **Approver:** [Needs input: approver name]

## 1. Summary table
| Defect ID | Title | Severity | Priority | Status (New/Open/Fixed/Re-test/Closed/Reopened/Won't Fix) | Related TC |
|---|---|---|---|---|---|
| DEF-001 | [Storage] Page is dead (no grid, form does nothing) when reading `window.localStorage` throws | Blocker (affected configuration only) | P2 (proposed) | Closed | TC-STO-006 |
| DEF-002 | [Week grid] Check mark on a done cell is 2.22:1 in the dark colour scheme | Minor | P2 (proposed) | Closed | NF-A11Y-01 (A11Y-F1) |
| DEF-003 | [Forms and grid] Borders of text inputs and empty day cells are 1.58:1 / 1.61:1 against the page | Major | P2 (proposed) | Closed | NF-A11Y-01 (A11Y-F2) |
| DEF-004 | [Forms] Validation errors are not tied to the offending field (no `aria-invalid`, no `aria-describedby`) | Minor | P3 (proposed) | Closed | NF-A11Y-01 (A11Y-F3), TC-ADD-003 |

## 2. Defect details
Duplicate check against the existing `04-defects.md` of this module (none) and of the root file (taskbox module, different product): no duplicates.

### DEF-001 — [Storage] Page is dead (no grid, form does nothing) when reading `window.localStorage` throws
| Field | Content |
|---|---|
| Title | [Storage] Page is dead (no grid, form does nothing) when reading `window.localStorage` throws |
| Related TC | TC-STO-006 (R7; plan §5 "localStorage unavailable (private mode) -> in-memory fallback with message") |
| Environment | Windows 11; Playwright 1.65.1 Chromium 159.0.8154.6 headless; static server `python -m http.server 8765`; commit 8ec8923. Condition simulated by an init script, not by a real browser setting: `Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('denied', 'SecurityError'); } })`. [Needs input: a real browser/setting where this happens (for example blocked site data)] |
| Severity / Priority | Blocker / P2 (proposed). Severity: in the affected configuration nothing works and there is no in-app workaround (decision tree step 1). Priority: only users whose browser throws on `localStorage` access are hit; PO to confirm how common. |
| Status | Closed (round 2 Pass on 1a50381; closed by the user, 2026-11-27) |
| Reproducibility | Always (5/5: 4 Playwright runs of TC-STO-006 and 1 probe script) |
| Pre-conditions | `window.localStorage` access throws `SecurityError` before the page scripts run |
| Steps to Reproduce | 1. Add an init script that makes the `localStorage` getter throw (snippet above) 2. Open `http://localhost:8765/` 3. Observe the page 4. Type `X` in Name and click Add habit |
| Actual Result | Console `PAGEERROR: denied`. `#status` is empty; the grid header has 0 rows; "Add habit" does nothing (rows stay 0, URL unchanged). |
| Expected Result | Page opens empty with the notice `Storage is unavailable; changes will not be saved.` and works in memory (source: plan 003 §5 edge case, and `approved default` of TC-STO-006 accepted at the Phase 2 stop; not in R7 wording; PO to confirm). |
| Evidence | `qa-artifacts/habitly/tools/results-pw-round1.json` (TC-STO-006 failed); probe output in `03-execution-notes.md` section 4; `habitly/src/ui/app.js:174` (`load(localStorage)`) and `:24` read the global directly. |
| Notes / Hypothesis (unconfirmed) | `load()` in `storage.js` already guards `getItem`, but the property access `localStorage` itself throws before `load()` is entered, at module top level. |

### DEF-002 — [Week grid] Check mark on a done cell is 2.22:1 in the dark colour scheme
| Field | Content |
|---|---|
| Title | [Week grid] Check mark on a done cell is 2.22:1 in the dark colour scheme |
| Related TC | NF-A11Y-01 (finding A11Y-F1 in `03c-accessibility.md`) |
| Environment | Built-in browser pane, Chrome/156.0.8078.100 user agent, 360x740, dark scheme emulation (app followed `prefers-color-scheme: dark`); commit 8ec8923 |
| Severity / Priority | Minor / P2 (proposed). The done state is also shown by the fill (8.15:1 against the page) and `aria-pressed`; WCAG 1.4.3 needs 4.5:1 for the glyph. |
| Status | Closed (round 2 Pass on 1a50381; closed by the user, 2026-11-27) |
| Reproducibility | Deterministic: computed from CSS values; measured once per colour scheme |
| Pre-conditions | Dark colour scheme; one habit with a day marked done |
| Steps to Reproduce | 1. Open the page in dark scheme 2. Add a habit and click today's cell 3. Compute the contrast of the cell's text colour (`#fff`) against its background (`#4cc38a`) |
| Actual Result | 2.22:1 (light scheme: 5.35:1) |
| Expected Result | At least 4.5:1 (source: approved default — WCAG 2.2 AA suggested in the plan and accepted at the Phase 2 stop; R8 itself does not state a contrast rule; PO to confirm) |
| Evidence | `03c-accessibility.md` script output; `habitly/styles.css:6` and `:28` |
| Notes / Hypothesis (unconfirmed) | Dark-scheme `--done` is a light green while the glyph colour stays white. |

### DEF-003 — [Forms and grid] Borders of text inputs and empty day cells are 1.58:1 / 1.61:1 against the page
| Field | Content |
|---|---|
| Title | [Forms and grid] Borders of text inputs and empty day cells are 1.58:1 / 1.61:1 against the page |
| Related TC | NF-A11Y-01 (finding A11Y-F2) |
| Environment | Same as DEF-002, both colour schemes |
| Severity / Priority | Major / P2 (proposed). Empty day cells have no fill, so the border is the only visual cue of the main control; a workaround exists (keyboard, hover). WCAG 1.4.11 needs 3:1. |
| Status | Closed (round 2 Pass on 1a50381; closed by the user, 2026-11-27) |
| Reproducibility | Deterministic: computed from CSS values (light 1.58, dark 1.61) |
| Pre-conditions | Page with at least one habit |
| Steps to Reproduce | 1. Open the page 2. Compute contrast of the border colour of the Name input and of an empty day cell against the page background |
| Actual Result | Light: 1.58:1. Dark: 1.61:1 |
| Expected Result | At least 3:1 (source: approved default — WCAG 2.2 AA; PO to confirm) |
| Evidence | `03c-accessibility.md`; `habitly/styles.css:3`, `:6`, `:17`, `:27` |
| Notes / Hypothesis (unconfirmed) | One shared `--line` colour is used for decorative separators and for control boundaries. |

### DEF-004 — [Forms] Validation errors are not tied to the offending field
| Field | Content |
|---|---|
| Title | [Forms] Validation errors are not tied to the offending field (no `aria-invalid`, no `aria-describedby`) |
| Related TC | NF-A11Y-01 (finding A11Y-F3); TC-ADD-003 |
| Environment | Built-in browser pane, 320x640, light; commit 8ec8923 |
| Severity / Priority | Minor / P3 (proposed). The message is real text and announced politely, but sits in the header status line. |
| Status | Closed (round 2 Pass on 1a50381; closed by the user, 2026-11-27) |
| Reproducibility | Always (1/1 by hand in the pane; also seen in the TC-ADD-003 and TC-ADD-007 runs for the message text) |
| Pre-conditions | Empty form |
| Steps to Reproduce | 1. Enter three spaces in Name 2. Click Add habit 3. Read `#habit-name` attributes and the active element |
| Actual Result | Status `Name is required.` (class `error`); `aria-invalid` null; `aria-describedby` null; focus stays on the submit button |
| Expected Result | The field is marked invalid and linked to the message (source: approved default — WCAG 3.3.1 under the accepted AA level; PO to confirm) |
| Evidence | probe output in `03c-accessibility.md` finding A11Y-F3; `habitly/src/ui/app.js:16-20`, `:129-141` |
| Notes / Hypothesis (unconfirmed) | Single global status element is used for every message. |

## 3. Re-test history
| Defect ID | Round | Build | Result | Regression checked |
|---|---|---|---|---|
| DEF-001 | 2 | 1a50381 (fix commit) | Pass: TC-STO-006 passes (Playwright, plus the same init-script probe: no page error, grid renders, Add works; status `Could not save to this browser; changes will be lost on reload.` after the first add; `Storage is unavailable; changes will not be saved.` on load) | R7 group TC-STO-001..007 Pass, full automated run 53 passed |
| DEF-002 | 2 | 1a50381 | Pass: check mark 8.55:1 dark, 5.35:1 light (need 4.5) | NF-A11Y-01 round 2, TC-TOG-* Pass |
| DEF-003 | 2 | 1a50381 | Pass: input and empty-cell border 3.49:1 light, 3.71:1 dark (need 3) | TC-A11Y-001..004 Pass, NF-COMP-01 at 360/768/1280 Pass |
| DEF-004 | 2 | 1a50381 | Pass: `aria-invalid="true"`, `aria-describedby="status"`, focus on the field (name and target); cleared after a valid submit | TC-ADD-003/005/007, TC-EDIT-* Pass; TC-EDIT-006 re-run by hand Pass |

> **QA Advisor**
> - *Why it matters:* Severity is technical impact, Priority is business urgency; I rated DEF-001 Blocker/P2 because one configuration is dead but rare, and DEF-003 Major/P2.
> - *Underrated risk:* DEF-001 is about a data-storage edge; nothing is lost, but the app is unusable there.
> - *Default I will choose if you do not reply:* keep these ratings; raise DEF-001 to P1 if blocked-storage browsers are an audience.

---

# Round 2 — defect status after the fix (build 1a50381)
Lifecycle followed: New -> Open (reproduced again before the fix in Stage 1; probe output in `delivery-notes-habitly.md`) -> Fixed (developer commit 1a50381) -> Re-test (this round, Pass). QA cannot close defects; all four stayed `Re-test` until the user closed them (the Stage 3 stop message asked for it; the user replied "close DEF-001, DEF-002, DEF-003, DEF-004" on 2026-11-27, so all four are now `Closed`).
| Defect | Severity / Priority (unchanged) | Status now | Re-test result |
|---|---|---|---|
| DEF-001 | Blocker / P2 (proposed) | Closed (user, 2026-11-27) | Pass |
| DEF-002 | Minor / P2 (proposed) | Closed (user, 2026-11-27) | Pass |
| DEF-003 | Major / P2 (proposed) | Closed (user, 2026-11-27) | Pass |
| DEF-004 | Minor / P3 (proposed) | Closed (user, 2026-11-27) | Pass |
New defects found in round 2: none. Observations only (not defects): double click on Add still ends with `Name is required.` after the habit is added (round-1 observation, unchanged); the invalid field now also gets a 2px `--err` border (design addition in the fix).
Regression of previously failed areas: no earlier Closed defects exist in this module.

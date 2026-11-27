# Accessibility Audit — habitly 1.0.0
- **Phase:** 3/5 — Execution (accessibility)
- **Date:** 2026-11-27
- **Version:** v0.1
- **Status:** Draft
- **Requirement source:** R8 in `plan/003-habitly.md`; NF-A11Y-01 in `qa-artifacts/habitly/02b-nonfunctional.md` (Approved)
- **Approver:** [Needs input: approver name]

## 1. Scope and environment
- Target level: WCAG 2.2 level AA (suggested in the plan; the user accepted the default at the Phase 2 stop).
- Flows: whole single page (add/edit habit form, week grid and navigation, archive/restore, export/import).
- Environment: static server `python -m http.server 8765` on Windows 11; commit 8ec8923 (branch `feat/habitly`).
- Tools: (a) built-in browser pane of the desktop app (Chrome/156.0.8078.100 user agent) — viewport emulation 360x740 and 320x640, light and dark scheme emulation, DOM and computed-style script (contrast computed with the WCAG relative-luminance formula by an inline script); (b) Playwright 1.65.1 with Chromium 159.0.8154.6 for the Tab walk (`TC-A11Y-001`). No axe/Lighthouse (an extra install was not requested).
- Code reviewed: `habitly/index.html`, `habitly/styles.css`, `habitly/src/ui/app.js`.

## 2. Findings
| ID | Page / flow | Element or file:line | WCAG criterion | Severity | Issue | Fix | Evidence |
|---|---|---|---|---|---|---|---|
| A11Y-F1 | Week grid, dark scheme | `styles.css:6` (dark `--done` #4cc38a) and `styles.css:28` (`.cell[aria-pressed=true]` color `#fff`) | 1.4.3 Contrast (Minimum) | Minor | The check mark on a done cell is white on #4cc38a: contrast 2.22:1 (needs 4.5:1; light scheme is 5.35:1). The pressed state is still conveyed by the fill (8.15:1 against the page) and `aria-pressed`. | Use a dark glyph colour on the light green in dark mode | Script output below (dark) |
| A11Y-F2 | Add form, week grid | `styles.css:3` and `:6` (`--line`) used by `input` (`styles.css:17`) and `.cell` (`styles.css:27`) | 1.4.11 Non-text Contrast | Major | The only visible boundary of the text inputs and of the empty day cells is a 1px border at 1.58:1 (light) and 1.61:1 (dark); 3:1 is needed. An empty day cell has no fill, so low-vision users can hardly see where to click. | Darken the border colour to at least 3:1 against the page | Script output below (both schemes) |
| A11Y-F3 | Add/edit form errors | `app.js:16-20` (`say`), `app.js:129-141` (submit) | 3.3.1 Error Identification | Minor | An invalid submit writes the message to the header status line (`role=status`); the input gets no `aria-invalid` and no `aria-describedby`, and focus stays on the button. The error is text and is announced politely, but it is not tied to the field. | Mark the offending field with `aria-invalid` and `aria-describedby` pointing at the message | Probe: `Name is required.`, class `error`, `aria-invalid` null, `aria-describedby` null, activeElement is the submit button (id `habit-submit`) — see TC-ADD-003 run |

Script output (computed styles, built-in browser pane, 360x740):
```text
DARK
body text: 15.32 (need 4.5)           status muted: 7.66            .meta: 7.66          label: 15.32
primary button text: 7.61              secondary button text (Edit): 7.25
cell pressed check: 2.22 (need 4.5)    input border vs page (1.4.11): 1.61 (need 3)
cell border vs page (1.4.11): 1.61     focus outline vs page: 10.81   pressed cell bg vs page: 8.15
error status: 7.90
LIGHT
body text: 16.45   status muted: 7.14   .meta: 7.14   label: 16.45
primary button text: 6.18   secondary button text (Edit): 5.92   cell pressed check: 5.35
input border vs page (1.4.11): 1.58 (need 3)   cell border vs page (1.4.11): 1.58 (need 3)
focus outline vs page: 4.81   pressed cell bg vs page: 5.13   error status: 6.30
```
(Lines condensed for width; values are the script's verbatim numbers. The script is the inline snippet used in the session, not saved as a file.)

Automated results: none (no scanner run). All findings above come from code, DOM or computed style I observed.

## 3. Coverage
| Check | Criterion | Result | What was checked |
|---|---|---|---|
| Keyboard reach and order | 2.1.1, 2.4.3 | Pass | Playwright Tab walk (`TC-A11Y-001`): stops in DOM order: skip link, name, target, Add habit, Previous/This/Next week, grid region, enabled day cells, Edit, Archive, Export, Import. Future (disabled) cells are skipped. |
| Focus visible | 2.4.7 | Pass | Every stop of the walk has a computed `outline-style` other than `none` (3px `--focus`, 4.81:1 light, 10.81:1 dark). |
| No keyboard trap | 2.1.2 | Pass (partly) | Tab left the page after the last control; native confirm dialog and file chooser not exercised by keyboard (see Not Run). |
| Bypass blocks | 2.4.1 | Pass | Skip link is the first stop, targets `#grid-section`. |
| Name, role, value | 4.1.2 | Pass | Day cells are `button[aria-pressed]` with `aria-label` `<habit>, <Dow> <date>` (`TC-A11Y-002`). |
| Labels | 3.3.2 / 1.3.1 | Pass | Name, Target and Import inputs have `<label for>`; table has `th scope` and a caption. |
| Status messages | 4.1.3 | Pass (DOM only) | `#status` has `role=status` and `aria-live=polite` (`TC-A11Y-003`); actual announcement not heard. |
| Reflow 360 / 320 px | 1.4.10 | Pass | Page-level `scrollWidth` equals `clientWidth` at 360 and 320; the week grid (495px wide) scrolls inside its own focusable labelled region (data table). |
| Target size | 2.5.8 | Pass | Day cell 38x44 px at 360 wide; buttons have min 44px height. |
| Language / title | 3.1.1, 2.4.2 | Pass | `lang="en"`; title `habitly` (short but descriptive for a one-page app). |
| Headings | 1.3.1 | Pass | h1, then h2 per section. |
| Contrast text | 1.4.3 | Fail | A11Y-F1 (dark scheme); all other text pairs 5.35:1 or higher. |
| Contrast controls | 1.4.11 | Fail | A11Y-F2. Focus indicator and pressed cell fill pass. |
| Error identification | 3.3.1 | Fail (partly) | A11Y-F3. |

## 4. Not Run
- Screen-reader pass (NVDA/JAWS/VoiceOver): no screen reader available to the agent; needs a person (TC-A11Y-005).
- Browser zoom to 200% (1.4.4 Resize Text): the pane tool does not support page zoom; 320 px reflow was checked instead.
- Text spacing override (1.4.12), focus not obscured (2.4.11), keyboard use of the native `confirm` dialog and file chooser, high-contrast/forced-colors mode, touch device.
- Automated scan (axe/Lighthouse): not installed; a clean scan would not have proved compliance anyway.

## 5. Next step
Log A11Y-F1..F3 as defects (done in `04-defects.md`: DEF-002, DEF-003, DEF-004); fixes go through the developer workflow. Re-run this file after a fix.

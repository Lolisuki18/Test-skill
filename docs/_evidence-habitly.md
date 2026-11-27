# Evidence list - habitly

Module: `habitly/`. Confirmed file list: `habitly/README.md`, `habitly/CHANGELOG.md`, `docs/_evidence-habitly.md`, `docs/habitly/diagrams/*`, `docs/habitly/adr/*`, `docs/habitly/user-guide.md`, `docs/habitly/release-notes.md`.
Commit read: `8ec8923` (branch `feat/habitly`, not merged, no tags). Facts re-verified on 2026-11-27.

| Fact | Source (path:line / commit / command) | Used in |
|---|---|---|
| Name `habitly`, version `1.0.0`, `"type": "module"`, no dependencies | `habitly/package.json:2-3,5` | README, CHANGELOG |
| Scripts: `test` = `node --test`, `serve` = `python -m http.server 8080` | `habitly/package.json:8-9` | README |
| `npm test` ran: 26 tests, 26 pass (Node v22.23.2) | command output, 2026-11-27 | README (verification only, count not written) |
| `python -m http.server 8080` fails with OSError when the port is in use (it was in use by another server on the test machine) | command output, 2026-11-27 | README |
| Page served on `http://localhost:8099/index.html` loads and works | built-in browser run, 2026-11-27 | user guide |
| Storage key `habitly.v1`; corrupt copy key `habitly.v1.corrupt` | `habitly/src/storage.js:4-5` | README, ADR 001, user guide |
| Corrupt or invalid stored data copied to the corrupt key, state starts empty | `habitly/src/storage.js:21-28` | ADR 001, user guide, diagram |
| Notice `Saved data was unreadable. A copy was kept; starting empty.` | `habitly/src/storage.js:27` | user guide |
| Notice `Storage is unavailable; changes will not be saved.` | `habitly/src/storage.js:16` | user guide |
| Message `Could not save to this browser; changes will be lost on reload.` | `habitly/src/ui/app.js:24` | user guide |
| State shape `{version, habits[{id,name,target,archived,createdAt}], log{id:[dates]}}` | `habitly/src/domain/habits.js:5-7,43`; `habitly/src/domain/backup.js:33,41` | ADR 003, diagram |
| Name 1-60 chars after trim; target whole number 1-7; duplicate names rejected, case-insensitive | `habitly/src/domain/habits.js:3,13-31` | user guide |
| Messages `Name is required.`, `Name must be at most 60 characters.`, `Target must be a whole number from 1 to 7.`, `A habit with this name already exists.` | `habitly/src/domain/habits.js:14-15,21,29`; seen in browser run | user guide |
| Future day rejected `Cannot mark a future day.`; future cells are disabled buttons | `habitly/src/domain/habits.js:67`; `habitly/src/ui/app.js:66` | user guide |
| Week runs Monday-Sunday, dates are local `YYYY-MM-DD` | `habitly/src/domain/dates.js:32-46`; `habitly/README.md:9` | README, user guide |
| Current streak: today undone does not break the run | `habitly/src/domain/streaks.js:3-6` | user guide |
| Grid cell text `✓` when done; row text `<n>/<target> this week`; streak text `<current> / best <best>` | `habitly/src/ui/app.js:65,59,70`; seen in browser run | user guide |
| Buttons/labels: `Add habit`, `Save changes`, `Cancel edit`, `Edit`, `Archive`, `Restore`, `Previous week`, `This week`, `Next week`, `Export JSON`, `Import JSON file` | `habitly/index.html:20-39,52-53`; `habitly/src/ui/app.js:72-73,80-82,116,125` | user guide |
| Status texts: `Habit added.`, `Habit updated.`, `Habit archived.`, `Habit restored.`, `Editing <name>.`, `Edit cancelled.`, `<name> done on <date>.`, `<name> not done on <date>.`, `Showing previous week.`, `Showing next week.`, `Showing this week.`, `Backup exported.` | `habitly/src/ui/app.js:98-154` ; seen in browser run | user guide |
| Export filename `habitly-backup-<YYYY-MM-DD>.json`; file = state plus `exportedAt` | `habitly/src/ui/app.js:146-155`; `habitly/src/domain/backup.js:6-8` | user guide, ADR 003 |
| Import: max `2_000_000` characters; messages `Backup is not valid JSON.`, `Unsupported backup version.`, `Backup file is too large.`, etc. | `habitly/src/domain/backup.js:4,14-45`; seen in browser run | user guide, ADR 003 |
| Import confirm `Importing replaces all current habits. Continue?` only when habits exist; `Import cancelled; your data is unchanged.`; `Import failed, your data is unchanged: <reason>`; `Imported <n> habits.` | `habitly/src/ui/app.js:157-172`; seen in browser run | user guide, diagram |
| Archived habits are kept in data, listed under "Archived" with `Restore`; empty list shows `None` | `habitly/src/ui/app.js:76-83` | user guide |
| Layers: pure logic in `src/domain/`, `src/storage.js`, DOM in `src/ui/app.js`; one `<script type="module">` | `habitly/index.html:61`; file layout | README, ADR 002, diagram |
| Storage object is injected (`store` with getItem/setItem) | `habitly/src/storage.js:7-11,32` | ADR 001 |
| No build tooling, no dependency in `package.json` | `habitly/package.json` (no `dependencies`, no build script) | ADR 002 |
| Initial commit only: `8ec8923` "feat(habitly): add vanilla JS habit tracker with node:test suite", 2026-11-27 | `git log` | CHANGELOG, ADRs dates |
| No git tags; branch `feat/habitly` not merged into `main` | `git tag`, `git branch -a` | CHANGELOG, release notes |
| Decision rationale and rejected alternatives for ADRs 001-003 | supplied by the user in chat (the plan file is git-ignored, so it is not cited) | ADRs |

## [Needs input]

- Supported browsers: not declared anywhere in the repo.
- Where the browser saves the exported file: depends on the browser settings, not on the code.
- Licence of habitly: `habitly/` has no licence file (the repo-root `LICENSE` is not stated to cover this module).
- Decision dates and deciders of ADRs: not recorded; commit date used.

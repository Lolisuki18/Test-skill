# Changelog

All notable changes to habitly are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). No release has been tagged.

## [Unreleased] - on branch `feat/habitly`, not merged

### Added
- `habitly`, a browser habit tracker with no build step and no dependencies: add, edit, archive and restore habits (name up to 60 characters, target 1 to 7 days a week); tick days in a Monday-to-Sunday week grid with previous, next and this-week navigation; per-week count against target; current and best streak; data kept in `localStorage` under `habitly.v1`; JSON export and validated import; 26 `node:test` tests (`8ec8923`).

### Fixed
Found by QA before the first release, fixed on this branch in `1a50381`:
- The page now opens and works in memory when the browser blocks `localStorage`, with the notice `Storage is unavailable; changes will not be saved.`; before, nothing was drawn and **Add habit** did nothing (DEF-001).
- Borders of text boxes and empty day squares now have at least 3:1 contrast against the page, and the check mark on a done day has at least 4.5:1 in the dark colour scheme (DEF-003, DEF-002).
- A rejected **Name** or **Target** box is outlined, linked to its error message with `aria-invalid` and `aria-describedby`, and receives the cursor (DEF-004).
- 7 more `node:test` tests (33 in total) cover the storage guard and the colour contrast.

<!-- Version and date: [Needs input: release version and date; package.json declares 1.0.0 (habitly/package.json:3), no tag exists] -->
<!-- Comparison links omitted: no tags exist. Repository: https://github.com/Lolisuki18/Test-skill (git remote origin). -->

# 003. Back up and move data with a validated JSON export and import

- **Status:** Accepted
- **Date:** 2026-11-27 (commit `8ec8923`; `[Needs input: decision date - not recorded]`)
- **Deciders:** `[Needs input: deciders - not recorded]`
- **Related:** [001](001-localstorage-for-persistence.md), [Import sequence](../diagrams/sequence-import-backup.md)

## Context

Because data lives only in one browser ([001](001-localstorage-for-persistence.md)), the user needs a way to keep a copy and to move data to another browser. Imported files are untrusted input.

## Options Considered

### Option 1: Export and import the full state as one JSON file
- Description: **Export JSON** downloads `habitly-backup-<date>.json` containing the state plus `exportedAt` (`habitly/src/ui/app.js:164-173`, `habitly/src/domain/backup.js:6-8`). **Import JSON file** parses and validates the file before anything is saved (`habitly/src/domain/backup.js:14-47`).
- Pros: readable file; the same validation function is used for stored data and imported data (`habitly/src/storage.js:2,29`); a bad file changes nothing.
- Cons: manual; replaces all current habits instead of merging (`habitly/src/ui/app.js:180`).

### Option 2: No backup, or automatic cloud sync (Implied alternative, not recorded as considered)
- Description: rely on the browser alone, or sync to a service.
- Pros: `[Needs input: not discussed]`
- Cons: no way to recover from cleared site data; sync is out of scope (user-stated).
- `[Needs input: confirm whether this was actually weighed]`

## Decision

We provide manual JSON export and import. Import rejects, without touching stored data: a file over `2_000_000` characters, invalid JSON, a version other than `1`, and entries with bad ids, names, targets or dates, duplicate ids, or a log for an unknown habit (`habitly/src/domain/backup.js:4,14-47`). When habits already exist, the user must confirm before they are replaced (`habitly/src/ui/app.js:180`). Unknown extra fields are dropped on import (`habitly/src/domain/backup.js:28`; test `R6 boundary` in `habitly/tests/persistence.test.js`).

## Consequences / Trade-offs

- **Positive:** the user owns a portable copy; a bad import cannot damage current data.
- **Negative / costs:** no merge; no automatic backup, so the copy is only as recent as the last manual export; the size limit counts characters, not bytes (`habitly/src/domain/backup.js:41`).
- **Risks and how they are checked:** rejection cases are covered by `R6 negative` in `habitly/tests/persistence.test.js`; the confirm dialog and messages were exercised by hand in a browser on 2026-11-27.
- **Follow-ups:** none recorded.

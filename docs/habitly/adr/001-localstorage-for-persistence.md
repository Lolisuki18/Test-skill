# 001. Keep habit data in the browser's localStorage under one key

- **Status:** Accepted
- **Date:** 2026-11-27 (commit `8ec8923`; `[Needs input: decision date - not recorded]`)
- **Deciders:** `[Needs input: deciders - not recorded]`
- **Related:** [003](003-json-export-import-backup.md), [Architecture diagram](../diagrams/architecture-habitly.md)

## Context

habitly is a single-page habit tracker with no accounts, no sync and no server of its own (user-stated scope; the repo has no server code). State must survive a page reload. The state is small: a list of habits and a log of done dates per habit (`habitly/src/domain/habits.js:5-7`, `habitly/src/domain/habits.js:43`). Stored data can be corrupt or unreadable, and the storage itself can be unavailable or fail on write (`habitly/src/storage.js:22-27,41-48`).

## Options Considered

### Option 1: Browser `localStorage`, one JSON value under the key `habitly.v1`
- Description: `load` reads the key and validates it; `save` writes the whole state as JSON (`habitly/src/storage.js:4,20,41`). The storage object is passed in, so tests use a fake (`habitly/src/storage.js:16-20`; `habitly/tests/persistence.test.js`).
- Pros: no server and no dependency; synchronous; simple to test with a fake object.
- Cons: data stays in one browser profile on one device; the whole state is rewritten on each change; browsers can clear it.

### Option 2: A server or hosted account with sync (Implied alternative, not recorded as considered)
- Description: store data remotely so several devices share it.
- Pros: `[Needs input: not discussed]`
- Cons: needs a server, accounts and a deployment, which the requirement lists as out of scope (user-stated).
- `[Needs input: confirm whether this was actually weighed]`

### Other options
`[Needs input: other options considered, e.g. IndexedDB; neither the repo nor git history mentions any]`

## Decision

We keep all habit data in `localStorage` as one JSON value under `habitly.v1`, with a version field inside the value (`version: 1`, `habitly/src/domain/habits.js:6`). It applies to the web page in `habitly/` only.

Handling of bad storage, as implemented:
- Unparseable or invalid stored data is copied to `habitly.v1.corrupt`, the app starts empty and shows a notice (`habitly/src/storage.js:30-37`). The next change then saves over `habitly.v1`; the copy under the corrupt key is not removed by the app.
- If reading throws, the app starts empty and says changes will not be saved (`habitly/src/storage.js:22-27`). This includes the case where reading the `localStorage` property itself throws: `getStore()` returns `null` instead (`habitly/src/storage.js:8-14`, `habitly/src/ui/app.js:13`).
- If writing fails, the app shows a message that changes will be lost on reload (`habitly/src/ui/app.js:25`).

## Consequences / Trade-offs

- **Positive:** nothing to deploy or install; bad data is never silently thrown away.
- **Negative / costs:** data does not move between browsers or devices except by the manual backup in [003](003-json-export-import-backup.md); clearing site data deletes it; a second corrupt event overwrites the previous `habitly.v1.corrupt` copy (`setItem` on the same key, `habitly/src/storage.js:32`).
- **Risks and how they are checked:** corrupt, empty and throwing storage are covered by tests in `habitly/tests/persistence.test.js` (R7 cases). The browser's own storage quota behaviour is not tested.
- **Follow-ups:** none recorded.

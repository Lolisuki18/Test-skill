# 002. Build habitly from vanilla ES modules with no build step and no dependencies

- **Status:** Accepted
- **Date:** 2026-11-27 (commit `8ec8923`; `[Needs input: decision date - not recorded]`)
- **Deciders:** `[Needs input: deciders - not recorded]`
- **Related:** [001](001-localstorage-for-persistence.md), [Architecture diagram](../diagrams/architecture-habitly.md)

## Context

The page is one HTML file that loads one module script (`habitly/index.html:61`). `package.json` lists no dependencies and no build script; its scripts are `test` and `serve` only (`habitly/package.json:8-9`). The logic must be testable without a browser: the files in `habitly/src/domain/` use no DOM or `localStorage`, and tests import them directly under `node --test` (`habitly/tests/domain.test.js:3-5`).

## Options Considered

### Option 1: Plain ES modules served as static files
- Description: the browser loads `src/ui/app.js`, which imports the other modules by relative path (`habitly/src/ui/app.js:1-5`).
- Pros: nothing to install or compile; any static server works; the same files run in the browser and in Node tests.
- Cons: no bundling, no type checking, no framework helpers; DOM building is hand-written (`el()` in `habitly/src/ui/app.js:29-37`).

### Option 2: A framework and/or bundler (Implied alternative, not recorded as considered)
- Description: use a UI framework with a build tool.
- Pros: `[Needs input: not discussed]`
- Cons: adds dependencies and a build step, which the requirement rules out (user-stated: no third-party packages, no build).
- `[Needs input: confirm whether this was actually weighed]`

## Decision

We write habitly as vanilla JavaScript ES modules with no build step and no third-party packages, split into pure logic (`src/domain/`), a storage wrapper (`src/storage.js`) and a DOM shell (`src/ui/app.js`). It applies to all of `habitly/`.

## Consequences / Trade-offs

- **Positive:** serve the folder and open the page; tests need only Node.
- **Negative / costs:** no minification or bundling; browser support depends on native module and `localStorage` support (`[Needs input: supported browsers not declared]`); the UI layer (`app.js`) has no automated tests, because tests cover the domain and storage modules only.
- **Risks and how they are checked:** the UI was checked by hand in a browser, not by a test suite.
- **Follow-ups:** none recorded.

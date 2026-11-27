# Non-functional Design — habitly 1.0.0
- **Phase:** 2/5 — Test Matrix (non-functional design)
- **Date:** 2026-11-27
- **Version:** v0.2
- **Status:** Approved (approved on: 2026-11-27, user said "approved"; proposed defaults accepted)
- **Requirement source:** `qa-artifacts/habitly/01-test-plan.md` (Approved v0.2) risks R6/R7, audit #10; `plan/003-habitly.md` §5 ("huge file", "localStorage unavailable"), R8
- **Approver:** project owner (user)

## 1. Attributes selected
- Selected: Performance/large data and storage limits (the whole state is one JSON string in one localStorage key), Security basics (input handling only), Compatibility (viewports on one browser), Accessibility (delegated to `03c-accessibility.md`).
- Out of scope this round: load/stress/soak (single-user, no server), transport/headers (static dev server, not the product), other browsers and real devices (no required browser list: `[Needs input: browsers]`), localization (plan: i18n out of scope), usability studies.

## 2. Cases
No threshold exists in the requirements; every threshold below is a **Proposed** value from the QA, to be confirmed. A measurement without a confirmed threshold is reported `Informational`.

| NF ID | Attribute | Scenario | Metric & threshold | Tool | Environment | Priority | Linked requirement |
|---|---|---|---|---|---|---|---|
| NF-PERF-01 | Performance / large data | Seed `habitly.v1` with 50 habits x 1095 logged days each (valid per the schema), reload, then time the first render and one toggle | Render and toggle each < 1000 ms (Proposed — user to confirm); else `Informational` | Playwright/browser `performance.now()` around load | Chromium on the local static server | P2 | R3, R4, R5 (audit #10) |
| NF-PERF-02 | Storage limit | Fill localStorage with filler keys until the next write fails (quota), then add a habit and toggle a day | After quota: error status `Could not save...` shown, page does not crash, in-memory state still usable (spec R7 + code `app.js:24`); no threshold on size | Playwright, script fills quota | Chromium | P1 | R7 |
| NF-PERF-03 | Large data / import | Import backups of 1,999,000 and 2,000,100 characters (limit `MAX_BACKUP_BYTES` 2,000,000 chars, `backup.js:4`) | Smaller one accepted or rejected for schema reasons only; larger rejected with `Backup file is too large.`; UI stays responsive (import < 3000 ms, Proposed) | Playwright `setInputFiles` | Chromium | P2 | R6 |
| NF-SEC-01 | Security basics | Backup JSON whose habit names are `<img src=x onerror=alert(1)>` and a log key `__proto__` | Names rendered as text only, no script runs; `__proto__` log key rejected with `Log refers to unknown habit` | Playwright | Chromium | P1 | R6, R1 |
| NF-COMP-01 | Compatibility | Open the page at 360x740, 768x1024 and 1280x800 | No page-level horizontal scroll at 360 and 768 (Proposed from R8); layout usable | Playwright viewport | Chromium | P2 | R8 |
| NF-A11Y-01 | Accessibility | WCAG 2.2 AA audit of the UI | See `03c-accessibility.md` (qa-accessibility-auditor); level AA is a suggestion until confirmed | qa-accessibility-auditor | Chromium | P1 | R8 |

## 3. Tooling
- Playwright Chromium installed in a scratch folder outside the repository (nothing added to `habitly/`). Default if you do not reply: this. Alternative: built-in browser pane only.
- No k6/JMeter/ZAP/axe install proposed. An axe scan would need an extra dependency (ask before adding): default is a manual + scripted DOM/contrast check, listing the scan as `Not Run`.

## 4. Open threshold questions
1. Render/toggle time limit: default 1000 ms for 50 habits x 3 years (Proposed).
2. Largest supported data volume: default as in NF-PERF-01.
3. Required browsers: default Chromium only.
4. WCAG level: default 2.2 AA.

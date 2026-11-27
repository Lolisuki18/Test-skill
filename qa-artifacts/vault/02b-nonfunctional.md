# Non-functional Test Design — Vault (`vault/`)

- **Phase:** Phase 2/5 — Non-functional Design
- **Date:** 2026-11-27
- **Version:** 1.0
- **Status:** Approved
- **Requirement source:** `qa-artifacts/vault/01-test-plan.md` (`Approved`)

---

## 1. Selected Attributes

- **Selected:** Performance (`NF-PERF`), Security Basics (`NF-SEC`), Accessibility (`NF-A11Y` — delegated to `03c-accessibility.md`).
- **Out of scope:** Compatibility (`NF-COMP` — no multi-browser matrix in spec; static minimal HTML), Usability/Localization (`NF-USA` — English-only minimal API/HTML).

---

## 2. Non-functional Cases

| NF ID | Attribute | Scenario | Metric & Threshold | Tool | Environment | Priority | Linked Requirement |
|---|---|---|---|---|---|---|---|
| NF-PERF-01 | Performance | 50 sequential `GET /api/items` requests against local `VaultHandler` | p50, p95, max latency in ms (`[Needs input: SLA]` — `Informational` baseline only) | Python `urllib` + `time.perf_counter` | Local `127.0.0.1` (`ThreadingHTTPServer`) | P2 | REQ-03 |
| NF-SEC-01 | Security Basics | Inspect HTTP security headers (`X-Content-Type-Options`, `X-Frame-Options`, `CSP`, `Cache-Control`) and 10 rapid failed logins | Presence of headers & `429` throttling (`Informational` — no security SLA in spec) | Python `urllib` | Local `127.0.0.1` (`ThreadingHTTPServer`) | P1 | REQ-02, REQ-07 |

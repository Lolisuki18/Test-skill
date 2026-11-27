# Defect Log — Vault (`vault/`)

- **Phase:** Phase 4/5 — Defect Management
- **Date:** 2026-11-27
- **Build / Commit:** `09a555a`

---

## Summary Table

| Defect ID | Title | Severity | Priority | Status | Related TC |
|---|---|---|---|---|---|
| DEF-001 | `[Items] POST /api/items coerces JSON null title to string "None" and returns 201` | Major | P1 (proposed) | New | TC-ITEM-004 |
| DEF-002 | `[UI] GET / bookmark list omits item URL from rendered HTML` | Major | P2 (proposed) | New | TC-UI-001 |
| DEF-003 | `[Accessibility] GET / HTML head omits viewport meta tag and skip link` | Minor | P2 (proposed) | New | TC-A11Y-001 |

---

## Defect Details

### DEF-001 — [Items] POST /api/items coerces JSON null title to string "None" and returns 201
| Field | Content |
|---|---|
| Title | `[Items] POST /api/items coerces JSON null title to string "None" and returns 201` |
| Related TC | `TC-ITEM-004` |
| Environment | Local Windows, `Python 3.14.6`, `ThreadingHTTPServer` (`127.0.0.1`), commit `09a555a` |
| Severity / Priority | **Major / P1 (proposed)** — Core validation bypassed for JSON `null` (`title: null` stored as `"None"`), no server-side workaround. |
| Status | `New` |
| Reproducibility | `Always (1/1)` |
| Pre-conditions | Authenticated user token (`bob`) |
| Steps to Reproduce | 1. Send `POST /api/items` with `Authorization: Bearer <bob_token>` and JSON body `{"title": null, "url": "https://example.test"}`. |
| Actual Result | HTTP `201` returned with `{"item": {"id": 3, "title": "None", "url": "https://example.test", "tag": "general", "status": "active", "owner_id": 2, "owner": "bob", ...}}`. |
| Expected Result | HTTP `400` validation error rejecting non-string / `null` `title` (source: approved default `01-test-plan.md` Q3 / `TC-ITEM-004`; expected behavior unconfirmed by formal spec, PO to confirm). |
| Evidence | `vault_qa_runner.py` -> `TC-ITEM-004`; code traced at `vault/server.py:174` (`title=str(data.get("title", ""))`). |
| Notes / Hypothesis (unconfirmed) | `str(None)` evaluates to `"None"` before `create_item()` checks `clean_title = title.strip()`. Same pattern affects `tag` (`vault/server.py:176`). |

### DEF-002 — [UI] GET / bookmark list omits item URL from rendered HTML
| Field | Content |
|---|---|
| Title | `[UI] GET / bookmark list omits item URL from rendered HTML` |
| Related TC | `TC-UI-001` |
| Environment | Local Windows, `Python 3.14.6`, `ThreadingHTTPServer` (`127.0.0.1`), commit `09a555a` |
| Severity / Priority | **Major / P2 (proposed)** — Main bookmark list page does not display or link to stored bookmark URLs (API `GET /api/items` works as workaround). |
| Status | `New` |
| Reproducibility | `Always (1/1)` |
| Pre-conditions | At least one bookmark item with a non-empty `url` (e.g. `https://xss.example.test`) exists in DB |
| Steps to Reproduce | 1. Create item with `url="https://xss.example.test"`. 2. Send `GET /`. |
| Actual Result | HTTP `200` HTML contains `title`, `tag`, and `status` (`<li><strong>...</strong> <span>[...]</span> <em>...</em></li>`), but `https://xss.example.test` is absent from HTML. |
| Expected Result | Rendered bookmark list displays/links the item's `url` safely (source: approved default `01-test-plan.md` Q2 / `TC-UI-001`; PO to confirm). |
| Evidence | `vault_qa_runner.py` -> `TC-UI-001` (`renders_url=False`); code traced at `vault/server.py:55-62`. |
| Notes / Hypothesis (unconfirmed) | `render_html` only interpolates `title`, `tag`, and `status`. |

### DEF-003 — [Accessibility] GET / HTML head omits viewport meta tag and skip link
| Field | Content |
|---|---|
| Title | `[Accessibility] GET / HTML head omits viewport meta tag and skip link` |
| Related TC | `TC-A11Y-001` |
| Environment | Code review of `vault/server.py:55-74`, commit `09a555a` |
| Severity / Priority | **Minor / P2 (proposed)** — Missing `<meta name="viewport">` (WCAG 1.4.10 Reflow) and skip link (WCAG 2.4.1). |
| Status | `New` |
| Reproducibility | `Always (1/1)` |
| Pre-conditions | None |
| Steps to Reproduce | 1. Inspect `render_html` in `vault/server.py:64-73` or `GET /` HTML output. |
| Actual Result | `<head><meta charset="utf-8"><title>Vault</title></head>` without viewport meta; `<body>` starts directly with `<header>`. |
| Expected Result | `<meta name="viewport" content="width=device-width, initial-scale=1">` in `<head>` and skip link to `#main-content` (source: spec WCAG 2.2 AA). |
| Evidence | `vault/server.py:66-69`, `03c-accessibility.md` (`A11Y-001`, `A11Y-002`). |
| Notes / Hypothesis (unconfirmed) | Minimal HTML template omitted mobile viewport and skip link. |

---

## Re-test History

| Defect ID | Round | Build | Result | Regression Checked |
|---|---|---|---|---|
| — | — | — | No re-tests yet | — |

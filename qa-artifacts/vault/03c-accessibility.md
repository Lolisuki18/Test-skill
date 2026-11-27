# Accessibility Audit — Vault (`vault/`)

- **Phase:** Phase 3/5 — Accessibility Audit (`qa-accessibility-auditor`)
- **Date:** 2026-11-27
- **Target Level:** WCAG 2.2 Level AA *(suggested default)*
- **Tools:** Static HTML/DOM code review (`vault/server.py:55-74`); no automated browser axe/Lighthouse scan or screen reader run in this environment.

---

## 1. Scope

- **Audited:** `GET /` server-rendered HTML (`render_html` in `vault/server.py:55-74`).
- **Not Run (requires live browser / assistive tech):** Keyboard walk-through, 200% zoom, color contrast computation, screen reader pass (NVDA/VoiceOver).

---

## 2. Findings Table

| ID | Page / Flow | Element or `file:line` | WCAG Criterion | Severity | Issue | Fix | Evidence |
|---|---|---|---|---|---|---|---|
| A11Y-001 | `GET /` (Bookmark list) | `vault/server.py:66` (`<head>`) | 1.4.10 Reflow (AA) | **Minor** | Missing `<meta name="viewport" content="width=device-width, initial-scale=1">`; mobile browsers may scale down desktop width instead of reflowing at 320 CSS px | Add `<meta name="viewport" content="width=device-width, initial-scale=1">` inside `<head>` | `vault/server.py:66`: `<head><meta charset="utf-8"><title>Vault</title></head>` |
| A11Y-002 | `GET /` (Bookmark list) | `vault/server.py:67-71` (`<body>`) | 2.4.1 Bypass Blocks (A) | **Minor** | No skip link (`<a href="#main-content">Skip to main content</a>`) before `<header>`, though `<header>` and `<main id="main-content">` landmarks are present | Add a skip link targeting `#main-content` as first focusable element in `<body>` | `vault/server.py:67-69` |

*(Logged in `04-defects.md` as `DEF-003`.)*

---

## 3. Coverage & Not-Run Checks

- **Verified in code (`vault/server.py:55-74`):**
  - `3.1.1 Language of Page`: `<html lang="en">` present (`L65`).
  - `2.4.2 Page Titled`: `<title>Vault</title>` present (`L66`).
  - `1.3.1 Info and Relationships`: `<header><h1>Vault Bookmark Manager</h1></header>`, `<main id="main-content"><ul><li>...</li></ul></main>` (`L68-70`).
- **Not Run:**
  - `2.1.1 Keyboard`, `2.4.7 Focus Visible`, `1.4.3 Contrast (Minimum)`, `1.4.4 Resize Text` (200% zoom), and screen-reader outline/announcements (`Not Run` — no browser/screen-reader session).

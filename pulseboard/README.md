# PulseBoard

Zero-dependency Python stdlib multi-actor issue tracker (`Users`, `Issues`, `Audit Log`) created inside `Test-skill` to exercise all 41+ non-course skills in the AI Workflow Suite.

## Quick start

```bash
python -m pulseboard --seed --port 8090
```

Seeded accounts:
- `admin` / `admin-pass-123` (role: `admin`)
- `alice` / `member-pass-123` (role: `member`)

## Endpoints & CLI

- `GET /` — HTML5 dashboard (`<html lang="en">`, `<main>`, `<label>`, `role="status"`)
- `GET /health` — DB & `schema_version` check
- `POST /api/auth/login` — HMAC-SHA256 bearer token
- `GET /api/issues?status=open` — list/filter issues
- `POST /api/issues` — create issue (authenticated)
- `PATCH /api/issues/<id>/status` — state machine (`open` -> `in_progress` -> `resolved` -> `closed`; `closed` requires `admin`)
- `DELETE /api/issues/<id>` — delete issue (`admin` only)
- `GET /api/admin/stats` — status & audit counts (`admin` only)
- `python -m pulseboard --db <path> --seed --migrate-only` — run SQL migrations (`pulseboard/migrations/001_init.sql`)

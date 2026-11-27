# Vault API Specification

Base URL (default local config): `http://127.0.0.1:8095` (`vault/__main__.py:13-14`, `vault/server.py:236`).

## Authentication & Authorization

- **Mechanism:** Bearer token (`Authorization: Bearer <token>`) signed with HMAC-SHA256 using `VAULT_SECRET` (`vault/server.py:32-52, 104-113`).
- **Token lifetime:** `3600` seconds (`ttl=3600` in `vault/server.py:32`).
- **Roles:** `admin`, `member` (`vault/migrations/001_init.sql:6`).
- **Request body limit:** `MAX_BODY_BYTES = 32768` (32 KiB) for JSON `POST` bodies (`vault/server.py:29, 97-98`).

## Common Error Shape

All JSON error responses return `Content-Type: application/json; charset=utf-8` with a single `error` string (`vault/server.py:84-90`):

```json
{
  "error": "authentication required"
}
```

| Status | Meaning | Example `error` values in code |
|---|---|---|
| `400` | Validation or malformed request | `"Invalid Content-Length"`, `"Body length must be 1..32768"`, `"JSON body must be an object"`, `"title must be 1..120 non-whitespace characters"`, `"url must start with http:// or https://"`, `"Invalid status: <val>"`, `"item is already archived"`, `"invalid item id"` |
| `401` | Missing, invalid, or expired auth | `"authentication required"`, `"invalid or expired token"`, `"invalid credentials"` |
| `403` | Insufficient role permissions | `"Only admin can view summary"`, `"Only admin can delete items"` |
| `404` | Resource or route not found | `"not found"` |

---

## Endpoint Summary

| Method | Path | Description | Auth | Request Body | Response Body | Source |
|---|---|---|---|---|---|---|
| `GET` | `/health` | Returns server health and SQLite schema version | Public | — | `HealthResponse` | `vault/server.py:117-121` |
| `GET` | `/` | Returns HTML list of all vault items | Public | — | HTML (`text/html`) | `vault/server.py:122-129` |
| `GET` | `/api/items` | Lists vault items with optional `tag` and `status` filters | Public | — | `ItemListResponse` | `vault/server.py:130-138` |
| `POST` | `/api/auth/login` | Authenticates user and issues bearer token | Public | `LoginRequest` | `LoginResponse` | `vault/server.py:154-165` |
| `POST` | `/api/items` | Creates a new active vault item | Bearer (`admin`, `member`) | `CreateItemRequest` | `ItemResponse` | `vault/server.py:166-183` |
| `PATCH` | `/api/items/{id}/archive` | Transitions an active item to `archived` | Bearer (`admin`, `member`) | — | `ItemResponse` | `vault/server.py:186-201` |
| `DELETE` | `/api/items/{id}` | Permanently deletes a vault item | Bearer (`admin`) | — | `DeleteResponse` | `vault/server.py:204-223` |
| `GET` | `/api/admin/summary` | Returns item counts grouped by status | Bearer (`admin`) | — | `SummaryResponse` | `vault/server.py:139-149` |

Total endpoints: **8** in doc = **8** in `vault/server.py:115-225`.

---

## Endpoints

### System & UI

#### GET /health

Returns service status and current SQLite `PRAGMA user_version` (`vault/server.py:117-121`).

- **Auth:** Public
- **Responses:**

| Status | Meaning | Body |
|---|---|---|
| `200` | Healthy | `{"status": "ok", "schema_version": 1}` |

#### GET /

Renders an HTML5 page listing all vault items ordered by `id DESC` (`vault/server.py:55-74, 122-129`, `vault/storage.py:97`).

- **Auth:** Public
- **Responses:**

| Status | Meaning | Body |
|---|---|---|
| `200` | HTML page | `Content-Type: text/html; charset=utf-8` |

---

### Authentication

#### POST /api/auth/login

Verifies username and PBKDF2-HMAC-SHA256 password hash and returns a signed bearer token (`vault/server.py:154-165`, `vault/storage.py:72-80`).

- **Auth:** Public
- **Request body:** `LoginRequest`

| Field | Type | Required | Constraints |
|---|---|---|---|
| `username` | string | yes | Trimmed before lookup (`vault/storage.py:76`) |
| `password` | string | yes | Verified against `password_hash` (`vault/storage.py:78`) |

**Example request**
```json
{
  "username": "bob",
  "password": "string"
}
```

**Responses**

| Status | Meaning | Body |
|---|---|---|
| `200` | Authenticated | `{"token": "<base64url>.<hmac_hex>", "user": {"id": 2, "username": "bob", "role": "member"}}` |
| `400` | Malformed JSON or body size out of `1..32768` | `{"error": "..."}` |
| `401` | Invalid username or password | `{"error": "invalid credentials"}` |

---

### Items

#### GET /api/items

Lists vault items ordered by `id DESC` (`vault/server.py:130-138`, `vault/storage.py:83-101`).

- **Auth:** Public
- **Query parameters:**

| Parameter | Type | Required | Constraints |
|---|---|---|---|
| `tag` | string | no | Trimmed and lowercased before exact match (`vault/storage.py:93`) |
| `status` | string | no | Must be `"active"` or `"archived"` (`vault/storage.py:15, 87-88`) |

**Responses**

| Status | Meaning | Body |
|---|---|---|
| `200` | Item list | `{"items": [{"id": 1, "title": "Docs", "url": "https://example.test", "tag": "ref", "status": "active", "owner_id": 2, "owner": "bob", "created_at": "2026-11-27T00:00:00Z"}]}` |
| `400` | Invalid `status` query value | `{"error": "Invalid status: <value>"}` |

#### POST /api/items

Creates a new `active` vault item owned by the authenticated user (`vault/server.py:166-183`, `vault/storage.py:104-123`).

- **Auth:** Bearer token, any role (`admin` or `member`) (`vault/server.py:167`)
- **Request body:** `CreateItemRequest`

| Field | Type | Required | Constraints |
|---|---|---|---|
| `title` | string | yes | Stripped length `1..120` chars (`vault/storage.py:105-107`) |
| `url` | string | no | Default `""`; if non-empty, must start with `http://` or `https://` (`vault/storage.py:108-110`) |
| `tag` | string | no | Default `"general"`; stripped, lowercased, truncated to `32` chars (`vault/storage.py:111`) |

**Example request**
```json
{
  "title": "API Reference",
  "url": "https://example.test/docs",
  "tag": "ref"
}
```

**Responses**

| Status | Meaning | Body |
|---|---|---|
| `201` | Created | `{"item": {"id": 1, "title": "API Reference", "url": "https://example.test/docs", "tag": "ref", "status": "active", "owner_id": 2, "owner": "bob", "created_at": "2026-11-27T00:00:00Z"}}` |
| `400` | Validation or JSON error | `{"error": "..."}` |
| `401` | Missing, invalid, or expired token | `{"error": "authentication required"}` / `{"error": "invalid or expired token"}` |

#### PATCH /api/items/{id}/archive

Marks an `active` item as `archived` (`vault/server.py:186-201`, `vault/storage.py:126-139`).

- **Auth:** Bearer token, any role (`admin` or `member`) (`vault/server.py:189`)
- **Path parameters:**

| Parameter | Type | Required | Constraints |
|---|---|---|---|
| `id` | integer | yes | Parsed with `int(parts[2])` (`vault/server.py:193`) |

**Responses**

| Status | Meaning | Body |
|---|---|---|
| `200` | Archived | `{"item": { ... "status": "archived" ... }}` |
| `400` | Item already archived or non-integer `id` | `{"error": "item is already archived"}` or `int()` parse error |
| `401` | Missing, invalid, or expired token | `{"error": "..."}` |
| `404` | Item not found | `{"error": "not found"}` |

#### DELETE /api/items/{id}

Deletes a vault item (`vault/server.py:204-223`, `vault/storage.py:142-147`).

- **Auth:** Bearer token, role `admin` (`vault/storage.py:143-144`)
- **Path parameters:**

| Parameter | Type | Required | Constraints |
|---|---|---|---|
| `id` | integer | yes | Parsed with `int(parts[2])` (`vault/server.py:211`) |

**Responses**

| Status | Meaning | Body |
|---|---|---|
| `200` | Deleted | `{"deleted": 1}` |
| `400` | Non-integer `id` | `{"error": "invalid item id"}` |
| `401` | Missing, invalid, or expired token | `{"error": "..."}` |
| `403` | Non-admin actor | `{"error": "Only admin can delete items"}` |
| `404` | Item not found | `{"error": "not found"}` |

---

### Admin

#### GET /api/admin/summary

Returns total item count and counts per status (`active`, `archived`) (`vault/server.py:139-149`, `vault/storage.py:150-158`).

- **Auth:** Bearer token, role `admin` (`vault/storage.py:151-152`)
- **Responses**

| Status | Meaning | Body |
|---|---|---|
| `200` | Summary | `{"by_status": {"active": 1, "archived": 0}, "total": 1}` |
| `401` | Missing, invalid, or expired token | `{"error": "..."}` |
| `403` | Non-admin actor | `{"error": "Only admin can view summary"}` |

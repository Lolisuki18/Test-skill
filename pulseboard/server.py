"""HTTP server, token auth, and accessible HTML UI for PulseBoard."""

from __future__ import annotations

import base64
from contextlib import closing
import hashlib
import hmac
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import time
from typing import Any
from urllib.parse import parse_qs, urlparse

from .storage import (
    apply_migrations,
    authenticate_user,
    create_issue,
    delete_issue,
    get_admin_stats,
    get_conn,
    list_issues,
    transition_issue,
)

MAX_BODY_BYTES = 64 * 1024
TOKEN_TTL_SECONDS = 3600


def sign_token(user: dict[str, Any], secret: str, ttl: int = TOKEN_TTL_SECONDS) -> str:
    """Create an HMAC-SHA256 signed bearer token."""
    payload = {
        "id": user["id"],
        "username": user["username"],
        "role": user["role"],
        "exp": int(time.time()) + ttl,
    }
    raw = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    sig = hmac.new(secret.encode("utf-8"), raw.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def verify_token(token: str, secret: str) -> dict[str, Any] | None:
    """Verify an HMAC-SHA256 bearer token and check expiration."""
    if "." not in token:
        return None
    raw, sig = token.split(".", 1)
    expected = hmac.new(secret.encode("utf-8"), raw.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(raw.encode("ascii")).decode("utf-8"))
    except (ValueError, json.JSONDecodeError):
        return None
    if int(payload.get("exp", 0)) < int(time.time()):
        return None
    return payload


def render_dashboard_html(issues: list[dict[str, Any]]) -> str:
    """Render an accessible HTML5 page listing current issues."""
    items = []
    for issue in issues:
        iid = int(issue["id"])
        title = html.escape(str(issue["title"]))
        status = html.escape(str(issue["status"]))
        prio = html.escape(str(issue["priority"]))
        author = html.escape(str(issue["author"]))
        items.append(
            f'<li data-issue-id="{iid}">'
            f"<strong>[{prio}] {title}</strong> "
            f'<span class="badge">{status}</span> '
            f'<span class="meta">by {author}</span>'
            f"</li>"
        )
    list_html = "\n".join(items) if items else "<li>No issues yet.</li>"
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>PulseBoard</title></head>\n'
        "<body>\n"
        '<a href="#main-content">Skip to main content</a>\n'
        "<header><h1>PulseBoard Issue Tracker</h1></header>\n"
        '<main id="main-content">\n'
        '<section aria-labelledby="login-heading">\n'
        '<h2 id="login-heading">Sign in</h2>\n'
        '<form id="login-form">\n'
        '<label for="username">Username</label>\n'
        '<input id="username" name="username" type="text" required>\n'
        '<label for="password">Password</label>\n'
        '<input id="password" name="password" type="password" required>\n'
        '<button type="submit">Sign in</button>\n'
        "</form>\n"
        "</section>\n"
        '<section aria-labelledby="issues-heading">\n'
        '<h2 id="issues-heading">Issues</h2>\n'
        '<div id="status-region" role="status" aria-live="polite"></div>\n'
        f"<ul>\n{list_html}\n</ul>\n"
        "</section>\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )


class PulseBoardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for PulseBoard API and HTML UI."""

    db_path: Path = Path("pulseboard.db")
    secret: str = os.environ.get("PULSEBOARD_SECRET", "dev-local-secret")

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, status: int, payload: Any) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> dict[str, Any]:
        raw_len = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_len)
        except ValueError as exc:
            raise ValueError("Invalid Content-Length") from exc
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValueError(f"Body length must be 1..{MAX_BODY_BYTES} bytes")
        raw = self.rfile.read(length)
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def _require_auth(self) -> dict[str, Any] | None:
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            self._send_json(401, {"error": "authentication required"})
            return None
        user = verify_token(auth[7:].strip(), self.secret)
        if user is None:
            self._send_json(401, {"error": "invalid or expired token"})
            return None
        return user

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            with closing(get_conn(self.db_path)) as conn:
                ver = conn.execute("PRAGMA user_version").fetchone()[0]
            self._send_json(200, {"status": "ok", "db": "connected", "schema_version": ver})
            return
        if parsed.path == "/":
            body = render_dashboard_html(list_issues(self.db_path)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/issues":
            qs = parse_qs(parsed.query)
            status_filter = qs.get("status", [None])[0]
            try:
                issues = list_issues(self.db_path, status=status_filter)
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, {"issues": issues})
            return
        if parsed.path == "/api/admin/stats":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                stats = get_admin_stats(self.db_path, actor)
            except PermissionError as exc:
                self._send_json(403, {"error": str(exc)})
                return
            self._send_json(200, stats)
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/auth/login":
            try:
                data = self._read_json()
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": str(exc)})
                return
            user = authenticate_user(
                self.db_path,
                str(data.get("username", "")),
                str(data.get("password", "")),
            )
            if user is None:
                self._send_json(401, {"error": "invalid credentials"})
                return
            self._send_json(200, {"token": sign_token(user, self.secret), "user": user})
            return
        if parsed.path == "/api/issues":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                data = self._read_json()
                issue = create_issue(
                    self.db_path,
                    title=str(data.get("title", "")),
                    description=str(data.get("description", "")),
                    priority=str(data.get("priority", "P2")),
                    author_id=int(actor["id"]),
                )
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(201, {"issue": issue})
            return
        self._send_json(404, {"error": "not found"})

    def do_PATCH(self) -> None:
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "issues" and parts[3] == "status":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                issue_id = int(parts[2])
                data = self._read_json()
                updated = transition_issue(
                    self.db_path,
                    issue_id=issue_id,
                    new_status=str(data.get("status", "")),
                    actor=actor,
                )
            except PermissionError as exc:
                self._send_json(403, {"error": str(exc)})
                return
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": str(exc)})
                return
            if updated is None:
                self._send_json(404, {"error": "not found"})
                return
            self._send_json(200, {"issue": updated})
            return
        self._send_json(404, {"error": "not found"})

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "issues":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                issue_id = int(parts[2])
                deleted = delete_issue(self.db_path, issue_id=issue_id, actor=actor)
            except PermissionError as exc:
                self._send_json(403, {"error": str(exc)})
                return
            except ValueError:
                self._send_json(400, {"error": "invalid issue id"})
                return
            if not deleted:
                self._send_json(404, {"error": "not found"})
                return
            self._send_json(200, {"deleted": issue_id})
            return
        self._send_json(404, {"error": "not found"})


def make_handler(db_path: str | Path, secret: str) -> type[PulseBoardHandler]:
    """Create a request handler class bound to a specific DB path and secret."""

    class BoundHandler(PulseBoardHandler):
        pass

    BoundHandler.db_path = Path(db_path)
    BoundHandler.secret = secret
    return BoundHandler


def run_server(
    host: str = "127.0.0.1",
    port: int = 8090,
    db_path: str | Path = "pulseboard.db",
    secret: str | None = None,
) -> None:
    """Apply migrations and start the PulseBoard HTTP server."""
    apply_migrations(db_path)
    used_secret = secret or os.environ.get("PULSEBOARD_SECRET", "dev-local-secret")
    server = ThreadingHTTPServer((host, port), make_handler(db_path, used_secret))
    server.serve_forever()

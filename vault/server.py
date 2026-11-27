"""HTTP server and accessible HTML UI for Vault."""

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
    archive_item,
    authenticate,
    create_item,
    delete_item,
    get_conn,
    get_summary,
    list_items,
)

MAX_BODY_BYTES = 32 * 1024


def sign_token(user: dict[str, Any], secret: str, ttl: int = 3600) -> str:
    payload = {"id": user["id"], "username": user["username"], "role": user["role"], "exp": int(time.time()) + ttl}
    raw = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("ascii")
    sig = hmac.new(secret.encode("utf-8"), raw.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def verify_token(token: str, secret: str) -> dict[str, Any] | None:
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


def render_html(items: list[dict[str, Any]]) -> str:
    rows = []
    for it in items:
        title = html.escape(str(it["title"]))
        tag = html.escape(str(it["tag"]))
        status = html.escape(str(it["status"]))
        rows.append(f'<li><strong>{title}</strong> <span>[{tag}]</span> <em>{status}</em></li>')
    body_list = "\n".join(rows) if rows else "<li>No items yet.</li>"
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>Vault</title></head>\n'
        "<body>\n"
        "<header><h1>Vault Bookmark Manager</h1></header>\n"
        '<main id="main-content">\n'
        f"<ul>\n{body_list}\n</ul>\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )


class VaultHandler(BaseHTTPRequestHandler):
    db_path: Path = Path("vault.db")
    secret: str = ""

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
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as exc:
            raise ValueError("Invalid Content-Length") from exc
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ValueError(f"Body length must be 1..{MAX_BODY_BYTES}")
        data = json.loads(self.rfile.read(length).decode("utf-8"))
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
            self._send_json(200, {"status": "ok", "schema_version": ver})
            return
        if parsed.path == "/":
            body = render_html(list_items(self.db_path)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if parsed.path == "/api/items":
            qs = parse_qs(parsed.query)
            try:
                items = list_items(self.db_path, tag=qs.get("tag", [None])[0], status=qs.get("status", [None])[0])
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(200, {"items": items})
            return
        if parsed.path == "/api/admin/summary":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                summary = get_summary(self.db_path, actor)
            except PermissionError as exc:
                self._send_json(403, {"error": str(exc)})
                return
            self._send_json(200, summary)
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
            user = authenticate(self.db_path, str(data.get("username", "")), str(data.get("password", "")))
            if user is None:
                self._send_json(401, {"error": "invalid credentials"})
                return
            self._send_json(200, {"token": sign_token(user, self.secret), "user": user})
            return
        if parsed.path == "/api/items":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                data = self._read_json()
                item = create_item(
                    self.db_path,
                    title=str(data.get("title", "")),
                    url=str(data.get("url", "")),
                    tag=str(data.get("tag", "general")),
                    owner_id=int(actor["id"]),
                )
            except (ValueError, json.JSONDecodeError) as exc:
                self._send_json(400, {"error": str(exc)})
                return
            self._send_json(201, {"item": item})
            return
        self._send_json(404, {"error": "not found"})

    def do_PATCH(self) -> None:
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) == 4 and parts[0] == "api" and parts[1] == "items" and parts[3] == "archive":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                updated = archive_item(self.db_path, int(parts[2]))
            except ValueError as exc:
                self._send_json(400, {"error": str(exc)})
                return
            if updated is None:
                self._send_json(404, {"error": "not found"})
                return
            self._send_json(200, {"item": updated})
            return
        self._send_json(404, {"error": "not found"})

    def do_DELETE(self) -> None:
        parts = urlparse(self.path).path.strip("/").split("/")
        if len(parts) == 3 and parts[0] == "api" and parts[1] == "items":
            actor = self._require_auth()
            if actor is None:
                return
            try:
                item_id = int(parts[2])
                deleted = delete_item(self.db_path, item_id, actor)
            except PermissionError as exc:
                self._send_json(403, {"error": str(exc)})
                return
            except ValueError:
                self._send_json(400, {"error": "invalid item id"})
                return
            if not deleted:
                self._send_json(404, {"error": "not found"})
                return
            self._send_json(200, {"deleted": item_id})
            return
        self._send_json(404, {"error": "not found"})


def make_handler(db_path: str | Path, secret: str) -> type[VaultHandler]:
    class BoundHandler(VaultHandler):
        pass

    BoundHandler.db_path = Path(db_path)
    BoundHandler.secret = secret
    return BoundHandler


def run_server(host: str = "127.0.0.1", port: int = 8095, db_path: str | Path = "vault.db", secret: str | None = None) -> None:
    apply_migrations(db_path)
    used_secret = secret or os.environ.get("VAULT_SECRET")
    if not used_secret:
        raise RuntimeError("VAULT_SECRET environment variable must be set")
    ThreadingHTTPServer((host, port), make_handler(db_path, used_secret)).serve_forever()

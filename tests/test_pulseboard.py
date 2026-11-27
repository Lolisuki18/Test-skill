"""Unit and HTTP integration tests for PulseBoard."""

from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from pulseboard.server import make_handler
from pulseboard.storage import (
    apply_migrations,
    authenticate_user,
    create_issue,
    list_issues,
    seed_default_users,
    transition_issue,
)


class PulseBoardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "pulseboard.db"
        self.secret = "test-secret-key"
        apply_migrations(self.db_path)
        seed_default_users(self.db_path)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.db_path, self.secret))
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmpdir.cleanup()

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, object] | None = None,
        token: str | None = None,
    ) -> tuple[int, dict[str, object] | str]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers: dict[str, str] = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = f"Bearer {token}"
        req = Request(f"http://127.0.0.1:{self.port}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
                ct = resp.headers.get("Content-Type", "")
                return resp.status, json.loads(raw) if "application/json" in ct else raw
        except HTTPError as err:
            with err:
                raw = err.read().decode("utf-8")
                return err.code, json.loads(raw)

    def _login(self, username: str, password: str) -> str:
        status, payload = self._request("POST", "/api/auth/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        assert isinstance(payload, dict)
        return str(payload["token"])

    def test_migration_is_idempotent(self) -> None:
        self.assertEqual(apply_migrations(self.db_path), 1)
        self.assertEqual(apply_migrations(self.db_path), 1)

    def test_health_and_html_ui(self) -> None:
        status, health = self._request("GET", "/health")
        self.assertEqual(status, 200)
        assert isinstance(health, dict)
        self.assertEqual(health["schema_version"], 1)

        html_status, page = self._request("GET", "/")
        self.assertEqual(html_status, 200)
        assert isinstance(page, str)
        self.assertIn('<html lang="en">', page)
        self.assertIn('<main id="main-content">', page)
        self.assertIn('<label for="username">', page)

    def test_auth_rbac_and_lifecycle_transitions(self) -> None:
        # Anonymous cannot create issue or view admin stats
        s_unauth, _ = self._request("POST", "/api/issues", {"title": "Anon", "priority": "P1"})
        self.assertEqual(s_unauth, 401)
        s_stats_anon, _ = self._request("GET", "/api/admin/stats")
        self.assertEqual(s_stats_anon, 401)

        member_tok = self._login("alice", "member-pass-123")
        admin_tok = self._login("admin", "admin-pass-123")

        # Member cannot access admin stats
        s_stats_mem, _ = self._request("GET", "/api/admin/stats", token=member_tok)
        self.assertEqual(s_stats_mem, 403)

        # Member creates issue (including HTML characters to verify escaping on GET /)
        s_create, created = self._request(
            "POST",
            "/api/issues",
            {"title": "<script>alert(1)</script>", "description": "desc", "priority": "P0"},
            token=member_tok,
        )
        self.assertEqual(s_create, 201)
        assert isinstance(created, dict)
        issue = created["issue"]
        assert isinstance(issue, dict)
        issue_id = int(issue["id"])

        # Verify XSS escaping in HTML UI
        _, html_page = self._request("GET", "/")
        assert isinstance(html_page, str)
        self.assertNotIn("<script>alert(1)</script>", html_page)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html_page)

        # Member transitions open -> in_progress -> resolved
        s1, _ = self._request("PATCH", f"/api/issues/{issue_id}/status", {"status": "in_progress"}, token=member_tok)
        self.assertEqual(s1, 200)
        s2, _ = self._request("PATCH", f"/api/issues/{issue_id}/status", {"status": "resolved"}, token=member_tok)
        self.assertEqual(s2, 200)

        # Member cannot close or delete; Admin can
        s_close_mem, _ = self._request("PATCH", f"/api/issues/{issue_id}/status", {"status": "closed"}, token=member_tok)
        self.assertEqual(s_close_mem, 403)
        s_del_mem, _ = self._request("DELETE", f"/api/issues/{issue_id}", token=member_tok)
        self.assertEqual(s_del_mem, 403)

        s_close_adm, _ = self._request("PATCH", f"/api/issues/{issue_id}/status", {"status": "closed"}, token=admin_tok)
        self.assertEqual(s_close_adm, 200)
        s_stats_adm, stats = self._request("GET", "/api/admin/stats", token=admin_tok)
        self.assertEqual(s_stats_adm, 200)
        assert isinstance(stats, dict)
        self.assertEqual(stats["total_issues"], 1)

        s_del_adm, _ = self._request("DELETE", f"/api/issues/{issue_id}", token=admin_tok)
        self.assertEqual(s_del_adm, 200)

    def test_invalid_inputs_and_transitions(self) -> None:
        alice = authenticate_user(self.db_path, "alice", "member-pass-123")
        assert alice is not None
        with self.assertRaises(ValueError):
            create_issue(self.db_path, "   ", "", "P1", alice["id"])
        issue = create_issue(self.db_path, "Valid", "", "P2", alice["id"])
        with self.assertRaises(ValueError):
            transition_issue(self.db_path, issue["id"], "closed", {"id": alice["id"], "role": "admin"})
        self.assertEqual(len(list_issues(self.db_path, status="open")), 1)

    def test_cli_migrate_only(self) -> None:
        cli_db = Path(self.tmpdir.name) / "cli.db"
        proc = subprocess.run(
            [sys.executable, "-m", "pulseboard", "--db", str(cli_db), "--seed", "--migrate-only"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("schema_version=1", proc.stdout)

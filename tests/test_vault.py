"""Unit and HTTP integration tests for Vault."""

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

from vault.server import make_handler
from vault.storage import apply_migrations, create_item, seed_users


class VaultTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmpdir.name) / "vault.db"
        apply_migrations(self.db_path)
        seed_users(self.db_path)
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(self.db_path, "vault-test-secret"))
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmpdir.cleanup()

    def _req(self, method: str, path: str, body: dict[str, object] | None = None, token: str | None = None) -> tuple[int, dict[str, object] | str]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {"Content-Type": "application/json"} if data is not None else {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = Request(f"http://127.0.0.1:{self.port}{path}", data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=5) as resp:
                raw = resp.read().decode("utf-8")
                return resp.status, json.loads(raw) if "application/json" in resp.headers.get("Content-Type", "") else raw
        except HTTPError as err:
            with err:
                return err.code, json.loads(err.read().decode("utf-8"))

    def _login(self, username: str, password: str) -> str:
        status, payload = self._req("POST", "/api/auth/login", {"username": username, "password": password})
        self.assertEqual(status, 200)
        assert isinstance(payload, dict)
        return str(payload["token"])

    def test_health_ui_and_rbac_flow(self) -> None:
        s_health, health = self._req("GET", "/health")
        self.assertEqual(s_health, 200)
        assert isinstance(health, dict)
        self.assertEqual(health["schema_version"], 1)

        bob_tok = self._login("bob", "vault-member-123")
        adm_tok = self._login("admin", "vault-admin-123")

        s_create, created = self._req(
            "POST",
            "/api/items",
            {"title": "<b>Docs</b>", "url": "https://example.test", "tag": "ref"},
            token=bob_tok,
        )
        self.assertEqual(s_create, 201)
        assert isinstance(created, dict)
        item_id = int(created["item"]["id"])

        _, html_page = self._req("GET", "/")
        assert isinstance(html_page, str)
        self.assertIn("&lt;b&gt;Docs&lt;/b&gt;", html_page)

        s_arch, _ = self._req("PATCH", f"/api/items/{item_id}/archive", token=bob_tok)
        self.assertEqual(s_arch, 200)
        s_arch_again, _ = self._req("PATCH", f"/api/items/{item_id}/archive", token=bob_tok)
        self.assertEqual(s_arch_again, 400)

        s_del_mem, _ = self._req("DELETE", f"/api/items/{item_id}", token=bob_tok)
        self.assertEqual(s_del_mem, 403)
        s_sum_adm, summary = self._req("GET", "/api/admin/summary", token=adm_tok)
        self.assertEqual(s_sum_adm, 200)
        assert isinstance(summary, dict)
        self.assertEqual(summary["total"], 1)
        s_del_adm, _ = self._req("DELETE", f"/api/items/{item_id}", token=adm_tok)
        self.assertEqual(s_del_adm, 200)

    def test_validation_and_cli(self) -> None:
        with self.assertRaises(ValueError):
            create_item(self.db_path, "Bad URL", "ftp://example.test", "t", 1)
        cli_db = Path(self.tmpdir.name) / "cli.db"
        proc = subprocess.run(
            [sys.executable, "-m", "vault", "--db", str(cli_db), "--seed", "--migrate-only"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("schema_version=1", proc.stdout)

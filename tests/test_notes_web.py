import json
import os
import tempfile
import threading
import unittest
from http.server import HTTPServer
from urllib.request import Request, urlopen

from notes_web.app import NotesHandler, create_note, delete_note, init_db, list_notes


class NotesWebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.tmp.close()
        init_db(self.tmp.name)

    def tearDown(self) -> None:
        os.unlink(self.tmp.name)

    def test_crud(self) -> None:
        n = create_note("Hello", "World", self.tmp.name)
        self.assertEqual(n["title"], "Hello")
        self.assertEqual(len(list_notes(self.tmp.name)), 1)
        self.assertTrue(delete_note(n["id"], self.tmp.name))
        self.assertEqual(len(list_notes(self.tmp.name)), 0)

    def test_http_health_and_notes(self) -> None:
        NotesHandler.db_path = self.tmp.name
        srv = HTTPServer(("127.0.0.1", 0), NotesHandler)
        port = srv.server_address[1]
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            with urlopen(f"http://127.0.0.1:{port}/health") as r:
                self.assertEqual(r.status, 200)
                self.assertEqual(json.loads(r.read())["status"], "ok")
            req = Request(
                f"http://127.0.0.1:{port}/api/notes",
                data=json.dumps({"title": "API", "body": "Test"}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req) as r:
                self.assertEqual(r.status, 201)
        finally:
            srv.shutdown()
            srv.server_close()

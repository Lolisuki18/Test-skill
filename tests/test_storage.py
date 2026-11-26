import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from taskbox import storage
from taskbox.models import Task
from taskbox.storage import StorageError, load_tasks, resolve_path, save_tasks


class StorageTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.path = self.dir / "tasks.json"


class RoundTripTests(StorageTestCase):
    def test_S1_save_then_load_round_trips(self):  # R6 happy
        tasks = [
            Task(id=1, title="Mua sữa", priority="high", due="2026-12-01"),
            Task(id=3, title="done one", status="done"),
        ]
        save_tasks(self.path, tasks, 4)
        loaded, next_id = load_tasks(self.path)
        self.assertEqual(loaded, tasks)
        self.assertEqual(next_id, 4)

    def test_S1_file_is_utf8_without_ascii_escapes(self):  # R6 boundary
        save_tasks(self.path, [Task(id=1, title="sữa")], 2)
        self.assertIn("sữa", self.path.read_text(encoding="utf-8"))

    def test_S2_missing_file_is_empty_store(self):  # R6 boundary
        self.assertEqual(load_tasks(self.path), ([], 1))

    def test_S2_empty_file_is_empty_store(self):  # R6 boundary
        self.path.write_text("  \n", encoding="utf-8")
        self.assertEqual(load_tasks(self.path), ([], 1))

    def test_S2_save_creates_missing_parent_dirs(self):  # R6 boundary
        nested = self.dir / "a" / "b" / "tasks.json"
        save_tasks(nested, [], 1)
        self.assertTrue(nested.is_file())

    def test_S2_next_id_never_below_highest_id_plus_one(self):  # R4 boundary
        save_tasks(self.path, [Task(id=5, title="x")], 2)  # stale next_id
        _, next_id = load_tasks(self.path)
        self.assertEqual(next_id, 6)


class CorruptFileTests(StorageTestCase):
    def assert_rejected_and_untouched(self, content, pattern):
        self.path.write_text(content, encoding="utf-8")
        with self.assertRaisesRegex(StorageError, pattern):
            load_tasks(self.path)
        self.assertEqual(self.path.read_text(encoding="utf-8"), content)

    def test_S3_corrupt_json(self):  # R6 negative
        self.assert_rejected_and_untouched("{bad", "not valid JSON")

    def test_S3_unknown_version(self):  # R6 negative
        self.assert_rejected_and_untouched(
            json.dumps({"version": 99, "next_id": 1, "tasks": []}), "unsupported format or version"
        )

    def test_S3_top_level_not_object(self):  # R6 negative
        self.assert_rejected_and_untouched("[]", "unsupported format or version")

    def test_S3_tasks_not_a_list(self):  # R6 negative
        self.assert_rejected_and_untouched(
            json.dumps({"version": 1, "next_id": 1, "tasks": {}}), "malformed structure"
        )

    def test_S3_invalid_task_entry(self):  # R6 negative
        bad = {"version": 1, "next_id": 2, "tasks": [{"id": 1, "title": "", "priority": "low", "due": None, "status": "todo"}]}
        self.assert_rejected_and_untouched(json.dumps(bad), "invalid task")


    def test_S3_non_utf8_bytes_raise_storage_error(self):  # R6 negative
        content = "{}".encode("utf-16")  # e.g. a file produced by PowerShell `>`
        self.path.write_bytes(content)
        with self.assertRaisesRegex(StorageError, "not valid UTF-8"):
            load_tasks(self.path)
        self.assertEqual(self.path.read_bytes(), content)

    def test_S3_utf8_bom_is_rejected_with_storage_error(self):  # R6 boundary
        body = json.dumps({"version": 1, "next_id": 1, "tasks": []})
        self.path.write_bytes(body.encode("utf-8-sig"))
        with self.assertRaisesRegex(StorageError, "not valid JSON"):
            load_tasks(self.path)

    def test_S3_deeply_nested_json_raises_storage_error(self):  # R6 negative
        self.assert_rejected_and_untouched("[" * 200000, "not valid JSON")


class ResolvePathTests(unittest.TestCase):
    def test_S4_cli_arg_wins_over_env(self):  # R6 happy
        with mock.patch.dict(os.environ, {storage.ENV_VAR: "/env/tasks.json"}):
            self.assertEqual(resolve_path("/cli/t.json"), Path("/cli/t.json"))

    def test_S4_env_used_when_no_arg(self):  # R6 happy
        with mock.patch.dict(os.environ, {storage.ENV_VAR: "/env/tasks.json"}):
            self.assertEqual(resolve_path(None), Path("/env/tasks.json"))

    def test_S4_default_is_home_taskbox(self):  # R6 boundary
        env = {k: v for k, v in os.environ.items() if k != storage.ENV_VAR}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(resolve_path(None), Path.home() / ".taskbox" / "tasks.json")


class AtomicWriteTests(StorageTestCase):
    def test_S5_failed_replace_keeps_old_file_and_cleans_temp(self):  # R6 negative
        save_tasks(self.path, [Task(id=1, title="old")], 2)
        before = self.path.read_text(encoding="utf-8")
        with mock.patch("taskbox.storage.os.replace", side_effect=OSError("locked")):
            with self.assertRaisesRegex(StorageError, "cannot write"):
                save_tasks(self.path, [Task(id=1, title="new")], 2)
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)
        self.assertEqual([p.name for p in self.dir.iterdir()], ["tasks.json"])


if __name__ == "__main__":
    unittest.main()

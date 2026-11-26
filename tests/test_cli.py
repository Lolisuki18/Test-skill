import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from taskbox.cli import main


class CliTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "tasks.json"

    def run_cli(self, *argv):
        """Run main() with --file pointing at the temp store; return (code, stdout, stderr)."""
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main(["--file", str(self.path), *argv])
            except SystemExit as exc:  # argparse errors exit with 2
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def stored(self):
        return json.loads(self.path.read_text(encoding="utf-8"))["tasks"]

    def seed(self):
        self.run_cli("add", "A low todo", "--priority", "low", "--due", "2026-12-05")
        self.run_cli("add", "B high done", "--priority", "high", "--due", "2026-12-01")
        self.run_cli("add", "C med nodue")
        self.run_cli("add", "D high todo", "--priority", "high", "--due", "2026-12-03")
        self.run_cli("done", "2")

    def listed_ids(self, *argv):
        _, out, _ = self.run_cli("list", *argv)
        return [int(line.split()[0]) for line in out.splitlines()[1:]]


class AddTests(CliTestCase):
    def test_C1_add_defaults(self):  # R1 happy
        code, out, _ = self.run_cli("add", "Buy milk")
        self.assertEqual(code, 0)
        self.assertIn("Added task 1: Buy milk", out)
        self.assertEqual(
            self.stored(),
            [{"id": 1, "title": "Buy milk", "priority": "med", "due": None, "status": "todo"}],
        )

    def test_C1_add_with_priority_and_due(self):  # R1 happy
        self.run_cli("add", "Report", "--priority", "high", "--due", "2026-12-01")
        task = self.stored()[0]
        self.assertEqual((task["priority"], task["due"]), ("high", "2026-12-01"))

    def test_C2_ids_increment(self):  # R1 boundary
        self.run_cli("add", "one")
        self.run_cli("add", "two")
        self.assertEqual([t["id"] for t in self.stored()], [1, 2])

    def test_C2_unicode_and_200_char_title(self):  # R1 boundary
        self.assertEqual(self.run_cli("add", "Mua sữa")[0], 0)
        self.assertEqual(self.run_cli("add", "x" * 200)[0], 0)
        self.assertEqual(self.stored()[0]["title"], "Mua sữa")

    def test_C3_rejects_bad_input_and_leaves_file_unchanged(self):  # R1/R5 negative
        self.run_cli("add", "keep me")
        before = self.path.read_text(encoding="utf-8")
        cases = [
            (("add", "   "), 1, "must not be empty"),
            (("add", "x" * 201), 1, "at most 200"),
            (("add", "x", "--due", "2026-02-30"), 1, "not a real calendar date"),
            (("add", "x", "--due", "soon"), 1, "YYYY-MM-DD"),
            (("add", "x", "--priority", "urgent"), 2, "invalid choice"),
        ]
        for argv, expected_code, message in cases:
            with self.subTest(argv=argv):
                code, _, err = self.run_cli(*argv)
                self.assertEqual(code, expected_code)
                self.assertIn(message, err)
                self.assertEqual(self.path.read_text(encoding="utf-8"), before)


class ListTests(CliTestCase):
    def test_C4_list_all_in_id_order(self):  # R2 happy
        self.seed()
        self.assertEqual(self.listed_ids(), [1, 2, 3, 4])

    def test_C4_filter_by_status(self):  # R2 happy
        self.seed()
        self.assertEqual(self.listed_ids("--status", "done"), [2])
        self.assertEqual(self.listed_ids("--status", "todo"), [1, 3, 4])

    def test_C4_filter_by_priority(self):  # R2 happy
        self.seed()
        self.assertEqual(self.listed_ids("--priority", "high"), [2, 4])

    def test_C4_filters_combine_with_and(self):  # R2 happy
        self.seed()
        self.assertEqual(self.listed_ids("--status", "todo", "--priority", "high"), [4])

    def test_C4_sort_by_due_puts_undated_last(self):  # R2 boundary
        self.seed()
        self.assertEqual(self.listed_ids("--sort", "due"), [2, 4, 1, 3])

    def test_C4_sort_and_filter_together(self):  # R2 happy
        self.seed()
        self.assertEqual(self.listed_ids("--status", "todo", "--sort", "due"), [4, 1, 3])

    def test_C5_empty_store(self):  # R2 boundary
        code, out, _ = self.run_cli("list")
        self.assertEqual((code, out.strip()), (0, "No tasks."))

    def test_C5_filter_matching_nothing(self):  # R2 boundary
        self.run_cli("add", "x")
        code, out, _ = self.run_cli("list", "--status", "done")
        self.assertEqual((code, out.strip()), (0, "No tasks."))

    def test_C6_invalid_filter_values_exit_2(self):  # R2 negative
        for argv in (("--status", "foo"), ("--priority", "urgent"), ("--sort", "title")):
            with self.subTest(argv=argv):
                code, _, err = self.run_cli("list", *argv)
                self.assertEqual(code, 2)
                self.assertIn("invalid choice", err)


class DoneTests(CliTestCase):
    def test_C7_done_persists(self):  # R3 happy
        self.run_cli("add", "x")
        code, out, _ = self.run_cli("done", "1")
        self.assertEqual(code, 0)
        self.assertIn("Task 1 marked done.", out)
        self.assertEqual(self.stored()[0]["status"], "done")

    def test_C7_done_twice_is_idempotent(self):  # R3 boundary
        self.run_cli("add", "x")
        self.run_cli("done", "1")
        code, out, _ = self.run_cli("done", "1")
        self.assertEqual(code, 0)
        self.assertIn("already done", out)

    def test_C8_unknown_id_exit_1_and_file_unchanged(self):  # R3 negative
        self.run_cli("add", "x")
        before = self.path.read_text(encoding="utf-8")
        code, _, err = self.run_cli("done", "99")
        self.assertEqual(code, 1)
        self.assertIn("no task with id 99", err)
        self.assertEqual(self.path.read_text(encoding="utf-8"), before)

    def test_C8_non_integer_id_exit_2(self):  # R3 negative
        code, _, err = self.run_cli("done", "abc")
        self.assertEqual(code, 2)
        self.assertIn("invalid int value", err)


class DeleteTests(CliTestCase):
    def test_C9_delete_removes_only_that_task(self):  # R4 happy
        self.run_cli("add", "one")
        self.run_cli("add", "two")
        code, out, _ = self.run_cli("delete", "1")
        self.assertEqual(code, 0)
        self.assertIn("Deleted task 1.", out)
        self.assertEqual([t["title"] for t in self.stored()], ["two"])

    def test_C9_ids_are_not_reused_after_delete(self):  # R4 boundary
        self.run_cli("add", "one")
        self.run_cli("add", "two")
        self.run_cli("delete", "2")
        self.run_cli("add", "three")
        self.assertEqual([t["id"] for t in self.stored()], [1, 3])

    def test_C10_unknown_id_exit_1(self):  # R4 negative
        code, _, err = self.run_cli("delete", "5")
        self.assertEqual(code, 1)
        self.assertIn("no task with id 5", err)

    def test_C10_delete_same_id_twice_fails_second_time(self):  # R4 negative
        self.run_cli("add", "one")
        self.run_cli("delete", "1")
        self.assertEqual(self.run_cli("delete", "1")[0], 1)

    def test_C10_non_integer_id_exit_2(self):  # R4 negative
        self.assertEqual(self.run_cli("delete", "x")[0], 2)


class CorruptStoreTests(CliTestCase):
    def test_C11_corrupt_file_reports_error_and_is_not_overwritten(self):  # R6 negative
        self.path.write_text("{bad", encoding="utf-8")
        for argv in (("list",), ("add", "x"), ("done", "1"), ("delete", "1")):
            with self.subTest(argv=argv):
                code, _, err = self.run_cli(*argv)
                self.assertEqual(code, 1)
                self.assertIn("not valid JSON", err)
                self.assertEqual(self.path.read_text(encoding="utf-8"), "{bad")

    def test_C12_non_utf8_file_reports_error_without_traceback(self):  # R6 negative
        content = "[]".encode("utf-16")
        self.path.write_bytes(content)
        for argv in (("list",), ("add", "x"), ("done", "1"), ("delete", "1")):
            with self.subTest(argv=argv):
                code, _, err = self.run_cli(*argv)
                self.assertEqual(code, 1)
                self.assertIn("not valid UTF-8", err)
                self.assertEqual(self.path.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()

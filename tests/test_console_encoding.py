import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class NarrowConsoleTests(unittest.TestCase):
    """DEF-001: real subprocess whose stdout/stderr use cp1252 (StringIO has no code page)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "tasks.json"

    def run_cli(self, *argv):
        env = dict(os.environ, PYTHONIOENCODING="cp1252", TASKBOX_FILE=str(self.path))
        env.pop("PYTHONUTF8", None)
        proc = subprocess.run(
            [sys.executable, "-m", "taskbox", *argv],
            cwd=str(ROOT), env=env, capture_output=True,
        )
        return proc.returncode, proc.stdout.decode("cp1252"), proc.stderr.decode("cp1252")

    def test_R1_add_with_emoji_does_not_crash(self):  # R1 boundary
        code, out, err = self.run_cli("add", "Buy coffee ☕")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Added task 1: Buy coffee ", out)

    def test_R2_list_with_emoji_does_not_crash(self):  # R2 boundary
        self.run_cli("add", "Buy coffee ☕")
        code, out, err = self.run_cli("list")
        self.assertEqual((code, err), (0, ""))
        self.assertIn("Buy coffee ", out)
        self.assertNotIn("Traceback", err)

    def test_R1_printable_cp1252_text_is_unchanged(self):  # R1 happy
        code, out, _ = self.run_cli("add", "Café")
        self.assertEqual(code, 0)
        self.assertIn("Added task 1: Café", out)

    def test_R5_error_message_with_emoji_goes_to_stderr(self):  # R5 negative
        code, _, err = self.run_cli("--file", str(self.path), "add", "x", "--due", "☕")
        self.assertEqual(code, 1)
        self.assertIn("error:", err)

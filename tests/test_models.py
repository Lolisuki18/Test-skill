import unittest

from taskbox.models import (
    Task,
    ValidationError,
    due_sort_key,
    validate_due,
    validate_priority,
    validate_title,
)


class ValidateTitleTests(unittest.TestCase):
    def test_M1_accepts_normal_title(self):  # R5 happy
        self.assertEqual(validate_title("Buy milk"), "Buy milk")

    def test_M2_trims_whitespace(self):  # R5 boundary
        self.assertEqual(validate_title("  hi  "), "hi")

    def test_M2_accepts_exactly_200_chars(self):  # R5 boundary
        self.assertEqual(len(validate_title("a" * 200)), 200)

    def test_M2_keeps_unicode(self):  # R1 boundary
        self.assertEqual(validate_title("Mua sữa 🥛"), "Mua sữa 🥛")

    def test_M3_rejects_empty_and_blank(self):  # R5 negative
        for bad in ("", "   ", "\t\n"):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValidationError, "must not be empty"):
                    validate_title(bad)

    def test_M3_rejects_201_chars(self):  # R5 negative
        with self.assertRaisesRegex(ValidationError, "at most 200"):
            validate_title("a" * 201)

    def test_M3_rejects_non_string(self):  # R5 negative
        with self.assertRaisesRegex(ValidationError, "must be text"):
            validate_title(123)


class ValidatePriorityTests(unittest.TestCase):
    def test_M1_accepts_all_levels(self):  # R5 happy
        for p in ("low", "med", "high"):
            self.assertEqual(validate_priority(p), p)

    def test_M3_rejects_unknown_priority(self):  # R5 negative
        for bad in ("urgent", "HIGH", "", None):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValidationError, "priority must be one of"):
                    validate_priority(bad)


class ValidateDueTests(unittest.TestCase):
    def test_M1_accepts_iso_date(self):  # R5 happy
        self.assertEqual(validate_due("2026-12-01"), "2026-12-01")

    def test_M2_none_means_no_due_date(self):  # R5 boundary
        self.assertIsNone(validate_due(None))

    def test_M2_accepts_leap_day(self):  # R5 boundary
        self.assertEqual(validate_due("2028-02-29"), "2028-02-29")

    def test_M3_rejects_impossible_dates(self):  # R5 negative
        for bad in ("2026-02-30", "2027-02-29", "2026-13-01"):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValidationError, "not a real calendar date"):
                    validate_due(bad)

    def test_M3_rejects_wrong_formats(self):  # R5 negative
        for bad in ("2026-1-5", "31/12/2026", "tomorrow", "", 20261201):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValidationError, "YYYY-MM-DD"):
                    validate_due(bad)


class DueSortKeyTests(unittest.TestCase):
    def test_M4_dated_first_ascending_none_last_ties_by_id(self):  # R2 boundary
        tasks = [
            Task(id=1, title="no due"),
            Task(id=2, title="late", due="2026-12-31"),
            Task(id=3, title="early", due="2026-01-05"),
            Task(id=4, title="same as late", due="2026-12-31"),
            Task(id=5, title="also no due"),
        ]
        ordered = [t.id for t in sorted(tasks, key=due_sort_key)]
        self.assertEqual(ordered, [3, 2, 4, 1, 5])


class TaskDictTests(unittest.TestCase):
    def test_M5_round_trip(self):  # R6 happy
        task = Task(id=7, title="x", priority="high", due="2026-12-01", status="done")
        self.assertEqual(Task.from_dict(task.to_dict()), task)

    def test_M5_rejects_bad_stored_entries(self):  # R6 negative
        good = {"id": 1, "title": "t", "priority": "low", "due": None, "status": "todo"}
        bad_variants = [
            "not a dict",
            dict(good, id=0),
            dict(good, id="1"),
            dict(good, id=True),
            dict(good, status="blocked"),
            dict(good, title=""),
            dict(good, priority="urgent"),
            dict(good, due="2026-02-30"),
        ]
        for bad in bad_variants:
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    Task.from_dict(bad)


if __name__ == "__main__":
    unittest.main()


class ControlCharacterTitleTests(unittest.TestCase):
    """DEF-002: a line break in a title broke the list table."""

    def test_R5_rejects_control_characters(self):  # R5 negative
        for bad in ("line1\nline2", "a\rb", "tab\there", "nul\x00x", "esc\x1b[0m"):
            with self.subTest(bad=bad):
                with self.assertRaisesRegex(ValidationError, "control characters"):
                    validate_title(bad)

    def test_R5_surrounding_newline_is_still_trimmed(self):  # R5 boundary
        self.assertEqual(validate_title("hi\n"), "hi")

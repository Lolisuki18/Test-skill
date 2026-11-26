"""QA case definitions for taskbox: single source for the matrix (gen) and the run.

Usage:  python qa-artifacts/tools/matrix_cases.py gen   -> prints matrix rows (markdown)
        python qa-artifacts/tools/matrix_cases.py run   -> runs Auto cases, writes results.json
Every run uses a fresh temp folder and TASKBOX_FILE; the real ~/.taskbox is never touched.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CASES = []


def case(tc, req, module, title, pre, steps, data, expected, prio, etype, fn=None):
    CASES.append(dict(tc=tc, req=req, module=module, title=title, pre=pre, steps=steps,
                      data=data, expected=expected, prio=prio, etype=etype, fn=fn))


class Ctx:
    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="qa-taskbox-"))
        self.f = self.tmp / "tasks.json"
        self.fails = []
        self.notes = []

    def cli(self, *args, f=True, env=None):
        e = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING", "TASKBOX_FILE")}
        if f is True:
            e["TASKBOX_FILE"] = str(self.f)
        elif f:
            e["TASKBOX_FILE"] = str(f)
        e.update(env or {})
        p = subprocess.run([sys.executable, "-m", "taskbox", *args], cwd=REPO, env=e,
                           capture_output=True)
        out = p.stdout.decode("cp1252", "replace") if "PYTHONUTF8" not in e else p.stdout.decode("utf-8", "replace")
        err = p.stderr.decode("utf-8", "replace")
        self.notes.append("$ taskbox %s -> exit %d" % (" ".join(args)[:70], p.returncode))
        return p.returncode, out, err

    def seed(self):
        for a in (("add", "A low todo", "--priority", "low", "--due", "2026-12-05"),
                  ("add", "B high done", "--priority", "high", "--due", "2026-12-01"),
                  ("add", "C med nodue"),
                  ("add", "D high todo", "--priority", "high", "--due", "2026-12-03"),
                  ("done", "2")):
            self.cli(*a)

    def tasks(self):
        return json.loads(self.f.read_text(encoding="utf-8"))["tasks"]

    def ids(self, *args):
        c, out, _ = self.cli("list", *args)
        return [int(l.split()[0]) for l in out.splitlines()[1:]] if c == 0 and "No tasks" not in out else []

    def ok(self, cond, msg):
        if not cond:
            self.fails.append(msg)


STORE_ERR_FILES = {}


# ---------------- ADD (R1) ----------------
def t_add_001(c):
    code, out, err = c.cli("add", "Buy milk")
    c.ok(code == 0, "exit %s" % code); c.ok("Added task 1: Buy milk" in out, "stdout=%r" % out)
    c.ok(c.tasks() == [{"id": 1, "title": "Buy milk", "priority": "med", "due": None, "status": "todo"}], "stored=%r" % c.tasks())
case("TC-ADD-001", "R1", "ADD", "Add with title only creates task 1, med/todo, no due",
     "Temp data file does not exist", "1. Run `add \"Buy milk\"`\n2. Read the data file", "title=Buy milk",
     "Exit 0; stdout contains `Added task 1: Buy milk`; file holds one task id 1, priority med, status todo, due null", "P0", "Auto (API)", t_add_001)


def t_add_002(c):
    code, out, _ = c.cli("add", "Report", "--priority", "high", "--due", "2026-12-01")
    t = c.tasks()[0]
    c.ok(code == 0, "exit %s" % code); c.ok((t["priority"], t["due"]) == ("high", "2026-12-01"), "stored=%r" % t)
case("TC-ADD-002", "R1", "ADD", "Add with --priority high and --due stores both values",
     "No data file", "1. Run `add Report --priority high --due 2026-12-01`\n2. Read the data file", "priority=high, due=2026-12-01",
     "Exit 0; stored priority `high`, due `2026-12-01`", "P1", "Auto (API)", t_add_002)


def t_add_003(c):
    c.cli("add", "one"); code, out, _ = c.cli("add", "two")
    c.ok(code == 0 and "Added task 2" in out, "out=%r" % out); c.ok([t["id"] for t in c.tasks()] == [1, 2], "ids=%r" % [t["id"] for t in c.tasks()])
case("TC-ADD-003", "R1", "ADD", "Second add gets id 2",
     "No data file", "1. Run `add one`\n2. Run `add two`", "titles one, two", "Second add prints id 2; file ids are [1, 2]", "P1", "Auto (API)", t_add_003)


def t_add_004(c):
    c.cli("add", "a"); c.cli("add", "b"); c.cli("delete", "2"); code, out, _ = c.cli("add", "c")
    c.ok("Added task 3" in out, "out=%r" % out)
case("TC-ADD-004", "R1, R4", "ADD", "Id is not reused after delete (next add gets 3)",
     "No data file", "1. `add a`\n2. `add b`\n3. `delete 2`\n4. `add c`", "titles a, b, c", "Step 4 prints `Added task 3`", "P1", "Auto (API)", t_add_004)


def t_add_005(c):
    code, out, _ = c.cli("add", "Caf\u00e9 cr\u00e8me")
    raw = c.f.read_bytes().decode("utf-8")
    c.ok(code == 0, "exit %s" % code); c.ok("Caf\u00e9 cr\u00e8me" in raw, "file lacks unescaped accents")
case("TC-ADD-005", "R1, R6", "ADD", "Accented title (cp1252-safe) is stored as real UTF-8, not \\u escapes",
     "No data file", "1. Run `add \"Café crème\"`\n2. Read the file bytes as UTF-8", "title=Café crème", "Exit 0; file text contains `Café crème` literally", "P2", "Auto (API)", t_add_005)


def t_add_006(c):
    code, out, _ = c.cli("add", "--", "-dash")
    c.ok(code == 0 and c.tasks()[0]["title"] == "-dash", "code=%s out=%r" % (code, out))
case("TC-ADD-006", "R1", "ADD", "Title starting with `-` can be added after `--`",
     "No data file", "1. Run `add -- -dash`", "title=-dash", "Exit 0; stored title `-dash`", "P2", "Auto (API)", t_add_006)


def t_add_007(c):
    code, out, err = c.cli("add", "-dash")
    c.ok(code == 2, "exit %s" % code); c.ok(not c.f.exists(), "file created")
case("TC-ADD-007", "R1", "ADD", "Title starting with `-` without `--` is rejected as a usage error, file untouched",
     "No data file", "1. Run `add -dash`", "title=-dash", "Exit 2 (argparse); no file created; wording of message `[Needs input: exact error message]`", "P3", "Auto (API)", t_add_007)

case("TC-ADD-008", "R1, R5", "ADD", "Title containing a newline: behaviour is observed and recorded",
     "No data file", "1. In a shell run `add $'line1\\nline2'`\n2. Run `list`\n3. Note whether it is rejected or accepted and how the table looks", "title=line1<LF>line2",
     "[Needs input: expected behaviour for control characters; plan default is reject]", "P3", "Manual")


# ---------------- VAL (R5) ----------------
def t_val_001(c):
    code, out, err = c.cli("add", "")
    c.ok(code == 1 and "must not be empty" in err, "code=%s err=%r" % (code, err)); c.ok(not c.f.exists(), "file created")
case("TC-VAL-001", "R5, R1", "VAL", "Empty title is rejected, exit 1, file not created",
     "No data file", "1. Run `add \"\"`", "title=(empty)", "Exit 1; stderr contains `title must not be empty`; no data file", "P1", "Auto (API)", t_val_001)


def t_val_002(c):
    code, out, err = c.cli("add", "   ")
    c.ok(code == 1 and "must not be empty" in err, "code=%s err=%r" % (code, err))
case("TC-VAL-002", "R5, R1", "VAL", "Whitespace-only title is rejected, exit 1",
     "No data file", "1. Run `add \"   \"`", "title=3 spaces", "Exit 1; stderr contains `must not be empty`", "P1", "Auto (API)", t_val_002)


def t_val_003(c):
    code, _, _ = c.cli("add", "x" * 200)
    c.ok(code == 0 and len(c.tasks()[0]["title"]) == 200, "code=%s" % code)
case("TC-VAL-003", "R5", "VAL", "Title of exactly 200 characters is accepted",
     "No data file", "1. Run `add` with 200 x's", "title=x*200", "Exit 0; stored length 200", "P1", "Auto (API)", t_val_003)


def t_val_004(c):
    code, _, err = c.cli("add", "x" * 201)
    c.ok(code == 1 and "at most 200" in err, "code=%s err=%r" % (code, err)); c.ok(not c.f.exists(), "file created")
case("TC-VAL-004", "R5, R1", "VAL", "Title of 201 characters is rejected, exit 1, file not created",
     "No data file", "1. Run `add` with 201 x's", "title=x*201", "Exit 1; stderr contains `at most 200`; no data file", "P1", "Auto (API)", t_val_004)


def t_val_005(c):
    code, _, _ = c.cli("add", "  padded  ")
    c.ok(code == 0 and c.tasks()[0]["title"] == "padded", "stored=%r" % c.tasks())
case("TC-VAL-005", "R5", "VAL", "Surrounding whitespace is trimmed before saving",
     "No data file", "1. Run `add \"  padded  \"`", "title=2 spaces+padded+2 spaces", "Stored title `padded`", "P2", "Auto (API)", t_val_005)


def t_val_006(c):
    code, _, _ = c.cli("add", "  " + "x" * 200 + "  ")
    c.ok(code == 0, "code=%s (limit counted before trim?)" % code)
case("TC-VAL-006", "R5", "VAL", "Limit is counted after trim: 200 chars plus padding is accepted",
     "No data file", "1. Run `add` with 2 spaces + 200 x's + 2 spaces", "title=204 chars raw", "Exit 0 (plan open question 2 default: count after trim)", "P2", "Auto (API)", t_val_006)


def t_val_007(c):
    code, _, err = c.cli("add", "X", "--priority", "urgent")
    c.ok(code == 2 and "invalid choice" in err, "code=%s err=%r" % (code, err[-80:])); c.ok(not c.f.exists(), "file created")
case("TC-VAL-007", "R5, R1", "VAL", "Invalid priority `urgent` is rejected by argparse, exit 2, file not created",
     "No data file", "1. Run `add X --priority urgent`", "priority=urgent", "Exit 2; stderr `invalid choice`; no data file", "P1", "Auto (API)", t_val_007)


def t_val_008(c):
    codes = [c.cli("add", p, "--priority", p)[0] for p in ("low", "med", "high")]
    c.ok(codes == [0, 0, 0], "codes=%r" % codes); c.ok([t["priority"] for t in c.tasks()] == ["low", "med", "high"], "stored")
case("TC-VAL-008", "R5", "VAL", "Each valid priority low, med, high is accepted",
     "No data file", "1. Run `add` three times with --priority low / med / high", "low, med, high", "Three exit 0; stored priorities in order", "P2", "Auto (API)", t_val_008)


def t_val_009(c):
    code, _, err = c.cli("add", "X", "--due", "2026-02-30")
    c.ok(code == 1 and "not a real calendar date" in err, "code=%s err=%r" % (code, err))
case("TC-VAL-009", "R5, R1", "VAL", "Impossible date 2026-02-30 is rejected, exit 1",
     "No data file", "1. Run `add X --due 2026-02-30`", "due=2026-02-30", "Exit 1; stderr `not a real calendar date`; no file", "P1", "Auto (API)", t_val_009)


def t_val_010(c):
    code, _, err = c.cli("add", "X", "--due", "31/12/2026")
    c.ok(code == 1 and "YYYY-MM-DD" in err, "code=%s err=%r" % (code, err))
case("TC-VAL-010", "R5, R1", "VAL", "Wrong date format 31/12/2026 is rejected, exit 1",
     "No data file", "1. Run `add X --due 31/12/2026`", "due=31/12/2026", "Exit 1; stderr mentions `YYYY-MM-DD`", "P1", "Auto (API)", t_val_010)


def t_val_011(c):
    code, _, err = c.cli("add", "X", "--due", "")
    c.ok(code == 1, "code=%s err=%r" % (code, err))
case("TC-VAL-011", "R5, R1", "VAL", "Empty --due value is rejected, exit 1",
     "No data file", "1. Run `add X --due \"\"`", "due=(empty)", "Exit 1; message about YYYY-MM-DD", "P2", "Auto (API)", t_val_011)


def t_val_012(c):
    code, _, _ = c.cli("add", "leap", "--due", "2028-02-29")
    c.ok(code == 0, "code=%s" % code)
case("TC-VAL-012", "R5", "VAL", "Leap day 2028-02-29 is accepted",
     "No data file", "1. Run `add leap --due 2028-02-29`", "due=2028-02-29", "Exit 0", "P2", "Auto (API)", t_val_012)


def t_val_013(c):
    code, _, err = c.cli("add", "leap", "--due", "2027-02-29")
    c.ok(code == 1, "code=%s err=%r" % (code, err))
case("TC-VAL-013", "R5, R1", "VAL", "2027-02-29 (not a leap year) is rejected",
     "No data file", "1. Run `add leap --due 2027-02-29`", "due=2027-02-29", "Exit 1; `not a real calendar date`", "P2", "Auto (API)", t_val_013)


def t_val_014(c):
    code, _, err = c.cli("add", "X", "--due", "2026-1-5")
    c.ok(code == 1 and "YYYY-MM-DD" in err, "code=%s err=%r" % (code, err))
case("TC-VAL-014", "R5, R1", "VAL", "Non-zero-padded date 2026-1-5 is rejected",
     "No data file", "1. Run `add X --due 2026-1-5`", "due=2026-1-5", "Exit 1; `YYYY-MM-DD`", "P2", "Auto (API)", t_val_014)


def t_val_015(c):
    code, _, _ = c.cli("add", "old", "--due", "1999-01-01")
    c.ok(code == 0, "code=%s" % code)
case("TC-VAL-015", "R5", "VAL", "Past due date is accepted (plan assumption, no overdue logic)",
     "No data file", "1. Run `add old --due 1999-01-01`", "due=1999-01-01", "Exit 0", "P3", "Auto (API)", t_val_015)


def t_val_016(c):
    c.cli("add", "keep"); before = c.f.read_bytes()
    r = [c.cli("add", ""), c.cli("add", "X", "--priority", "urgent"), c.cli("add", "X", "--due", "2026-02-30")]
    c.ok([x[0] for x in r] == [1, 2, 1], "codes=%r" % [x[0] for x in r]); c.ok(c.f.read_bytes() == before, "file bytes changed")
case("TC-VAL-016", "R5, R6", "VAL", "Three rejected adds leave an existing data file byte-identical",
     "Data file with one task `keep`", "1. Save the file bytes\n2. Run `add \"\"`, `add X --priority urgent`, `add X --due 2026-02-30`\n3. Compare bytes", "see steps",
     "Exit codes 1, 2, 1; file bytes identical to step 1", "P0", "Auto (API)", t_val_016)


# ---------------- LIST (R2) ----------------
def t_list_001(c):
    c.seed(); code, out, _ = c.cli("list"); c.ok(c.ids() == [1, 2, 3, 4], "ids=%r" % c.ids()); c.ok(out.splitlines()[0].split()[0] == "ID", "header")
case("TC-LIST-001", "R2", "LIST", "List without options shows all tasks by id with a header",
     "Seeded store: 1 A low todo due 12-05, 2 B high done due 12-01, 3 C med no due, 4 D high todo due 12-03", "1. Run `list`", "seed (4 tasks)", "Header line then ids 1,2,3,4", "P1", "Auto (API)", t_list_001)


def t_list_002(c):
    c.seed(); i = c.ids("--status", "done"); c.ok(i == [2], "ids=%r" % i)
case("TC-LIST-002", "R2", "LIST", "--status done shows only done tasks", "Seeded store", "1. Run `list --status done`", "status=done", "Only id 2", "P2", "Auto (API)", t_list_002)


def t_list_003(c):
    c.seed(); i = c.ids("--status", "todo"); c.ok(i == [1, 3, 4], "ids=%r" % i)
case("TC-LIST-003", "R2", "LIST", "--status todo shows only todo tasks", "Seeded store", "1. Run `list --status todo`", "status=todo", "Ids 1,3,4", "P2", "Auto (API)", t_list_003)


def t_list_004(c):
    c.seed(); i = c.ids("--priority", "high"); c.ok(i == [2, 4], "ids=%r" % i)
case("TC-LIST-004", "R2", "LIST", "--priority high filters by priority", "Seeded store", "1. Run `list --priority high`", "priority=high", "Ids 2,4", "P2", "Auto (API)", t_list_004)


def t_list_005(c):
    c.seed(); i = c.ids("--status", "todo", "--priority", "high"); c.ok(i == [4], "ids=%r" % i)
case("TC-LIST-005", "R2", "LIST", "Status and priority filters combine with AND", "Seeded store", "1. Run `list --status todo --priority high`", "todo + high", "Only id 4", "P2", "Auto (API)", t_list_005)


def t_list_006(c):
    c.seed(); i = c.ids("--sort", "due"); c.ok(i == [2, 4, 1, 3], "ids=%r" % i)
case("TC-LIST-006", "R2", "LIST", "--sort due orders by date ascending, no-due task last", "Seeded store", "1. Run `list --sort due`", "sort=due", "Ids 2,4,1,3", "P1", "Auto (API)", t_list_006)


def t_list_007(c):
    c.cli("add", "n1"); c.cli("add", "n2", "--due", "2026-12-01"); c.cli("add", "n3", "--due", "2026-12-01"); c.cli("add", "n4")
    i = c.ids("--sort", "due"); c.ok(i == [2, 3, 1, 4], "ids=%r" % i)
case("TC-LIST-007", "R2", "LIST", "--sort due ties are broken by id; undated tasks keep id order", "No data file",
     "1. Add n1 (no due), n2 and n3 (due 2026-12-01), n4 (no due)\n2. Run `list --sort due`", "4 tasks", "Ids 2,3,1,4", "P2", "Auto (API)", t_list_007)


def t_list_008(c):
    code, out, _ = c.cli("list"); c.ok(code == 0 and out.strip() == "No tasks.", "code=%s out=%r" % (code, out))
case("TC-LIST-008", "R2", "LIST", "List on an empty store prints `No tasks.`, exit 0", "No data file", "1. Run `list`", "none", "Exit 0; stdout `No tasks.`", "P1", "Auto (API)", t_list_008)


def t_list_009(c):
    c.cli("add", "only"); code, out, _ = c.cli("list", "--status", "done"); c.ok(code == 0 and out.strip() == "No tasks.", "out=%r" % out)
case("TC-LIST-009", "R2", "LIST", "Filter with no match prints `No tasks.`, exit 0", "One todo task", "1. Run `list --status done`", "status=done", "Exit 0; `No tasks.`", "P2", "Auto (API)", t_list_009)


def t_list_010(c):
    code, _, err = c.cli("list", "--status", "bogus"); c.ok(code == 2 and "invalid choice" in err, "code=%s" % code)
case("TC-LIST-010", "R2", "LIST", "Invalid --status value is rejected by argparse, exit 2", "None", "1. Run `list --status bogus`", "status=bogus", "Exit 2; `invalid choice`", "P2", "Auto (API)", t_list_010)


def t_list_011(c):
    code, _, err = c.cli("list", "--sort", "name"); c.ok(code == 2, "code=%s" % code)
case("TC-LIST-011", "R2", "LIST", "Unsupported --sort value name is rejected, exit 2", "None", "1. Run `list --sort name`", "sort=name", "Exit 2", "P3", "Auto (API)", t_list_011)


def t_list_012(c):
    c.seed(); b = c.f.read_bytes(); c.cli("list"); c.cli("list", "--sort", "due"); c.ok(c.f.read_bytes() == b, "bytes changed")
case("TC-LIST-012", "R2, R6", "LIST", "List is read-only: data file bytes unchanged", "Seeded store", "1. Save bytes\n2. Run `list` and `list --sort due`\n3. Compare", "seed", "Bytes identical", "P2", "Auto (API)", t_list_012)


# ---------------- DONE (R3) ----------------
def t_done_001(c):
    c.cli("add", "t"); code, out, _ = c.cli("done", "1")
    c.ok(code == 0 and "marked done" in out, "out=%r" % out); c.ok(c.tasks()[0]["status"] == "done", "status")
case("TC-DONE-001", "R3", "DONE", "done marks the task done and persists it", "One todo task id 1", "1. Run `done 1`\n2. Read file", "id=1", "Exit 0; `Task 1 marked done.`; stored status done", "P0", "Auto (API)", t_done_001)


def t_done_002(c):
    c.cli("add", "t"); c.cli("done", "1"); b = c.f.read_bytes(); code, out, _ = c.cli("done", "1")
    c.ok(code == 0 and "already done" in out, "out=%r" % out); c.ok(c.f.read_bytes() == b, "file rewritten")
case("TC-DONE-002", "R3", "DONE", "done on an already-done task is idempotent (message, exit 0, file unchanged)", "Task 1 already done", "1. Run `done 1` again", "id=1", "Exit 0; `already done`; bytes unchanged", "P1", "Auto (API)", t_done_002)


def t_done_003(c):
    c.cli("add", "t"); b = c.f.read_bytes(); code, _, err = c.cli("done", "99")
    c.ok(code == 1 and "no task with id 99" in err, "code=%s err=%r" % (code, err)); c.ok(c.f.read_bytes() == b, "changed")
case("TC-DONE-003", "R3", "DONE", "done with an unknown id fails, exit 1, file unchanged", "One task id 1", "1. Run `done 99`", "id=99", "Exit 1; stderr `no task with id 99`; bytes unchanged", "P0", "Auto (API)", t_done_003)


def t_done_004(c):
    code, _, err = c.cli("done", "abc"); c.ok(code == 2 and "invalid int value" in err, "code=%s" % code)
case("TC-DONE-004", "R3", "DONE", "done with non-integer id abc is a usage error, exit 2", "None", "1. Run `done abc`", "id=abc", "Exit 2", "P1", "Auto (API)", t_done_004)


def t_done_005(c):
    c.cli("add", "t"); r = [c.cli("done", "0")[0], c.cli("done", "-1")[0]]; c.ok(r == [1, 1], "codes=%r" % r)
case("TC-DONE-005", "R3", "DONE", "Ids 0 and -1 are reported as unknown ids, exit 1", "One task", "1. `done 0`\n2. `done -1`", "0, -1", "Both exit 1", "P2", "Auto (API)", t_done_005)


def t_done_006(c):
    c.cli("add", "t"); code, out, err = c.cli("done", "9" * 23); c.ok(code == 1 and "Traceback" not in err, "code=%s" % code)
case("TC-DONE-006", "R3", "DONE", "Huge id (23 digits) is a clean error, no traceback", "One task", "1. Run `done 99999999999999999999999`", "id=9*23", "Exit 1; no traceback", "P3", "Auto (API)", t_done_006)


# ---------------- DEL (R4) ----------------
def t_del_001(c):
    c.cli("add", "a"); c.cli("add", "b"); code, out, _ = c.cli("delete", "1")
    c.ok(code == 0 and "Deleted task 1" in out, "out=%r" % out); c.ok([t["id"] for t in c.tasks()] == [2], "ids")
case("TC-DEL-001", "R4", "DEL", "delete removes the task and persists", "Tasks 1 and 2", "1. Run `delete 1`\n2. Read file", "id=1", "Exit 0; `Deleted task 1.`; file ids [2]", "P0", "Auto (API)", t_del_001)


def t_del_002(c):
    c.cli("add", "a"); b = c.f.read_bytes(); code, _, err = c.cli("delete", "7")
    c.ok(code == 1 and "no task with id 7" in err, "code=%s" % code); c.ok(c.f.read_bytes() == b, "changed")
case("TC-DEL-002", "R4", "DEL", "delete with unknown id fails, exit 1, file unchanged", "One task", "1. Run `delete 7`", "id=7", "Exit 1; `no task with id 7`; bytes unchanged", "P0", "Auto (API)", t_del_002)


def t_del_003(c):
    c.cli("add", "a"); c.cli("delete", "1"); code, _, _ = c.cli("delete", "1"); c.ok(code == 1, "code=%s" % code)
case("TC-DEL-003", "R4", "DEL", "Deleting the same id twice: second call exits 1", "One task", "1. `delete 1`\n2. `delete 1`", "id=1", "Second exit 1", "P1", "Auto (API)", t_del_003)


def t_del_004(c):
    c.cli("add", "a"); c.cli("delete", "1"); code, out, _ = c.cli("list"); c.ok(code == 0 and out.strip() == "No tasks.", "out=%r" % out)
case("TC-DEL-004", "R4", "DEL", "After deleting the last task, list prints `No tasks.`", "One task", "1. `delete 1`\n2. `list`", "id=1", "`No tasks.`, exit 0", "P2", "Auto (API)", t_del_004)


def t_del_005(c):
    c.cli("add", "a"); c.cli("delete", "1"); c.cli("delete", "1")
    data = json.loads(c.f.read_text(encoding="utf-8")); c.ok(data["next_id"] == 2 and data["tasks"] == [], "data=%r" % data)
case("TC-DEL-005", "R4, R6", "DEL", "next_id survives deleting every task (file keeps next_id 2)", "One task", "1. `delete 1`\n2. Read file", "id=1", "File: tasks [], next_id 2", "P2", "Auto (API)", t_del_005)


# ---------------- STORE (R6) ----------------
def t_store_001(c):
    code, out, _ = c.cli("list"); c.ok(code == 0 and "No tasks" in out and not c.f.exists(), "code=%s exists=%s" % (code, c.f.exists()))
case("TC-STORE-001", "R6", "STORE", "Missing file means empty list and list does not create the file", "No data file", "1. Run `list`", "none", "Exit 0; `No tasks.`; file still absent", "P1", "Auto (API)", t_store_001)


def t_store_002(c):
    p = c.tmp / "a" / "b" / "t.json"; code, _, _ = c.cli("add", "x", f=p); c.ok(code == 0 and p.is_file(), "code=%s" % code)
case("TC-STORE-002", "R6", "STORE", "add creates missing parent folders for the data file", "Folder `a/b` absent", "1. Run `add x` with TASKBOX_FILE=<tmp>/a/b/t.json", "path with 2 missing levels", "Exit 0; file exists", "P1", "Auto (API)", t_store_002)


def t_store_003(c):
    c.f.write_bytes(b""); code, out, _ = c.cli("list"); c.ok(code == 0 and "No tasks" in out, "out=%r" % out)
case("TC-STORE-003", "R6", "STORE", "Zero-byte data file is treated as an empty store", "Empty file", "1. Run `list`", "0-byte file", "Exit 0; `No tasks.`", "P2", "Auto (API)", t_store_003)


def _bad(c, content, needle, tcname, cmds=(("list",), ("add", "x"), ("done", "1"), ("delete", "1"))):
    c.f.write_bytes(content)
    for a in cmds:
        code, out, err = c.cli(*a)
        c.ok(code == 1 and needle in err and "Traceback" not in err, "%s: code=%s err=%r" % (a, code, err[:90]))
        c.ok(c.f.read_bytes() == content, "%s changed the file" % (a,))


def t_store_004(c): _bad(c, b"{bad", "not valid JSON", "corrupt")
case("TC-STORE-004", "R6", "STORE", "Corrupt JSON: all four commands exit 1 with a clear error and the file is not overwritten",
     "Data file containing `{bad`", "1. Run `list`, `add x`, `done 1`, `delete 1` in turn\n2. After each, compare file bytes", "content=`{bad`", "Each: exit 1; stderr `not valid JSON`; no traceback; bytes unchanged", "P0", "Auto (API)", t_store_004)


def t_store_005(c): _bad(c, b'{"version":2,"next_id":1,"tasks":[]}', "unsupported", "ver")
case("TC-STORE-005", "R6", "STORE", "Unknown format version 2 is rejected and file untouched",
     "File with version 2", "1. Run the four commands\n2. Compare bytes", "version=2", "Each: exit 1; `unsupported format or version`; bytes unchanged", "P1", "Auto (API)", t_store_005)


def t_store_006(c): _bad(c, b'{"version":1,"next_id":1,"tasks":{}}', "malformed", "struct")
case("TC-STORE-006", "R6", "STORE", "Wrong structure (tasks is not a list) is rejected and file untouched",
     "File with tasks as object", "1. Run the four commands\n2. Compare bytes", "tasks={}", "Each: exit 1; `malformed structure`; bytes unchanged", "P1", "Auto (API)", t_store_006)


def t_store_007(c): _bad(c, "[]".encode("utf-16"), "not valid UTF-8", "utf16")
case("TC-STORE-007", "R6", "STORE", "UTF-16 data file (e.g. written by PowerShell `>`) gives a clean error, file untouched (last fix, commit 9a50011)",
     "File saved as UTF-16", "1. Run the four commands\n2. Compare bytes", "UTF-16 `[]`", "Each: exit 1; `not valid UTF-8`; no traceback; bytes unchanged", "P0", "Auto (API)", t_store_007)


def t_store_008(c):
    body = json.dumps({"version": 1, "next_id": 1, "tasks": []}).encode("utf-8-sig"); _bad(c, body, "not valid JSON", "bom")
case("TC-STORE-008", "R6", "STORE", "UTF-8 file with BOM (Notepad style) gives a clean error and file untouched",
     "File saved as UTF-8 with BOM", "1. Run the four commands\n2. Compare bytes", "BOM + valid JSON", "Each: exit 1; clean `error:` line, no traceback; bytes unchanged. Whether BOM should be tolerated: `[Needs input: product decision]`", "P2", "Auto (API)", t_store_008)


def t_store_009(c): _bad(c, b"[" * 200000, "not valid JSON", "nest")
case("TC-STORE-009", "R6", "STORE", "Deeply nested JSON (200000 `[`) gives a clean error, no traceback (last fix, commit ac9ee0a)",
     "File of 200000 `[`", "1. Run the four commands\n2. Compare bytes", "`[` x 200000", "Each: exit 1; `not valid JSON`; no traceback; bytes unchanged", "P1", "Auto (API)", t_store_009)


def t_store_010(c):
    d = c.tmp / "adir"; d.mkdir(); code, out, err = c.cli("list", f=d)
    c.ok(code == 1 and "error:" in err and "Traceback" not in err, "code=%s err=%r" % (code, err[:100]))
case("TC-STORE-010", "R6", "STORE", "Data file path that is a directory gives `error:` and exit 1", "Folder exists at the path", "1. Run `list` with TASKBOX_FILE=<folder>", "path=folder", "Exit 1; `error: cannot read ...`; no traceback", "P2", "Auto (API)", t_store_010)


def t_store_011(c):
    other = c.tmp / "env.json"; code, _, _ = c.cli("--file", str(c.tmp / "cli.json"), "add", "x", f=other)
    c.ok(code == 0 and (c.tmp / "cli.json").exists() and not other.exists(), "cli=%s env=%s" % ((c.tmp / "cli.json").exists(), other.exists()))
case("TC-STORE-011", "R6", "STORE", "--file wins over TASKBOX_FILE", "Both set to different files", "1. Run `--file cli.json add x` with TASKBOX_FILE=env.json", "two paths", "cli.json created; env.json absent", "P2", "Auto (API)", t_store_011)


def t_store_012(c):
    home = c.tmp / "home"; home.mkdir()
    code, _, _ = c.cli("add", "x", f=False, env={"USERPROFILE": str(home), "HOME": str(home)})
    c.ok(code == 0 and (home / ".taskbox" / "tasks.json").is_file(), "code=%s" % code)
case("TC-STORE-012", "R6", "STORE", "Default path is <home>/.taskbox/tasks.json (home redirected to a temp folder)", "TASKBOX_FILE unset; USERPROFILE/HOME point to a temp folder", "1. Run `add x`\n2. Look for <home>/.taskbox/tasks.json", "temp home", "Exit 0; file at <temp home>/.taskbox/tasks.json (the real home is never touched)", "P2", "Auto (API)", t_store_012)


def t_store_013(c):
    c.cli("add", "a"); c.cli("add", "b"); c.cli("done", "1"); c.cli("delete", "2")
    left = [p.name for p in c.tmp.iterdir() if p.name != "tasks.json"]; c.ok(left == [], "leftovers=%r" % left)
case("TC-STORE-013", "R6", "STORE", "Successful writes leave no `.taskbox-*.tmp` temp files", "No data file", "1. add, add, done, delete\n2. List the folder", "4 writes", "Folder contains only tasks.json", "P2", "Auto (API)", t_store_013)


def t_store_014(c):
    body = json.dumps({"version": 1, "next_id": 2, "tasks": [{"id": 1, "title": "", "priority": "med", "due": None, "status": "todo"}]}).encode()
    _bad(c, body, "invalid task", "badtask")
case("TC-STORE-014", "R6, R5", "STORE", "A stored task that violates R5 (empty title) is rejected on load, file untouched", "Valid JSON with one task whose title is empty", "1. Run the four commands\n2. Compare bytes", "title=\"\"", "Each: exit 1; `contains an invalid task`; bytes unchanged", "P2", "Auto (API)", t_store_014)

case("TC-STORE-015", "R6", "STORE", "Two processes adding at the same time: no corruption (lost update tolerated by plan §8)",
     "No data file", "1. Start 10 `add` processes at once against one file\n2. Count tasks and check the file is valid JSON", "10 parallel adds",
     "File stays valid JSON; every process exits 0 or prints a clean `error:`; count of tasks recorded (plan accepts lost updates)", "P2", "Manual")

case("TC-STORE-016", "R6", "STORE", "Read-only data file: add fails with a clean error and the file is not changed",
     "Data file with one task, set read-only", "1. `attrib +R` the file\n2. Run `add x`\n3. Compare bytes", "read-only attribute", "Exit 1 `error: cannot write ...`, no traceback, bytes unchanged", "P2", "Manual")


# ---------------- ENC (console encoding, finding #1) ----------------
def t_enc_001(c):
    code, out, err = c.cli("add", "Buy coffee \u2615")
    c.ok(code == 0, "exit %s" % code); c.ok("Traceback" not in err, "traceback printed: %s" % (err.strip().splitlines() or [""])[-1][:90])
case("TC-ENC-001", "R1, R5", "ENC", "Add a title with a character outside cp1252 (`☕`) on a cp1252 console: no traceback, exit 0",
     "Windows console, code page cp1252; PYTHONUTF8 unset", "1. Run `add \"Buy coffee ☕\"`\n2. Check exit code and stderr", "title=Buy coffee ☕",
     "Exit 0 and `Added task 1: ...` (characters may be replaced); no Python traceback; (source: plan §5 \"unicode title kept intact\", audit finding 1)", "P1", "Auto (API)", t_enc_001)


def t_enc_002(c):
    c.f.write_text(json.dumps({"version": 1, "next_id": 2, "tasks": [{"id": 1, "title": "Buy coffee \u2615", "priority": "med", "due": None, "status": "todo"}]}, ensure_ascii=False), encoding="utf-8")
    code, out, err = c.cli("list"); c.ok(code == 0, "exit %s" % code); c.ok("Traceback" not in err, "traceback printed: %s" % (err.strip().splitlines() or [""])[-1][:90])
case("TC-ENC-002", "R2, R6", "ENC", "List a store that contains `☕` on a cp1252 console: no traceback, exit 0",
     "Data file with a task titled `Buy coffee ☕` (UTF-8); cp1252 console", "1. Run `list`", "stored title with ☕", "Exit 0; table printed (characters may be replaced); no traceback", "P1", "Auto (API)", t_enc_002)


def t_enc_003(c):
    code, out, err = c.cli("add", "Buy coffee \u2615", env={"PYTHONUTF8": "1"}); code2, out2, _ = c.cli("list", env={"PYTHONUTF8": "1"})
    c.ok(code == 0 and code2 == 0 and "\u2615" in out2, "codes=%s,%s" % (code, code2))
case("TC-ENC-003", "R1, R2", "ENC", "Workaround check: with PYTHONUTF8=1 the same add/list works", "PYTHONUTF8=1", "1. `add \"Buy coffee ☕\"`\n2. `list`", "title=Buy coffee ☕", "Both exit 0; list shows ☕", "P2", "Auto (API)", t_enc_003)


def t_enc_004(c):
    code, out, err = c.cli("add", "Caf\u00e9"); code2, out2, _ = c.cli("list")
    c.ok(code == 0 and code2 == 0 and "Caf\u00e9" in out2, "codes=%s,%s out=%r" % (code, code2, out2))
case("TC-ENC-004", "R1, R2", "ENC", "Accented title that cp1252 can print works end to end", "cp1252 console", "1. `add Café`\n2. `list`", "title=Café", "Both exit 0; list shows `Café`", "P2", "Auto (API)", t_enc_004)

case("TC-ENC-005", "R1", "ENC", "Real interactive terminal (Windows Terminal / cmd with `chcp 65001`): ☕ title add and list",
     "Interactive terminal controlled by the user", "1. Open the user's terminal\n2. Run add and list with ☕", "title=Buy coffee ☕", "No traceback; characters render", "P3", "Manual")


# ---------------- CLI general ----------------
def t_cli_001(c):
    code, _, err = c.cli(); c.ok(code == 2 and "required" in err, "code=%s" % code)
case("TC-CLI-001", "R5", "CLI", "No sub-command prints usage and exits 2", "None", "1. Run `python -m taskbox`", "none", "Exit 2; usage on stderr", "P3", "Auto (API)", t_cli_001)


def t_cli_002(c):
    code, out, _ = c.cli("--version"); c.ok(code == 0 and out.strip() == "taskbox 0.1.0", "out=%r" % out)
case("TC-CLI-002", "R1", "CLI", "--version prints `taskbox 0.1.0`", "None", "1. Run `--version`", "none", "Exit 0; `taskbox 0.1.0`", "P3", "Auto (API)", t_cli_002)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "gen"
    if mode == "gen":
        for k in CASES:
            esc = lambda s: s.replace("|", "\\|").replace("\n", "<br>")
            print("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % tuple(esc(x) for x in (
                k["tc"], k["req"], k["module"], k["title"], k["pre"], k["steps"], k["data"], k["expected"], k["prio"], k["etype"])))
        return
    results = []
    for k in CASES:
        if k["etype"] != "Auto (API)":
            results.append(dict(tc=k["tc"], result="Not Run", evidence="Manual case, not executed by the script"))
            continue
        c = Ctx()
        try:
            k["fn"](c)
            res = "Pass" if not c.fails else "Fail"
            ev = "; ".join(c.fails) if c.fails else "all checks met (%d commands)" % len(c.notes)
        except Exception as exc:  # harness problem, not a product verdict
            res, ev = "Blocked", "harness error: %r" % exc
        results.append(dict(tc=k["tc"], result=res, evidence=ev, folder=str(c.tmp)))
    out = Path(__file__).with_name("results.json")
    out.write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in results:
        print(r["tc"], r["result"], "|", r["evidence"][:150])


main()

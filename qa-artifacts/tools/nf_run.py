"""Non-functional runs for taskbox (NF-PERF-01..05, NF-SEC-01, NF-SEC-04). Temp folder only."""
import json
import os
import random
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
tmp = Path(tempfile.mkdtemp(prefix="qa-nf-"))
home_store = Path.home() / ".taskbox" / "tasks.json"
home_before = (home_store.exists(), home_store.stat().st_mtime if home_store.exists() else None)


def env(f):
    e = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING")}
    e["TASKBOX_FILE"] = str(f)
    return e


def run(f, *args):
    t = time.perf_counter()
    p = subprocess.run([sys.executable, "-m", "taskbox", *args], cwd=REPO, env=env(f), capture_output=True)
    return time.perf_counter() - t, p.returncode


def make_store(n, name):
    f = tmp / name
    tasks = [{"id": i, "title": "task number %d" % i, "priority": ("low", "med", "high")[i % 3],
              "due": "2026-%02d-%02d" % (1 + i % 12, 1 + i % 28) if i % 5 else None,
              "status": "done" if i % 4 == 0 else "todo"} for i in range(1, n + 1)]
    f.write_text(json.dumps({"version": 1, "next_id": n + 1, "tasks": tasks}, ensure_ascii=False), encoding="utf-8")
    return f


def med(f, args, reps=5):
    ts, codes = [], set()
    for _ in range(reps):
        t, c = run(f, *args); ts.append(t); codes.add(c)
    return statistics.median(ts), max(ts), codes


def baseline():
    f = tmp / "empty.json"
    return med(f, ["list"], 5)[0]


print("baseline: list on empty store, median of 5 = %.3f s" % baseline())
for n in (1000, 10000, 50000):
    f = make_store(n, "s%d.json" % n)
    size = f.stat().st_size
    for label, args in (("list", ["list"]), ("add", ["add", "x"]), ("list --sort due --status todo", ["list", "--sort", "due", "--status", "todo"])):
        m, mx, codes = med(f, args)
        print("n=%-6d size=%6.1f KB  %-30s median %.3f s  max %.3f s  exit codes %s" % (n, size / 1024, label, m, mx, sorted(codes)))
    if n == 10000:
        f = make_store(n, "s10k-done.json")
        md, _, cd = med(f, ["done", str(n)], 1)
        mdel, _, cdel = med(f, ["delete", "1"], 1)
        print("n=10000 done(last id) %.3f s exit %s ; delete(first id) %.3f s exit %s" % (md, sorted(cd), mdel, sorted(cdel)))

# NF-SEC-01: kill during write, 40 iterations
f = tmp / "kill.json"
bad = 0
stray = 0
big = make_store(5000, "kill.json")
random.seed(7)
for i in range(40):
    p = subprocess.Popen([sys.executable, "-m", "taskbox", "add", "k%d" % i], cwd=REPO, env=env(f),
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(random.uniform(0.0, 0.25))
    p.kill(); p.wait()
    try:
        d = json.loads(f.read_text(encoding="utf-8"))
        ids = [t["id"] for t in d["tasks"]]
        if len(ids) != len(set(ids)) or d["next_id"] <= max(ids):
            bad += 1
    except Exception as exc:
        bad += 1
        print("iteration %d: file invalid: %r" % (i, exc))
stray = len([p for p in tmp.iterdir() if p.name.startswith(".taskbox-")])
d = json.loads(f.read_text(encoding="utf-8"))
print("NF-SEC-01: 40 kill iterations on a 5000-task store; invalid/inconsistent files: %d; stray .taskbox-*.tmp left: %d; final tasks %d" % (bad, stray, len(d["tasks"])))

home_after = (home_store.exists(), home_store.stat().st_mtime if home_store.exists() else None)
print("NF-SEC-04: real ~/.taskbox/tasks.json before=%r after=%r -> %s" % (home_before, home_after, "unchanged" if home_before == home_after else "CHANGED"))

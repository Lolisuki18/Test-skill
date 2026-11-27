#!/usr/bin/env python3
"""Builds the per-case results table of 03-execution-notes.md from machine-readable results
(Playwright JSON + node:test JUnit) and the matrix. Nothing is typed by hand: a case with no result
in any report is 'Not Run'. Run from repo root: python qa-artifacts/habitly/tools/build_notes.py
Round info is kept in ROUND below."""
import json, os, re, sys
import xml.etree.ElementTree as ET
from pathlib import Path

T = Path(__file__).resolve().parent
ART = T.parent
ROUND = os.environ.get("ROUND", "1")
DATE = "2026-11-27"
DEFECT_FOR = {"TC-STO-006": "DEF-001"}  # linked after Phase 4
MANUAL_REASON = {
    "TC-BKP-010": "needs the real OS file chooser / download dialog (not drivable by the agent); run script below",
    "TC-A11Y-005": "needs a real screen reader on a real device; not available to the agent",
    "TC-WEEK-005": "needs the tab to stay open across local midnight (not run by the agent)",
}
# Auto (API) cases = existing node:test tests (substring of the JUnit test name)
NODE_MAP = {
    "TC-ADD-006": ["R1 negative: invalid name or target"],
    "TC-EDIT-004": ["R2 negative: unknown id and duplicate rename"],
    "TC-EDIT-005": ["R2 boundary: renaming to its own name"],
    "TC-TOG-005": ["R3 boundary: today allowed", "R3 negative: bad date"],
    "TC-WEEK-003": ["R4 happy: week of Fri", "R4 boundary: Sunday belongs"],
    "TC-WEEK-004": ["R4 boundary: weekCount", "R4 negative: invalid dates"],
    "TC-STRK-001": ["R5 happy: 3-day run"],
    "TC-STRK-002": ["R5 boundary: today not yet done"],
    "TC-BKP-001": ["R6 happy: export then import"],
    "TC-BKP-008": ["R6 negative: malformed backups"],
    "TC-BKP-009": ["R6 boundary: empty state"],
    "TC-STO-001": ["R7 happy: save then load"],
    "TC-STO-007": ["R7 negative: corrupt data", "R7 negative: invalid-but-parseable", "R7 negative: throwing storage"],
}
# Manual cases the agent really executed in the built-in browser pane (evidence quoted in 03-execution-notes.md section 4)
MANUAL_DONE = {"TC-EDIT-006": ("Pass", "built-in browser pane: Edit Meditate, typed `lost` (field `Meditatelost`, button `Save changes`), reloaded: field empty, button `Add habit`, both habits intact in localStorage. No unsaved-edit warning shown (Informational)")}
if ROUND == "2":
    MANUAL_DONE["TC-EDIT-006"] = ("Pass", "round 2, built-in browser pane 360x740 (dark), build 1a50381: Edit Meditate, typed `lost` (field `Meditatelost`, button `Save changes`), reloaded: field empty, button `Add habit`, stored habits [`Meditate`]. No unsaved-edit warning (Informational)")
INFORMATIONAL = {"TC-ADD-012"}  # Oracle: none

matrix = (ART / "02-test-matrix.md").read_text(encoding="utf-8")
cases = []
for line in matrix.splitlines():
    if line.startswith("| TC-"):
        c = [x.strip() for x in line.strip("|").split(" | ")]
        cases.append({"id": c[0], "prio": c[9], "type": c[10].rstrip(" |")})

pw = json.loads((T / f"results-pw-round{ROUND}.json").read_text(encoding="utf-8"))
pw_res = {}
def walk(s):
    for sp in s.get("specs", []):
        m = re.match(r"(TC-[A-Z0-9]+-\d+|NF-[A-Z0-9]+-\d+)", sp["title"])
        for t in sp["tests"]:
            r = t["results"][-1]
            pw_res.setdefault(m.group(1), []).append((r["status"], sp["title"], [a["description"] for a in t.get("annotations", [])], (r.get("error") or {}).get("message", "")))
    for c in s.get("suites", []): walk(c)
for s in pw["suites"]: walk(s)

node = {}
for tc in ET.parse(T / f"results-node-round{ROUND}.xml").getroot().iter("testcase"):
    node[tc.get("name")] = "fail" if tc.find("failure") is not None else "pass"

rows, tally = [], {}
for c in cases:
    tid = c["id"]; res = "Not Run"; note = ""
    if c["type"] == "Auto (browser)":
        r = pw_res.get(tid)
        if r:
            ok = all(x[0] == "passed" for x in r)
            res = "Pass" if ok else "Fail"
            ann = "; ".join(a for x in r for a in x[2])
            if tid in INFORMATIONAL: res = "Informational" if ok else "Fail"
            note = f"Playwright `{tid}`" + (f"; observed: {ann}" if ann else "")
            if not ok:
                err = re.sub(r"\x1b\[[0-9;]*m", "", r[0][3]).strip().splitlines()
                note += "; FAILED: " + " / ".join(x.strip() for x in err[:3] if x.strip())[:230]
        else:
            note = "no result in Playwright report"
    elif c["type"] == "Auto (API)":
        names = NODE_MAP.get(tid, [])
        found = [n for n in node for k in names if n.startswith(k)]
        if names and len(found) >= len(names) and all(node[n] == "pass" for n in found):
            res = "Pass"; note = "node:test (JUnit): " + "; ".join(found)
        elif found: res = "Fail"; note = "node:test failure: " + "; ".join(found)
        else: note = "no matching node test result"
    else:
        if tid in MANUAL_DONE: res, note = MANUAL_DONE[tid]
        else: note = MANUAL_REASON.get(tid, "manual, not executed")
    d = DEFECT_FOR.get(tid, "-") if res == "Fail" else "-"
    rows.append(f"| {tid} | {c['type']} | {res} | {DATE} | {d} | {note} |")
    tally[(c["prio"], res)] = tally.get((c["prio"], res), 0) + 1
    c["res"] = res

tot = {}
for c in cases: tot[c["res"]] = tot.get(c["res"], 0) + 1
(T / f"results-round{ROUND}-table.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
summary = {"total": len(cases), **tot, "byPrio": {f"{p}/{r}": n for (p, r), n in sorted(tally.items())}}
(T / f"results-round{ROUND}-summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
print(json.dumps(summary))

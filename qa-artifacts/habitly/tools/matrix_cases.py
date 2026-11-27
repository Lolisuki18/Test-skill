#!/usr/bin/env python3
"""Generates qa-artifacts/habitly/02-test-matrix.md from one case list (table and counts cannot drift).
Run: python qa-artifacts/habitly/tools/matrix_cases.py   (from the repo root)
Status line is preserved if the file already exists (so approval is never reset by a regenerate)."""
import re
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "02-test-matrix.md"
B, A, M = "Auto (browser)", "Auto (API)", "Manual"
URL = "http://localhost:8765/"

# (id, req, module, title, pre, steps, data, expected, oracle, prio, type)
C = [
 # ---- R1 add
 ("TC-ADD-001","R1","Add","Adding a valid habit shows it in the grid with 0/target","Empty storage; page open","1. Type the name 2. Set target 3. Click Add habit","name `Read`; target 3","Row `Read` appears with `0/3 this week`; status says `Habit added.`; form name cleared","spec","P1",B),
 ("TC-ADD-002","R1","Add","Name is trimmed before saving","Empty storage","1. Type name with spaces around 2. Click Add habit","name `  Read  `; target 3","Row name is `Read` (no surrounding spaces)","spec","P2",B),
 ("TC-ADD-003","R1","Add","Empty or whitespace-only name is rejected, no new row","Empty storage","1. Type whitespace in name 2. Click Add habit","name `   `; target 3","Status shows an error text (domain message `Name is required.`); grid stays empty; storage key not created","spec","P1",B),
 ("TC-ADD-004","R1","Add","Name of exactly 60 characters is accepted","Empty storage","1. Type 60 chars 2. Click Add habit","60 x `a`; target 3","Habit added; row shows the 60-char name","spec","P2",B),
 ("TC-ADD-005","R1","Add","Typing a 61st character is cut off by the field (maxlength 60)","Empty storage","1. Paste 61 chars into name 2. Read the field value","61 x `a`","Field value length is 60 (the 61-char rejection itself is domain-level, see TC-ADD-006)","code behavior","P3",B),
 ("TC-ADD-006","R1","Add","Domain rejects a 61-char name and invalid targets without changing state","Node 22","1. Run the existing R1 negative test","61-char name; target 0, 8, 2.5","ValidationError thrown for each; input state not mutated (test `R1 negative: invalid name or target rejected, state not mutated`)","spec","P1",A),
 ("TC-ADD-007","R1","Add","Target outside 1-7 or non-integer is rejected in the UI","Empty storage","1. Enter a valid name 2. Enter the target 3. Click Add habit","targets `0`, `8`, `2.5` (one run each)","Error text shown (domain: `Target must be a whole number from 1 to 7.`); no row added","spec","P1",B),
 ("TC-ADD-008","R1","Add","Targets 1 and 7 are accepted","Empty storage","1. Add `A` with target 1 2. Add `B` with target 7","targets `1`, `7`","Both rows appear with `0/1` and `0/7`","spec","P2",B),
 ("TC-ADD-009","R1","Add","Duplicate name (case-insensitive) is rejected","Habit `Read` exists","1. Add `read`","name `read`","Error `A habit with this name already exists.`; still one row","spec","P1",B),
 ("TC-ADD-010","R1","Add","HTML in a name is shown as plain text","Empty storage","1. Add habit named `<b>x</b>&amp;`","name `<b>x</b>&amp;`","Row shows the literal text; no `<b>` element in the DOM","spec","P1",B),
 ("TC-ADD-011","R1","Add","Double-clicking Add habit adds one habit only","Form filled","1. Double-click Add habit","name `Dbl`; target 3","Exactly one row `Dbl`; a second submit sees empty name (observe the final status text)","code behavior","P2",B),
 ("TC-ADD-012","R1","Add","Emoji name counts as UTF-16 code units (boundary)","Empty storage","1. Add a name of 30 emoji","30 x `😀` (60 code units)","Observe: accepted as 60 units (2 per emoji); Informational because spec does not say characters vs code units","none","P3",B),
 # ---- R2 edit / archive
 ("TC-EDIT-001","R2","Edit","Editing name and target saves both","Habit `Read` target 3","1. Click Edit Read 2. Change name and target 3. Click Save changes","name `Read more`; target 5","Row shows `Read more` and `0/5`; button text back to `Add habit`; status `Habit updated.`","spec","P2",B),
 ("TC-EDIT-002","R2","Edit","Cancel edit resets the form and changes nothing","Habit `Read`","1. Click Edit Read 2. Change name 3. Click Cancel edit","name `zzz`","Form empty, `Cancel edit` hidden, row still `Read`; status `Edit cancelled.`","code behavior","P3",B),
 ("TC-EDIT-003","R2","Edit","Archive hides habit from the grid but keeps data, restore brings it back","Habit `Read` with 1 done day","1. Click Archive Read 2. Check Archived list 3. Reload 4. Click Restore Read","-","After archive: grid empty, `Read` listed under Archived (also after reload); after restore: row back with the done day intact","spec","P2",B),
 ("TC-EDIT-004","R2","Edit","Rename to an existing name and unknown id are rejected (domain)","Node 22","1. Run existing R2 negative test","dup name; unknown id","ValidationError, state unchanged (`R2 negative: unknown id and duplicate rename rejected`)","spec","P2",A),
 ("TC-EDIT-005","R2","Edit","Renaming to its own name is allowed (domain)","Node 22","1. Run existing R2 boundary test","same name","No error (`R2 boundary: renaming to its own name is allowed`)","spec","P3",A),
 ("TC-EDIT-006","R2","Edit","Reload while editing discards the edit but keeps data","Habit `Read`; edit mode open with changed name","1. Click Edit 2. Type a new name 3. Reload the page (F5)","name `lost`","Page loads in normal mode, row still `Read`; Informational on whether an unsaved-edit warning is expected","none","P3",M),
 ("TC-EDIT-007","R2","Edit","Archived habit name still blocks a new habit with the same name","Habit `Read` archived","1. Add `Read`","name `Read`","Error `A habit with this name already exists.` (audit #6; approve or change)","approved default","P2",B),
 # ---- R3 toggle
 ("TC-TOG-001","R3","Toggle","Clicking today's cell marks done and updates count and status","Habit `Read` target 3; current week","1. Click today's cell for Read","today","Cell `aria-pressed=true` with check mark; `1/3 this week`; status `Read done on <today>.`; streak `1 / best 1`","spec","P0",B),
 ("TC-TOG-002","R3","Toggle","Toggling twice returns to the original state","Same","1. Click today's cell twice","today","Cell `aria-pressed=false`, `0/3`; status `Read not done on <today>.`","spec","P0",B),
 ("TC-TOG-003","R3","Toggle","Done days survive a page reload","Habit with today done","1. Reload the page","-","Same cell still pressed; localStorage `habitly.v1` contains today in the log","spec","P0",B),
 ("TC-TOG-004","R3","Toggle","Future-day cells are disabled in the UI","Habit exists","1. Look at the cells after today in the current week (or next week)","next week","Cells for future days have `disabled`; clicking changes nothing","spec","P1",B),
 ("TC-TOG-005","R3","Toggle","Domain rejects future date, bad date, unknown habit; today allowed; log sorted","Node 22","1. Run existing R3 boundary and negative tests","tomorrow; `2026-02-30`; unknown id","ValidationError for each; today accepted (`R3 boundary...`, `R3 negative...`)","spec","P1",A),
 ("TC-TOG-006","R3","Toggle","Year boundary: marking 2025-12-31 and 2026-01-01 works with the clock fixed at 2026-01-01","Habit exists; browser clock fixed 2026-01-01","1. Click the cell for 2025-12-31 2. Click the cell for 2026-01-01 (both are in the week 2025-12-29 to 2026-01-04)","dates `2025-12-31`, `2026-01-01`","Both cells pressed; week label `2025-12-29 to 2026-01-04`","spec","P2",B),
 ("TC-TOG-007","R3","Toggle","Keyboard Space and Enter toggle a focused cell and focus stays on it","Habit exists","1. Tab to today's cell 2. Press Space 3. Press Enter","-","State flips twice (done, undone); focus remains on the same cell","spec","P1",B),
 ("TC-TOG-008","R3","Toggle","Double-clicking a cell ends in the original state","Habit exists","1. Double-click today's cell","today","Cell not pressed, no error","code behavior","P2",B),
 # ---- R4 week
 ("TC-WEEK-001","R4","Week","Grid shows Mon-Sun headers and the week label for this week","Habit exists","1. Open the page","today","Headers `Mon dd` ... `Sun dd`; label `<Mon> to <Sun>` containing today; today header underlined","spec","P2",B),
 ("TC-WEEK-002","R4","Week","Previous / Next / This week buttons move by 7 days and return","Habit exists","1. Click Previous week 2. Click Next week twice 3. Click This week","-","Label shifts -7 then +7, +7; This week returns to the original label; status text announces each","spec","P2",B),
 ("TC-WEEK-003","R4","Week","Week of Fri 2026-11-27 runs Mon 11-23 to Sun 11-29; Sunday belongs to the previous Monday (domain)","Node 22","1. Run existing R4 tests","2026-11-27; a Sunday","Pass (`R4 happy`, `R4 boundary` tests)","spec","P2",A),
 ("TC-WEEK-004","R4","Week","weekCount counts only days in the viewed week; invalid dates rejected (domain)","Node 22","1. Run existing R4 weekCount and negative tests","dups; `2026-13-01`","Pass (`R4 boundary: weekCount...`, `R4 negative...`)","spec","P3",A),
 ("TC-WEEK-005","R4","Week","A tab left open past midnight keeps the old 'today' until re-render","Page open","1. Leave the tab open across local midnight 2. Look at the grid","-","Observe only (audit #3)","none","P3",M),
 # ---- R5 streak
 ("TC-STRK-001","R5","Streak","3-day run ending today shows current 3 / best 3","Node 22 / habit with 3 days","1. Run existing R5 happy test","3 consecutive days","current 3, best 3 (`R5 happy: 3-day run ending today`)","spec","P1",A),
 ("TC-STRK-002","R5","Streak","Today undone keeps yesterday's run; a missed day resets the current streak","Node 22","1. Run existing R5 boundary test","run to yesterday; gap","current keeps run; gap resets, best stays (`R5 boundary...`)","spec","P1",A),
 ("TC-STRK-003","R5","Streak","No logs gives 0 / best 0 in the UI","Habit with no days done","1. Look at the Streak column","-","`0 / best 0`","spec","P2",B),
 ("TC-STRK-004","R5","Streak","Streak across the year boundary in the UI","Browser clock fixed at 2026-01-01; habit exists","1. Mark 2025-12-31 and 2026-01-01","dates","Streak column `2 / best 2`","spec","P2",B),
 ("TC-STRK-005","R5","Streak","Streak column reflects today undone yesterday done","Habit; browser clock fixed 2026-01-01","1. Mark 2025-12-31 only","date","`1 / best 1` (today not done does not break it)","spec","P1",B),
 # ---- R6 backup
 ("TC-BKP-001","R6","Backup","Export then import round-trips equal state (domain)","Node 22","1. Run existing R6 happy test","sample state","Equal state after parse (`R6 happy`)","spec","P0",A),
 ("TC-BKP-002","R6","Backup","Export JSON button downloads `habitly-backup-<date>.json` with the habits","Habit with one done day","1. Click Export JSON 2. Read the downloaded file","-","File name matches; JSON has version 1, habits, log, exportedAt; status `Backup exported.`","spec","P1",B),
 ("TC-BKP-003","R6","Backup","Importing a valid backup into empty storage loads the habits","Empty storage; fixture `valid.json` (2 habits)","1. Choose the fixture in Import JSON file","fixtures/valid.json","Two rows appear; status `Imported 2 habits.`; stored in localStorage","spec","P0",B),
 ("TC-BKP-004","R6","Backup","Import over existing data asks for confirmation; cancel keeps data","Habit `Read` exists; fixture valid.json","1. Choose the fixture 2. Dismiss the confirm dialog","fixtures/valid.json","Dialog text `Importing replaces all current habits. Continue?`; after Cancel `Read` is still there, status `Import cancelled; your data is unchanged.`","spec","P0",B),
 ("TC-BKP-005","R6","Backup","Accepting the confirm replaces data","Habit `Read` exists","1. Choose valid.json 2. Accept the dialog","fixtures/valid.json","Only the fixture's habits remain","spec","P1",B),
 ("TC-BKP-006","R6","Backup","A non-JSON file is rejected and data is unchanged","Habit `Read` exists","1. Choose `notjson.json`","fixtures/notjson.json","Status `Import failed, your data is unchanged: Backup is not valid JSON.` (error style); `Read` still present","spec","P0",B),
 ("TC-BKP-007","R6","Backup","Wrong version and duplicate-id backups are rejected in the UI","Habit `Read` exists","1. Choose `badversion.json` 2. Choose `dupid.json`","fixtures","Messages `Unsupported backup version.` and `Duplicate habit id h1.`; data unchanged","spec","P1",B),
 ("TC-BKP-008","R6","Backup","Backup larger than 2,000,000 characters is rejected (domain)","Node 22","1. Run existing R6 negative test (malformed backups)","oversize text","`Backup file is too large.` (`R6 negative: malformed backups...`; check whether the oversize row is among them)","spec","P2",A),
 ("TC-BKP-009","R6","Backup","Empty habits list backup imports and unknown extra fields are dropped (domain)","Node 22","1. Run existing R6 boundary test","empty state; extra field","Pass (`R6 boundary...`)","spec","P2",A),
 ("TC-BKP-010","R6","Backup","Real OS file chooser and browser download dialog work with the keyboard","Real desktop browser","1. Use Import via the native picker 2. Use Export and save the file","-","Picker opens and file imports; download saved. Not drivable by the agent.","none","P3",M),
 # ---- R7 storage
 ("TC-STO-001","R7","Storage","Save then load round-trips (domain)","Node 22","1. Run existing R7 happy test","sample state","Equal state (`R7 happy`)","spec","P1",A),
 ("TC-STO-002","R7","Storage","Empty storage starts empty with no notice","Empty storage","1. Open the page","-","Empty message `No habits yet. Add one above.`; status empty","spec","P2",B),
 ("TC-STO-003","R7","Storage","Corrupt stored JSON is not lost: notice shown, copy kept under `habitly.v1.corrupt`","localStorage `habitly.v1` = `{not json`","1. Open the page 2. Read localStorage","`{not json`","Status error `Saved data was unreadable. A copy was kept; starting empty.`; `habitly.v1.corrupt` equals the original text","spec","P0",B),
 ("TC-STO-004","R7","Storage","Parseable but invalid data (bad version) is treated as corrupt","Stored `{\"version\":2,\"habits\":[],\"log\":{}}`","1. Open the page","-","Same notice and corrupt copy","spec","P1",B),
 ("TC-STO-005","R7","Storage","Storage write failure is reported and the page keeps working","Page open; `setItem` made to throw","1. Make Storage.setItem throw 2. Add a habit","name `Q`","Error status `Could not save to this browser; changes will be lost on reload.`; row still appears in memory","spec","P1",B),
 ("TC-STO-006","R7","Storage","Page still opens when merely reading `localStorage` throws","Browser where `window.localStorage` getter throws","1. Open the page","-","Expected (proposed default, audit #1): page renders empty with `Storage is unavailable; changes will not be saved.`","approved default","P1",B),
 ("TC-STO-007","R7","Storage","Corrupt / invalid / throwing storage handled (domain)","Node 22","1. Run existing R7 negative tests","-","Pass (3 `R7 negative` tests)","spec","P1",A),
 # ---- R8 a11y / reflow
 ("TC-A11Y-001","R8","A11y","Keyboard-only: every control reachable in a logical order with visible focus","Habit exists","1. Press Tab from the page top through to the end","-","Skip link, form, week buttons, grid region, cells, Edit/Archive, Export, Import all reached; each shows a focus outline","spec","P1",B),
 ("TC-A11Y-002","R8","A11y","Grid cells are buttons with name and pressed state","Habit exists","1. Inspect a cell","-","`button[aria-pressed]` with `aria-label` like `Read, Mon 2026-11-23`","spec","P1",B),
 ("TC-A11Y-003","R8","A11y","Status uses a live region","Page open","1. Inspect `#status` 2. Add a habit","-","`role=status`, `aria-live=polite`; text updates without focus move","spec","P1",B),
 ("TC-A11Y-004","R8","A11y","At 360px width the page has no horizontal scroll","Viewport 360x740; several habits","1. Resize 2. Compare scrollWidth to clientWidth","360 px","documentElement.scrollWidth <= 360; grid scrolls inside its own region","spec","P1",B),
 ("TC-A11Y-005","R8","A11y","Screen reader announces status and cell names","Real screen reader","1. Toggle a cell with a screen reader running","-","Name and state announced, status announced (needs a real person/device)","spec","P2",M),
]

PRIO_ORDER = ["P0", "P1", "P2", "P3"]
rows = []
for c in C:
    assert len(c) == 11, c[0]
    rows.append("| " + " | ".join(x.replace("|", "\\|") for x in c) + " |")
ids = [c[0] for c in C]
assert len(ids) == len(set(ids))
pc = Counter(c[9] for c in C)
tc = Counter(c[10] for c in C)

REQS = {
 "R1": "Add habit (name 1-60 trimmed, target 1-7, reject invalid)",
 "R2": "Edit and archive/restore",
 "R3": "Toggle done/undone per local date",
 "R4": "Weekly grid and navigation, count vs target",
 "R5": "Current and best streak",
 "R6": "Backup export/import with validation",
 "R7": "Persistence, corrupt storage not overwritten silently",
 "R8": "Keyboard accessible, 360px reflow",
}
NEG = {
 "R1": ["TC-ADD-003","TC-ADD-005","TC-ADD-006","TC-ADD-007","TC-ADD-009"],
 "R2": ["TC-EDIT-004","TC-EDIT-007"],
 "R3": ["TC-TOG-004","TC-TOG-005"],
 "R4": ["TC-WEEK-004"],
 "R5": ["TC-STRK-002","TC-STRK-003"],
 "R6": ["TC-BKP-006","TC-BKP-007","TC-BKP-008"],
 "R7": ["TC-STO-003","TC-STO-004","TC-STO-005","TC-STO-006","TC-STO-007"],
 "R8": [],
}
rtm = []
full = 0
for r, desc in REQS.items():
    mine = [c for c in C if c[1] == r]
    neg = NEG[r]
    assert all(n in ids for n in neg)
    hap = [c[0] for c in mine if c[0] not in neg]
    cov = "Full" if hap and neg else ("Missing Negative" if hap else "Missing Happy")
    note = ""
    if r == "R8":
        note = "; Negative N/A: R8 is a quality requirement, its cases are checks that fail when the property is missing"
        cov = "Full"
    if cov == "Full":
        full += 1
    rtm.append(f"| {r} | {desc} | {', '.join(hap) or '-'} | {', '.join(neg) or 'N/A'} | N/A (single local user, no roles){note} | {cov} |")

old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
m = re.search(r"(?im)^- \*\*Status:\*\*.*$", old)
status = m.group(0) if m else "- **Status:** Draft"
ver = re.search(r"(?im)^- \*\*Version:\*\*.*$", old)
version = ver.group(0) if ver else "- **Version:** v0.1"

text = f"""# Test Matrix — habitly 1.0.0
- **Phase:** 2/5 — Test Matrix
- **Date:** 2026-11-27
{version}
{status}
- **Requirement source:** `qa-artifacts/habitly/01-test-plan.md` (Approved v0.2), `plan/003-habitly.md`
- **Approver:** [Needs input: approver name]

Generated by `qa-artifacts/habitly/tools/matrix_cases.py` (edit the case list there, then regenerate). Oracle `proposed default` = needs your acceptance below; once accepted it becomes `approved default`.

## 1. Overview
Cases: {len(C)} | P0: {pc['P0']} | P1: {pc['P1']} | P2: {pc['P2']} | P3: {pc['P3']} | Manual: {tc[M]} | Auto (browser): {tc[B]} | Auto (API): {tc[A]}
(Auto (API) = automated non-UI run: the developer's `node --test` suites mapped to cases; no HTTP API exists.)

## 2. Test Cases
| TC ID | Req/UC ID | Module | Title | Pre-condition | Test Steps | Test Data | Expected Result | Oracle | Priority | Execution Type |
|---|---|---|---|---|---|---|---|---|---|---|
""" + "\n".join(rows) + f"""

## 3. RTM (Requirement Traceability Matrix)
| Req/UC ID | Requirement | TC ID (Happy) | TC ID (Negative) | TC ID (Permission) | Coverage |
|---|---|---|---|---|---|
""" + "\n".join(rtm) + f"""

Total requirements: {len(REQS)} | Full: {full} | Coverage: {full / len(REQS) * 100:.0f}%
Orphan cases (no requirement): none.

Change log: v0.3 (2026-11-27) TC-TOG-006 steps corrected (the two dates share one week, no navigation needed). No change of intent, scope or counts; noted for the user at the next stop message.

## 4. Uncovered requirements / Notes
- Permission cases: N/A for every requirement (single local user, no accounts).
- Contradictions / clarifications (defaults in the plan, section 7): audit #1 (TC-STO-006), #6 (TC-EDIT-007), #9 (TC-ADD-012) have `proposed default` or `none` oracles.
- Non-functional cases (storage quota, large data) are in `02b-nonfunctional.md` with a separate approval.
- Cases that cannot be run by the agent: TC-BKP-010, TC-A11Y-005, TC-WEEK-005, TC-EDIT-006 (stay `Not Run` unless the user reports).
"""
OUT.write_text(text, encoding="utf-8")
print(f"wrote {OUT} cases={len(C)} P={dict(pc)} T={dict(tc)} rtm_full={full}/{len(REQS)}")

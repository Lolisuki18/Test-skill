# taskbox [Needs input: version; `taskbox/__init__.py` says 0.1.0, no tag exists] - [Needs input: release date]

Status: draft prepared from git history and `qa-artifacts/`. Not released: no tag, no deploy, nothing pushed.

## Highlights
- Adding or listing a task whose title has an emoji no longer crashes on a Windows cp1252 console.
- Titles with a line break are rejected instead of breaking the `list` table.

## Upgrade notes
- **Behavior change:** a title containing a control character (line break, tab, NUL, ESC) is now rejected: `error: title must not contain control characters`, exit 1, nothing saved. Before: `add $'line1\nline2'` was accepted.
- A data file that already holds a title with a control character will no longer load (error, exit 1; the file is not modified). No such file is known outside QA temp files; this was not tested with a stored file.
- Characters the console cannot print are shown as `?`. The data file keeps them. Set `PYTHONUTF8=1` to display them on a cp1252 setup.
- No new configuration, environment variable or data-format change.

## Fixes
- `add "Buy coffee <emoji>"` printed a traceback after saving the task (exit 1), and `list` failed on every call afterwards. Both commands now exit 0 (DEF-001).
- A title with a line break broke the `list` table (DEF-002).

## Known issues
- Not verified in a real interactive terminal (TC-ENC-005 Not Run); the fix was tested with piped output on code page cp1252 only.
- Two commands running at the same time can lose an update silently (TC-STORE-015, accepted in plan 001 section 8).
- A title with U+2028 (line separator) is still accepted.
- Only Python 3.14.6 on Windows 11 was tested (NF-COMP-01 Not Run); minimum Python version is undetermined.

Test evidence (round 2, build `81d0868`): 66 unit tests OK; scripted QA pass 66 Auto cases Pass; QA verdict Conditional Go (`qa-artifacts/05-summary-report.md`).

Full list of changes: `CHANGELOG.md`, section Unreleased.

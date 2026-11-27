# habitly 1.0.0 - [Needs input: release date]

Status: on branch `feat/habitly`, not merged; no tag exists. The version comes from `habitly/package.json:3`.

## Highlights
- Add habits with a name and a weekly target, then tick the days you did them in a Monday-to-Sunday week table with a streak count for each habit.
- Archive habits you no longer follow and restore them later; their history is kept.
- Save your data as a JSON file and load it back; a file that cannot be used is rejected and your current data stays as it was.

## Fixes before the first release
- The page still opens when your browser blocks site data; it tells you that changes will not be saved instead of staying blank.
- Text boxes and empty day squares have a clearer outline, and the check mark is easier to read in the dark colour scheme.
- When a box is rejected (for example an empty name) it is outlined and the cursor moves into it.

## Known limitations
- Tested in one browser engine (Chromium) only. Not tested: a screen reader, the page left open across midnight, and the browser's own file dialog for **Import JSON file**.

## Upgrade notes
- None. This is the first version.

Your data is stored in the browser you use, on that computer only. Use **Export JSON** to move it.

Full list of changes: [habitly/CHANGELOG.md](../../habitly/CHANGELOG.md)

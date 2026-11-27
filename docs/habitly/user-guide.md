# habitly - Release Package & User Guides

## I. Record of Changes

| Date | A* / M, D | In charge | Change Description |
|---|---|---|---|
| 2026-11-27 | A | `[Needs input: author]` | First version, written for habitly 1.0.0 (commit `8ec8923`). |

*A - Added, M - Modified, D - Deleted

## II. Release Package & User Guides

### 1. Deliverable Package

| No. | Deliverable Item | Description |
|---|---|---|
| 1 | Source Codes | Folder `habitly/`, version 1.0.0 in `habitly/package.json`, commit `8ec8923` on branch `feat/habitly` (not merged, no tag) |
| 2 | Test Cases Document | Automated tests in `habitly/tests/` (`domain.test.js`, `persistence.test.js`) |

Rows for schedule, backlog, database scripts, final report, defects list, issues list and slides are left out: no such files exist for habitly in the repository.

### 2. Installation Guides

#### 2.1 System Requirements

- A web browser. `[Needs input: supported browsers - none declared in the repository]`
- To serve the page from your own computer: Python 3, or any other program that serves a folder as a website (the commands below were run with Python 3.14.6).

#### 2.2 Installation Instruction

There is nothing to install. Open a terminal in the `habitly` folder and run:

```bash
python -m http.server 8080
```

Then open http://localhost:8080/ in your browser. If the command stops with an error because port 8080 is already in use, use another port, for example `python -m http.server 8099`, and open http://localhost:8099/.

### 3. User Manual

#### 3.1 Overview

habitly lets you list the habits you want to build, tick the days you did each one, and see how many days in a row you have kept going. Everything you enter is saved in your browser on this computer. Nothing is sent anywhere.

The page has one screen with four areas, from top to bottom:

| Area | What it is for |
|---|---|
| **Add a habit** | Create a habit, or change an existing one |
| **Week of ...** | The week table where you tick days |
| **Archived** | Habits you put away, with a **Restore** button |
| **Backup** | **Export JSON** and **Import JSON file** |

A line of text under the title **habitly** tells you what just happened ("Habit added.") or what went wrong. Errors are shown in bold red.

[Screenshot: habitly page - the four areas and the status line under the title - circle in red: the status line]

Who can use it: anyone who opens the page. There are no accounts or roles.

#### 3.2 Add a habit

**Purpose:** create a habit you want to track.
**You need first:** a name (1 to 60 characters) and how many days a week you aim for (a whole number from 1 to 7).

1. In **Add a habit**, type the habit in **Name**.
2. In **Target days per week**, enter a number from 1 to 7. The box starts at 3.
   [Screenshot: Add a habit form - Name and Target days per week filled in - circle in red: the Add habit button]
3. Select **Add habit**.
   Result: you see "Habit added." and the habit appears as a new row in the week table.

**Common problems**

| You see | What it means and what to do |
|---|---|
| Name is required. | The name is empty or only spaces. Type a name. |
| Name must be at most 60 characters. | Shorten the name. |
| A habit with this name already exists. | Names are compared without regard to capital letters ("Read" and "read" are the same). Choose a different name. |
| Target must be a whole number from 1 to 7. | Enter 1, 2, 3, 4, 5, 6 or 7. An empty box, 0, 8 and 2.5 are rejected. |

When a message like this appears, nothing is added or changed.

[Screenshot: Add a habit form - a red error message under the title - circle in red: the status line]

#### 3.3 Tick a day

**Purpose:** record that you did a habit on a day.
**You need first:** at least one habit.

1. Find the habit's row in the week table. Each column is a day, Monday to Sunday, shown as day name and date number (for example "Fri 27"). The column for today has an underlined heading.
2. Select the square in the habit's row under the day you did it.
   Result: the square shows a check mark and you see "<habit name> done on <date>." (for example "Read done on 2026-11-27.").
   [Screenshot: week table - one ticked square - circle in red: the ticked square]
3. To undo, select the same square again. You see "<habit name> not done on <date>."

Notes:
- Squares for days after today are greyed out and cannot be selected.
- Under each habit name, "<n>/<target> this week" shows how many days you ticked in the shown week against your target (for example "2/3 this week").
- The **Streak** column shows "<current> / best <best>" (for example "2 / best 2"). Current is the number of days in a row ending today. If you have not ticked today yet, the run that ended yesterday still counts. Best is the longest run you have ever recorded.

#### 3.4 Look at another week

**Purpose:** see or tick days in an earlier or later week.

1. Above the week table, select **Previous week**, **Next week** or **This week**.
   Result: the heading **Week of** shows the Monday and Sunday dates (for example "2026-11-23 to 2026-11-29") and you see "Showing previous week.", "Showing next week." or "Showing this week."
   [Screenshot: week navigation buttons - circle in red: the Previous week button]

Days in a later week are greyed out because they are in the future.

#### 3.5 Change a habit

**Purpose:** rename a habit or change its target.

1. In the habit's row, select **Edit**.
   Result: the name and target move into the form, the button now reads **Save changes**, and you see "Editing <habit name>."
   [Screenshot: Add a habit form in edit mode - circle in red: the Save changes and Cancel edit buttons]
2. Change **Name** or **Target days per week**.
3. Select **Save changes**. You see "Habit updated."

To leave without saving, select **Cancel edit**. You see "Edit cancelled." The same messages as in 3.2 appear if the new values are not allowed. Your ticked days are not affected by a rename.

#### 3.6 Archive and restore a habit

**Purpose:** hide a habit you no longer follow without losing its history.

1. In the habit's row, select **Archive**. You see "Habit archived." The habit leaves the week table and appears under **Archived**.
2. To bring it back, find it under **Archived** and select **Restore**. You see "Habit restored."

Under **Archived**, "None" is shown when there are no archived habits.

[Screenshot: Archived area - one habit with a Restore button - circle in red: the Restore button]

#### 3.7 Save a backup file

**Purpose:** keep a copy of your habits, or move them to another browser.

1. Under **Backup**, select **Export JSON**.
   Result: your browser downloads a file named `habitly-backup-<date>.json` (for example `habitly-backup-2026-11-27.json`) and you see "Backup exported." `[Needs input: where the browser saves the file - depends on the browser's download settings]`
   [Screenshot: Backup area - circle in red: the Export JSON button]

#### 3.8 Restore from a backup file

**Purpose:** load habits from a file saved with **Export JSON**.
**You need first:** a backup file made by habitly.
**Warning:** importing replaces all habits you currently have in this browser.

1. Under **Backup**, select **Import JSON file** and choose the file.
2. If you already have habits, a question appears: "Importing replaces all current habits. Continue?" Select the browser's confirm button to go on, or cancel to stop. On cancel you see "Import cancelled; your data is unchanged."
   [Screenshot: confirmation question - circle in red: the confirm button]
3. Result: you see "Imported <n> habits." and the week table shows the imported habits. (With a single habit the page reads "Imported 1 habits.")

**Common problems**

If the file cannot be used, you see "Import failed, your data is unchanged: <reason>" and nothing changes. Reasons the page can give:

| Reason shown | What to do |
|---|---|
| Backup is not valid JSON. | The file is not a habitly backup or is damaged. Choose another file. |
| Unsupported backup version. | The file was not made by this version of habitly. |
| Backup file is too large. | The file is over 2,000,000 characters. Choose another file. |
| Backup must be a JSON object. / Backup has no habits list. / Backup has no log. | The file does not have the expected content. Choose another file. |
| Habit has a bad id. / Duplicate habit id <id>. / Habit <id> has a bad name. / Habit <id> has a bad target. / Habit <id> has a bad createdAt. / Habit entry is not an object. | An entry in the file is not valid. Choose another file or repair it. |
| Log refers to unknown habit <id>. / Log for <id> has a bad date. | The ticked days in the file are not valid. Choose another file. |

#### 3.9 Messages about saving

| You see | What it means |
|---|---|
| Saved data was unreadable. A copy was kept; starting empty. | When the page opened, the saved habits could not be read. The page starts with no habits and keeps a copy of the unreadable data in the browser. `[Needs input: how a user can get at that copy - no screen offers it]` |
| Storage is unavailable; changes will not be saved. | Your browser does not let the page save data. You can still use the page, but your habits are gone when you close it. |
| Could not save to this browser; changes will be lost on reload. | A change could not be saved. Export a backup if you can, because a reload will lose the change. |

#### 3.10 Using the keyboard

The page can be used without a mouse: press Tab to move between controls and Enter or Space to press a button. The week table scrolls sideways on a narrow screen. `[Needs input: screen-reader behaviour was not tested]`

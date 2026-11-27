# Sequence: import a backup file

Shows what happens when the user picks a JSON file in **Import JSON file**, including the cases where nothing changes.

```mermaid
sequenceDiagram
  autonumber
  actor U as User
  participant A as app.js
  participant B as backup.js
  participant S as storage.js
  participant L as localStorage
  U->>A: choose a file
  A->>B: parseBackup(text)
  alt text too large, not JSON or fails validateState
    B-->>A: throws Error(message)
    A-->>U: status "Import failed, your data is unchanged: message"
  else valid backup
    B-->>A: clean state
    alt habits exist and the user declines the confirm
      A-->>U: status "Import cancelled#59; your data is unchanged."
    else no habits yet, or the user accepts
      A->>S: save(localStorage, state)
      S->>L: setItem("habitly.v1", JSON)
      A-->>U: status "Imported N habits." and the grid is redrawn
    end
  end
```

*Figure 2: Sequence - import a backup*

The file input is cleared at the end in every branch (`ev.target.value = ''`).

Evidence: `habitly/src/ui/app.js:175-190`, `habitly/src/domain/backup.js:14-47`, `habitly/src/storage.js:41-48`.
Not rendered in this session (no Mermaid renderer available); syntax checked by hand.

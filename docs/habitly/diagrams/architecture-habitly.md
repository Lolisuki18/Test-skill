# Architecture: habitly modules

Shows which file imports which, and where data is kept.

```mermaid
flowchart LR
  %% Evidence: imports in habitly/src/ui/app.js:1-5, habitly/src/storage.js:1-2, habitly/src/domain/*.js; habitly/index.html:61
  user([User in a browser]) --> page["index.html<br/>loads src/ui/app.js as a module"]
  page --> app["src/ui/app.js<br/>DOM wiring and render"]
  app --> habits["domain/habits.js<br/>addHabit, editHabit, setArchived, toggleDone, isDone"]
  app --> dates["domain/dates.js<br/>localDateString, weekDays, addDays"]
  app --> streaks["domain/streaks.js<br/>currentStreak, bestStreak, weekCount"]
  app --> backup["domain/backup.js<br/>serialize, parseBackup"]
  app --> storage["storage.js<br/>load, save"]
  habits --> dates
  streaks --> dates
  backup --> dates
  backup --> habits
  storage --> habits
  storage --> backup
  storage -->|"getItem / setItem"| ls[("localStorage<br/>habitly.v1, habitly.v1.corrupt")]
  app -->|"download / file input"| json[/"habitly-backup-YYYY-MM-DD.json"/]
```

*Figure 1: Architecture - habitly modules*

`src/storage.js` receives the storage object as an argument (`load(store)`, `save(store, state)`); `app.js` passes `localStorage` (`habitly/src/ui/app.js:24,174`). Nothing in `src/domain/` touches the DOM or `localStorage`.

Evidence: `habitly/src/ui/app.js:1-5`, `habitly/src/storage.js:1-5`, `habitly/src/domain/backup.js:1-2`, `habitly/src/domain/habits.js:1`, `habitly/src/domain/streaks.js:1`, `habitly/index.html:61`, `habitly/src/ui/app.js:146-155`.
Not rendered in this session (no Mermaid renderer available); syntax checked by hand.

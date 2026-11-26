# Architecture: taskbox modules

```mermaid
flowchart LR
  user([User in a terminal]) -->|"python -m taskbox"| main["__main__.py"]
  main --> cli["cli.py<br/>build_parser, cmd_add, cmd_list, cmd_done, cmd_delete, main"]
  cli --> storage["storage.py<br/>resolve_path, load_tasks, save_tasks, StorageError"]
  cli --> models["models.py<br/>Task, validate_title, validate_priority, validate_due, due_sort_key"]
  storage --> models
  storage -->|"read / atomic write"| file[("tasks.json<br/>--file, TASKBOX_FILE or ~/.taskbox/tasks.json")]
```

Dependencies point one way: `cli` -> `storage` -> `models`; `cli` also imports `models` directly.
Evidence: imports in `taskbox/cli.py:10-20`, `taskbox/storage.py:11`; entry `taskbox/__main__.py:3-5`; path resolution `taskbox/storage.py:21-28`.
Not rendered in this session (no Mermaid renderer available).

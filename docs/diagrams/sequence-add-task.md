# Sequence: `taskbox add`

```mermaid
sequenceDiagram
  actor U as User
  participant C as cli.main / cmd_add
  participant M as models
  participant S as storage
  participant F as tasks.json
  U->>C: add "title" --priority --due
  C->>S: resolve_path(--file)
  C->>M: validate_title / validate_priority / validate_due
  alt invalid input
    M-->>C: ValidationError
    C-->>U: stderr "error: ...", exit 1
  else valid
    C->>S: load_tasks(path)
    S->>F: read_text (missing file = empty store)
    S-->>C: tasks, next_id
    C->>S: save_tasks(path, tasks, next_id + 1)
    S->>F: write temp file, os.replace
    C-->>U: "Added task N: title", exit 0
  end
```

Evidence: `taskbox/cli.py:105-112` (main), `taskbox/cli.py:54-62` (cmd_add), `taskbox/storage.py:31-80`. A `StorageError` from `load_tasks` or `save_tasks` is reported the same way as `ValidationError` (stderr, exit 1; `taskbox/cli.py:110-112`), omitted from the diagram to stay readable.
Not rendered in this session.

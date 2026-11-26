# Sequence: `taskbox add`

```mermaid
sequenceDiagram
  actor U as User
  participant C as cli.main / cmd_add
  participant M as models
  participant S as storage
  participant F as tasks.json
  U->>C: add "title" --priority --due
  C->>C: _make_output_safe (stdout/stderr errors=replace)
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

Evidence: `taskbox/cli.py:113-121` (main), `taskbox/cli.py:105-110` (_make_output_safe), `taskbox/cli.py:54-62` (cmd_add), `taskbox/models.py:60-70` (validate_title rejects control characters), `taskbox/storage.py:31-80`. A `StorageError` from `load_tasks` or `save_tasks` is reported the same way as `ValidationError` (stderr, exit 1; `taskbox/cli.py:119-121`), omitted from the diagram to stay readable.
Not rendered in this session.

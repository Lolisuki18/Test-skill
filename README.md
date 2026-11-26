# taskbox

A small command-line task tracker. Python 3, standard library only. Tasks are stored in a JSON file.

## Prerequisites

- Python 3. `[Cần bổ sung: minimum Python version - no pyproject.toml or CI file declares it; code uses `datetime.date.fromisoformat` (taskbox/models.py:83)]`. Verified on Python 3.14.6.
- No third-party packages; nothing to install.

## Usage

Run from the repo root.

```
python -m taskbox add "Write report" --priority high --due 2026-12-01
python -m taskbox list [--status todo|done] [--priority low|med|high] [--sort due]
python -m taskbox done 1
python -m taskbox delete 1
python -m taskbox --version
```

- Priority: `low`, `med` (default), `high`. Due date: `YYYY-MM-DD`, optional.
- `list --sort due` orders by due date; tasks without a due date come last.
- Filters in `list` combine with AND. `list` on an empty store prints `No tasks.`
- `done` on an already-done task prints `Task N is already done.` and exits 0.
- Ids are not reused after `delete`.

## Data file

| Setting | Purpose | Required | Default |
|---|---|---|---|
| `--file PATH` | data file for this run | no | see below |
| `TASKBOX_FILE` | data file when `--file` is not given | no | `~/.taskbox/tasks.json` |

Order of precedence: `--file`, then `$TASKBOX_FILE`, then `~/.taskbox/tasks.json`.
`--file` is a global option and must come before the command: `python -m taskbox --file tasks.json list`. Placed after the command, argparse rejects it (exit 2).

The file is created (with its folder) on the first write. A missing or empty file counts as no tasks. A file that is not valid UTF-8 or JSON, or has an unsupported version or structure, is never overwritten: the command prints `error: ...` and exits 1. See [ADR 001](docs/adr/001-json-file-atomic-writes.md) and [ADR 002](docs/adr/002-never-overwrite-corrupt-file.md).

## Exit codes

| Code | Meaning |
|---|---|
| 0 | ok |
| 1 | error: validation (empty title, bad due date), unknown id, unreadable or corrupt data file |
| 2 | bad command line (unknown option, invalid `--priority`/`--status` choice, non-integer id, missing command) |

## Project structure

| Path | Contents |
|---|---|
| `taskbox/models.py` | `Task` dataclass, validation, due-date sort key |
| `taskbox/storage.py` | JSON load/save, atomic write, `StorageError` |
| `taskbox/cli.py` | argument parser and command handlers |
| `taskbox/__main__.py` | `python -m taskbox` entry point |
| `tests/` | unittest suite (60 tests) |
| `plan/` | implementation plan (listed in `.gitignore`, not tracked by git) |

## Tests

```
python -m unittest discover -s tests -t .
```

Last run in this session: 60 tests, OK.

## Documentation

- [Diagrams](docs/diagrams/): architecture, task status, sequence of `add`
- [Architecture decisions](docs/adr/README.md)
- [Changelog](CHANGELOG.md)

License: `[Cần bổ sung: license - no LICENSE file in the repo]`

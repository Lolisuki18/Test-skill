# taskbox

A small command-line task tracker. Python 3, standard library only. Tasks are stored in a JSON file.

## Usage

```
python -m taskbox add "Write report" --priority high --due 2026-12-01
python -m taskbox list [--status todo|done] [--priority low|med|high] [--sort due]
python -m taskbox done 1
python -m taskbox delete 1
```

- Priority: `low`, `med` (default), `high`. Due date: `YYYY-MM-DD`, optional.
- `list --sort due` orders by due date; tasks without a due date come last.
- Data file: `--file PATH`, else `$TASKBOX_FILE`, else `~/.taskbox/tasks.json`.
- Exit codes: 0 ok, 1 error (validation, unknown id, unreadable/corrupt file), 2 bad command line.

## Tests

```
python -m unittest discover -s tests -t .
```

# Evidence list

| Fact | Source | Used in |
|---|---|---|
| Entry `python -m taskbox` | `taskbox/__main__.py:3-5` | README, architecture |
| Commands add/list/done/delete, options, choices | `taskbox/cli.py:22-44` | README |
| `--file` is a global option, must precede the command | `taskbox/cli.py:26`; run: `add x --file F` -> exit 2 "unrecognized arguments" | README |
| Path precedence `--file` > `$TASKBOX_FILE` > `~/.taskbox/tasks.json` | `taskbox/storage.py:21-28` | README, ADR 001 |
| Exit codes 0/1/2 | `taskbox/cli.py:105-112`; runs of bad id (2), unknown id (1), empty title (1), bad priority (2) | README |
| Atomic write (mkstemp same dir + `os.replace`) | `taskbox/storage.py:61-80` | ADR 001, sequence |
| Corrupt/non-UTF-8/nested file -> StorageError, file untouched | `taskbox/storage.py:31-58`; run with `{bad` file: exit 1, file still `{bad` | ADR 002 |
| Status only goes todo -> done | `taskbox/cli.py:84-87`, `taskbox/models.py:11,28` | state diagram |
| 60 tests pass | run `python -m unittest discover -s tests -t .` -> "Ran 60 tests ... OK" | README |
| Plan says 56 tests (stale) | `plan/001-taskbox.md` section 9 | not copied |
| `plan/` is git-ignored | `.gitignore:1` | README |
| 3 commits, no tags; remote URL | `git log`, `git tag`, `git remote -v` | CHANGELOG |
| Python 3.14.6 used for runs | `python --version` | README |

## [Cần bổ sung]
- Minimum Python version (no manifest/CI).
- License (no LICENSE file).
- Release version/date (no tag).
- Deciders and alternatives considered for ADR 001/002.

## Confirmed file list
README.md (modified); CHANGELOG.md, docs/_evidence.md, docs/diagrams/{architecture-taskbox,state-task-status,sequence-add-task}.md, docs/adr/{README,001-...,002-...}.md (created). Not created: docs/runbook.md, docs/api/*, docs/postmortems/*, SRS/SDD, user guide, PM reports (judged not applicable).

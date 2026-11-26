# Changelog

All notable changes to this project are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). No release has been tagged yet, so all work is under Unreleased.

## [Unreleased]

### Added
- `taskbox` command-line task tracker: `add`, `list` (filters `--status`, `--priority`, `--sort due`), `done`, `delete`, `--version`, and a data file chosen by `--file`, `$TASKBOX_FILE` or `~/.taskbox/tasks.json`. Tasks are stored in one JSON file written atomically (`b0fea6d`).

### Fixed
- A data file that is not valid UTF-8 (for example UTF-16 written by PowerShell `>`) now gives `error: ... is not valid UTF-8 ...` and exit code 1 instead of a Python traceback; the file is left unchanged (`9a50011`).
- A pathologically deeply nested JSON data file now gives the "not valid JSON" error and exit code 1 instead of a traceback (`ac9ee0a`).

<!-- Version number and date: [Cần bổ sung: release version and date; package declares __version__ = "0.1.0" in taskbox/__init__.py, no tag exists] -->
<!-- Comparison links omitted: no tags exist. Repository: https://github.com/Lolisuki18/Test-skill (git remote origin). -->

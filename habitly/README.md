# habitly

Habit tracker that runs in a web browser. You add habits, tick the days you did them in a Monday-to-Sunday week grid, and see streaks. Data is stored in the browser (`localStorage`, key `habitly.v1`) and can be exported to and imported from a JSON file.

## Tech stack

| Layer | Technology | Version |
|---|---|---|
| UI | HTML, CSS, vanilla JavaScript (ES modules, no build step) | n/a |
| Storage | browser `localStorage` | n/a |
| Tests | `node:test` (built into Node) | Node 22 (run with v22.23.2) |
| Static server | `python -m http.server` (any static server works) | Python 3 (run with 3.14.6) |

The project has no third-party dependencies (`package.json` lists none).

## Prerequisites

- A web browser. `[Needs input: supported browsers - none declared in the repo]`
- Node.js 22 to run the tests. `package.json` has no `engines` field.
- Python 3, or another static file server, to serve the folder. `[Needs input: opening index.html directly from disk was not tried]`

## Getting started

Nothing to install. Run in a terminal inside the `habitly/` folder:

```bash
python -m http.server 8080
```

Open http://localhost:8080/ in the browser.

If port 8080 is already in use, the command stops with an `OSError`. Pick another port, for example:

```bash
python -m http.server 8099
```

and open http://localhost:8099/ instead.

## Scripts

| Command | What it does |
|---|---|
| `npm test` | runs `node --test` (all files in `tests/`) |
| `npm run serve` | runs `python -m http.server 8080` |

## Project structure

```text
index.html          page shell: forms, week grid, archived list, backup controls
styles.css          layout, colour tokens, focus styles, narrow-screen rules
src/domain/         pure logic with no DOM: dates, habits, streaks, backup validation
src/storage.js      getStore (reads window.localStorage safely), load/save wrapper around a localStorage-like object
src/ui/app.js       DOM wiring and rendering
tests/              node:test suites (domain.test.js, persistence.test.js, contrast.test.js)
```

Notes:
- Weeks run Monday to Sunday.
- Dates are local calendar days written as `YYYY-MM-DD`.

## Testing

Run in a terminal inside the `habitly/` folder:

```bash
node --test
```

The suites cover the domain functions, backup validation, storage and the colour contrast of the tokens in `styles.css`. They do not drive the browser page. As of commit `1a50381` all tests pass.

## Documentation

- [User guide](../docs/habitly/user-guide.md)
- [Architecture decisions](../docs/habitly/adr/README.md)
- Diagrams: [architecture](../docs/habitly/diagrams/architecture-habitly.md), [import backup](../docs/habitly/diagrams/sequence-import-backup.md)
- [Changelog](CHANGELOG.md) and [release notes](../docs/habitly/release-notes.md)

## License

`[Needs input: license - no license file in habitly/]`

# habitly

Habit tracker. Vanilla JavaScript ES modules, no build step, no dependencies. Data lives in `localStorage` (key `habitly.v1`).

Run: `python -m http.server 8080` in this folder (or any static server), open http://localhost:8080/.
Test: `node --test` (Node 22).

Layout: `src/domain/` pure logic, `src/storage.js` localStorage wrapper, `src/ui/app.js` DOM shell.
Weeks run Monday to Sunday. Dates are local `YYYY-MM-DD`.

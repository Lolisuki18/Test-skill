import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

// R8 / DEF-002, DEF-003: WCAG contrast of the colour tokens in styles.css (1.4.3 text 4.5, 1.4.11 controls 3).
const css = readFileSync(new URL('../styles.css', import.meta.url), 'utf8');
const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
const lum = (hex) => { const n = parseInt(hex.slice(1), 16); return 0.2126 * lin(n >> 16) + 0.7152 * lin((n >> 8) & 255) + 0.0722 * lin(n & 255); };
const ratio = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };
const tokens = (block) => Object.fromEntries([...block.matchAll(/--([\w-]+):\s*(#[0-9a-fA-F]{6})/g)].map((m) => [m[1], m[2]]));
const light = tokens(css.match(/:root\s*\{([^}]*)\}/)[1]);
const dark = { ...light, ...tokens(css.match(/prefers-color-scheme:\s*dark\)\s*\{\s*:root\s*\{([^}]*)\}/)[1]) };

for (const [name, t] of [['light', light], ['dark', dark]]) {
  test(`R8 DEF-003: control border token is at least 3:1 against the page (${name})`, () => {
    assert.ok(t['control-line'], 'token --control-line exists');
    assert.ok(ratio(t['control-line'], t.bg) >= 3, `${t['control-line']} on ${t.bg} = ${ratio(t['control-line'], t.bg).toFixed(2)}`);
  });
  test(`R8 DEF-002: check mark on a done cell is at least 4.5:1 (${name})`, () => {
    assert.ok(t['done-fg'], 'token --done-fg exists');
    assert.ok(ratio(t['done-fg'], t.done) >= 4.5, `${t['done-fg']} on ${t.done} = ${ratio(t['done-fg'], t.done).toFixed(2)}`);
  });
}
test('R8 DEF-003: input and day-cell borders use --control-line, not the decorative --line', () => {
  assert.match(css, /input:not\(\[type=file\]\)\s*\{[^}]*border:\s*1px solid var\(--control-line\)/);
  assert.match(css, /\.cell\s*\{[^}]*border-color:\s*var\(--control-line\)/);
});

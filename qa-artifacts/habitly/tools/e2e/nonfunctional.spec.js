// Cases of qa-artifacts/habitly/02b-nonfunctional.md (approved). Measurements without a confirmed threshold are annotated 'informational'.
const { test, expect } = require('@playwright/test');
const { HabitlyPage, localDate } = require('./pages/HabitlyPage');

const note = (type, description) => test.info().annotations.push({ type, description });

function bigState(habits, days) {
  const end = new Date();
  const log = {};
  const hs = [];
  for (let i = 1; i <= habits; i += 1) {
    hs.push({ id: `h${i}`, name: `Habit ${i}`, target: 3, archived: false, createdAt: '2023-01-01' });
    log[`h${i}`] = [];
    for (let d = 0; d < days; d += 1) {
      const dt = new Date(end.getFullYear(), end.getMonth(), end.getDate() - d);
      log[`h${i}`].push(localDate(dt));
    }
    log[`h${i}`].sort();
  }
  return { version: 1, habits: hs, log };
}

test('NF-PERF-01: 50 habits x 1095 days renders and toggles (Proposed < 1000 ms each)', async ({ page }) => {
  const h = new HabitlyPage(page);
  await page.goto('/');
  const state = bigState(50, 1095);
  await page.evaluate((s) => localStorage.setItem('habitly.v1', s), JSON.stringify(state));
  const bytes = (await h.stored()).length;
  const t0 = Date.now();
  await page.reload();
  await expect(h.row('Habit 50')).toBeVisible();
  const render = Date.now() - t0;
  const cell = h.cells('Habit 1').first();
  const t1 = Date.now();
  await cell.click();
  await expect(page.getByRole('status')).toContainText('Habit 1');
  const toggle = Date.now() - t1;
  note('informational', `state ${bytes} chars; reload to last row visible ${render} ms; toggle to status ${toggle} ms (proposed limit 1000 ms, unconfirmed -> Informational)`);
});

test('NF-PERF-02: storage quota reached -> error shown, page keeps working', async ({ page }) => {
  const h = new HabitlyPage(page);
  await page.goto('/');
  const filled = await page.evaluate(() => {
    let n = 0;
    for (let size = 1_000_000; size >= 1; size = Math.floor(size / 2)) {
      for (;;) {
        try { localStorage.setItem(`fill${n}`, 'x'.repeat(size)); n += 1; } catch { break; }
      }
    }
    return n;
  });
  note('informational', `filler keys written until quota: ${filled}`);
  await h.add('Q', 3);
  await h.expectError('Could not save to this browser; changes will be lost on reload.');
  await expect(h.row('Q')).toBeVisible();
  await h.cell('Q', localDate()).click();
  await expect(h.cell('Q', localDate())).toHaveAttribute('aria-pressed', 'true');
});

for (const [label, size, expectOk] of [['1999000', 1_999_000, true], ['2000100', 2_000_100, false]]) {
  test(`NF-PERF-03: import of ${label} chars is ${expectOk ? 'accepted' : 'rejected as too large'}`, async ({ page }) => {
    const h = new HabitlyPage(page);
    await page.goto('/');
    const head = '{"version":1,"habits":[],"log":{},"pad":"';
    const tail = '"}';
    const buffer = Buffer.from(head + 'x'.repeat(size - head.length - tail.length) + tail);
    expect(buffer.length).toBe(size);
    const t0 = Date.now();
    await h.importInput.setInputFiles({ name: 'big.json', mimeType: 'application/json', buffer });
    if (expectOk) await expect(h.status).toHaveText('Imported 0 habits.');
    else await h.expectError('Backup file is too large.');
    note('informational', `import handled in ${Date.now() - t0} ms (proposed limit 3000 ms, unconfirmed)`);
  });
}

test('NF-SEC-01: hostile names stay text; __proto__ log key rejected', async ({ page }) => {
  const h = new HabitlyPage(page);
  await page.goto('/');
  const evil = { version: 1, habits: [{ id: 'h1', name: '<img src=x onerror=window.__pwn=1>', target: 3, archived: false, createdAt: '2026-11-01' }], log: {} };
  await h.importInput.setInputFiles({ name: 'evil.json', mimeType: 'application/json', buffer: Buffer.from(JSON.stringify(evil)) });
  await expect(h.status).toHaveText('Imported 1 habits.');
  await expect(page.locator('tbody img')).toHaveCount(0);
  expect(await page.evaluate(() => window.__pwn)).toBeUndefined();
  const proto = '{"version":1,"habits":[],"log":{"__proto__":["2026-11-01"]}}';
  page.once('dialog', (d) => d.accept());
  await h.importInput.setInputFiles({ name: 'proto.json', mimeType: 'application/json', buffer: Buffer.from(proto) });
  await h.expectError('Log refers to unknown habit __proto__.');
});

for (const [w, hgt] of [[360, 740], [768, 1024], [1280, 800]]) {
  test(`NF-COMP-01: no page-level horizontal scroll at ${w}x${hgt}`, async ({ page }) => {
    await page.setViewportSize({ width: w, height: hgt });
    const h = new HabitlyPage(page);
    await page.goto('/');
    for (const n of ['Read a long book every day', 'Meditate', 'Stretch and walk']) await h.add(n, 3);
    const m = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
    expect(m.sw, JSON.stringify(m)).toBeLessThanOrEqual(m.cw);
  });
}

// Round 2 (build 1a50381): re-check of NF-A11Y-01 findings A11Y-F1..F3 (DEF-002, DEF-003, DEF-004). Same case, automated for the re-test.
const CONTRAST_JS = () => {
  const parse = (s) => { const m = s.match(/[\d.]+/g).map(Number); return { r: m[0], g: m[1], b: m[2], a: m.length > 3 ? m[3] : 1 }; };
  const lin = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
  const L = (c) => 0.2126 * lin(c.r) + 0.7152 * lin(c.g) + 0.0722 * lin(c.b);
  const ratio = (a, b) => { const x = L(a), y = L(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  const bg = parse(getComputedStyle(document.body).backgroundColor);
  const cs = (s) => getComputedStyle(document.querySelector(s));
  const pressed = document.querySelector('.cell[aria-pressed=true]');
  return {
    input: ratio(parse(cs('#habit-name').borderTopColor), bg),
    cell: ratio(parse(cs('.cell').borderTopColor), bg),
    check: ratio(parse(getComputedStyle(pressed).color), parse(getComputedStyle(pressed).backgroundColor)),
  };
};
for (const scheme of ['light', 'dark']) {
  test(`NF-A11Y-01 (round 2): control borders >= 3:1 and check mark >= 4.5:1 (${scheme})`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: scheme });
    const h = new HabitlyPage(page);
    await page.goto('/');
    await h.add('Read', 3);
    await h.cell('Read', localDate()).click();
    const r = await page.evaluate(CONTRAST_JS);
    note('informational', `${scheme}: input ${r.input.toFixed(2)}, empty cell ${r.cell.toFixed(2)}, check mark ${r.check.toFixed(2)}`);
    expect(r.input, JSON.stringify(r)).toBeGreaterThanOrEqual(3);
    expect(r.cell, JSON.stringify(r)).toBeGreaterThanOrEqual(3);
    expect(r.check, JSON.stringify(r)).toBeGreaterThanOrEqual(4.5);
  });
}
test('NF-A11Y-01 (round 2): invalid submit marks the field, links the message and moves focus; a valid submit clears it', async ({ page }) => {
  const h = new HabitlyPage(page);
  await page.goto('/');
  await h.add('   ', 3);
  await h.expectError('Name is required.');
  await expect(h.name).toHaveAttribute('aria-invalid', 'true');
  await expect(h.name).toHaveAttribute('aria-describedby', 'status');
  await expect(h.name).toBeFocused();
  await h.add('Read', 9);
  await h.expectError('Target must be a whole number from 1 to 7.');
  await expect(h.target).toHaveAttribute('aria-invalid', 'true');
  await expect(h.target).toBeFocused();
  await expect(h.name).not.toHaveAttribute('aria-invalid', 'true');
  await h.add('Read', 3);
  await expect(h.status).toHaveText('Habit added.');
  await expect(h.target).not.toHaveAttribute('aria-invalid', 'true');
  await expect(h.target).not.toHaveAttribute('aria-describedby', 'status');
});

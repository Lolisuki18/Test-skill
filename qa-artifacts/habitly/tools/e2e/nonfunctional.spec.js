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

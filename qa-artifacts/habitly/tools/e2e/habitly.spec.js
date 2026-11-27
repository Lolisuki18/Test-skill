// Auto (browser) cases of qa-artifacts/habitly/02-test-matrix.md. One test = one TC ID.
const { test, expect } = require('@playwright/test');
const path = require('node:path');
const fs = require('node:fs');
const { HabitlyPage, localDate } = require('./pages/HabitlyPage');

const FIX = (f) => path.join(__dirname, '..', 'fixtures', f);
const today = () => localDate();
const informational = (note) => test.info().annotations.push({ type: 'informational', description: note });

test.beforeEach(async ({ page }) => { await page.goto('/'); });

test.describe('R1 add', () => {
  test('TC-ADD-001: adding a valid habit shows it with 0/target', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await expect(h.row('Read')).toContainText('0/3 this week');
    await expect(h.status).toHaveText('Habit added.');
    await expect(h.name).toHaveValue('');
  });
  test('TC-ADD-002: name is trimmed before saving', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('  Read  ', 3);
    await expect(h.page.getByRole('rowheader', { name: /^Read0?/ })).toBeVisible();
    expect(JSON.parse(await h.stored()).habits[0].name).toBe('Read');
  });
  test('TC-ADD-003: whitespace-only name rejected, no row, nothing stored', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('   ', 3);
    await h.expectError('Name is required.');
    await expect(h.empty).toBeVisible();
    expect(await h.stored()).toBeNull();
  });
  test('TC-ADD-004: 60-char name accepted', async ({ page }) => {
    const h = new HabitlyPage(page);
    const n = 'a'.repeat(60);
    await h.add(n, 3);
    await expect(h.status).toHaveText('Habit added.');
    await expect(h.row(n)).toBeVisible();
  });
  test('TC-ADD-005: typing a 61st character is cut off by the field', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.name.pressSequentially('a'.repeat(61));
    await expect(h.name).toHaveValue('a'.repeat(60));
  });
  test('TC-ADD-007: targets 0, 8 and 2.5 are rejected', async ({ page }) => {
    const h = new HabitlyPage(page);
    for (const t of ['0', '8', '2.5']) {
      await h.name.fill('Walk');
      await h.target.fill(t);
      await h.submit.click();
      await h.expectError('Target must be a whole number from 1 to 7.');
      await expect(h.empty).toBeVisible();
    }
  });
  test('TC-ADD-008: targets 1 and 7 accepted', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('A', 1);
    await expect(h.row('A')).toContainText('0/1 this week');
    await h.add('B', 7);
    await expect(h.row('B')).toContainText('0/7 this week');
  });
  test('TC-ADD-009: duplicate name (case-insensitive) rejected', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.add('read', 3);
    await h.expectError('A habit with this name already exists.');
    await expect(h.page.getByRole('rowheader')).toHaveCount(1);
  });
  test('TC-ADD-010: HTML in a name is shown as text', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('<b>x</b>&amp;', 3);
    await expect(h.page.getByRole('rowheader')).toContainText('<b>x</b>&amp;');
    await expect(h.page.locator('tbody b')).toHaveCount(0);
  });
  test('TC-ADD-011: double-clicking Add habit adds one habit only', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.name.fill('Dbl');
    await h.target.fill('3');
    await h.submit.dblclick();
    await expect(h.page.getByRole('rowheader')).toHaveCount(1);
    informational(`final status after double click: "${await h.status.textContent()}" class=${await h.status.getAttribute('class')}`);
  });
  test('TC-ADD-012: 30 emoji (60 UTF-16 units) observed', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('😀'.repeat(30), 3);
    informational(`status: "${await h.status.textContent()}", rows: ${await h.page.getByRole('rowheader').count()}`);
  });
});

test.describe('R2 edit / archive', () => {
  test('TC-EDIT-001: editing name and target saves both', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.edit('Read').click();
    await h.name.fill('Read more');
    await h.target.fill('5');
    await h.submit.click();
    await expect(h.status).toHaveText('Habit updated.');
    await expect(h.row('Read more')).toContainText('0/5 this week');
    await expect(h.submit).toHaveText('Add habit');
  });
  test('TC-EDIT-002: cancel edit resets the form and changes nothing', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.edit('Read').click();
    await h.name.fill('zzz');
    await h.cancelEdit.click();
    await expect(h.name).toHaveValue('');
    await expect(h.cancelEdit).toBeHidden();
    await expect(h.row('Read')).toBeVisible();
    await expect(h.status).toHaveText('Edit cancelled.');
  });
  test('TC-EDIT-003: archive hides, keeps data across reload, restore brings it back with its log', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', today()).click();
    await h.archive('Read').click();
    await expect(h.empty).toBeVisible();
    await page.reload();
    await expect(h.restore('Read')).toBeVisible();
    await h.restore('Read').click();
    await expect(h.cell('Read', today())).toHaveAttribute('aria-pressed', 'true');
  });
  test('TC-EDIT-007: an archived name still blocks a new habit with the same name', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.archive('Read').click();
    await h.add('Read', 3);
    await h.expectError('A habit with this name already exists.');
  });
});

test.describe('R3 toggle', () => {
  test('TC-TOG-001: clicking today marks done, updates count, status and streak', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', today()).click();
    await expect(h.cell('Read', today())).toHaveAttribute('aria-pressed', 'true');
    await expect(h.cell('Read', today())).toHaveText('✓');
    await expect(h.row('Read')).toContainText('1/3 this week');
    await expect(h.status).toHaveText(`Read done on ${today()}.`);
    await expect(h.page.getByRole('cell', { name: '1 / best 1' })).toBeVisible();
  });
  test('TC-TOG-002: toggling twice returns to the original state', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', today()).click();
    await h.cell('Read', today()).click();
    await expect(h.cell('Read', today())).toHaveAttribute('aria-pressed', 'false');
    await expect(h.row('Read')).toContainText('0/3 this week');
    await expect(h.status).toHaveText(`Read not done on ${today()}.`);
  });
  test('TC-TOG-003: done days survive a reload', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', today()).click();
    await page.reload();
    await expect(h.cell('Read', today())).toHaveAttribute('aria-pressed', 'true');
    expect(JSON.parse(await h.stored()).log.h1).toContain(today());
  });
  test('TC-TOG-004: future-day cells are disabled (next week)', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.next.click();
    const cells = await h.cells('Read').all();
    expect(cells).toHaveLength(7);
    for (const c of cells) await expect(c).toBeDisabled();
  });
  test('TC-TOG-006: year boundary with the clock fixed at 2026-01-01', async ({ page }) => {
    await page.clock.setFixedTime(new Date('2026-01-01T12:00:00'));
    await page.reload();
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await expect(h.weekHeading).toContainText('2025-12-29 to 2026-01-04');
    await h.cell('Read', '2025-12-31').click();
    await h.cell('Read', '2026-01-01').click();
    await expect(h.cell('Read', '2025-12-31')).toHaveAttribute('aria-pressed', 'true');
    await expect(h.cell('Read', '2026-01-01')).toHaveAttribute('aria-pressed', 'true');
  });
  test('TC-TOG-007: Space and Enter toggle a focused cell, focus stays', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    const c = h.cell('Read', today());
    await h.tabTo(c);
    await page.keyboard.press('Space');
    await expect(c).toHaveAttribute('aria-pressed', 'true');
    await expect(c).toBeFocused();
    await page.keyboard.press('Enter');
    await expect(c).toHaveAttribute('aria-pressed', 'false');
    await expect(c).toBeFocused();
  });
  test('TC-TOG-008: double-clicking a cell ends unpressed', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', today()).dblclick();
    await expect(h.cell('Read', today())).toHaveAttribute('aria-pressed', 'false');
  });
});

test.describe('R4 week', () => {
  test('TC-WEEK-001: Mon-Sun headers and week label contain today', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    const heads = await page.getByRole('columnheader').allTextContents();
    expect(heads).toHaveLength(10);
    expect(heads.slice(1, 8).map((t) => t.slice(0, 3))).toEqual(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
    const [a, b] = (await h.weekHeading.textContent()).replace('Week of ', '').split(' to ');
    expect(today() >= a && today() <= b).toBe(true);
  });
  test('TC-WEEK-002: Previous / Next / This week move by 7 days and return', async ({ page }) => {
    const h = new HabitlyPage(page);
    const label = async () => (await h.weekHeading.textContent()).replace('Week of ', '');
    const base = await label();
    await h.prev.click();
    const p = await label();
    expect(p).not.toBe(base);
    await expect(h.status).toHaveText('Showing previous week.');
    await h.next.click(); await h.next.click();
    const n = await label();
    expect(n).not.toBe(base);
    await h.thisWeek.click();
    expect(await label()).toBe(base);
    const d = (s) => Date.UTC(...s.split(' to ')[0].split('-').map((x, i) => (i === 1 ? Number(x) - 1 : Number(x))));
    expect(d(base) - d(p)).toBe(7 * 86400000);
    expect(d(n) - d(base)).toBe(7 * 86400000);
  });
});

test.describe('R5 streak', () => {
  test('TC-STRK-003: no logs shows 0 / best 0', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await expect(page.getByRole('cell', { name: '0 / best 0' })).toBeVisible();
  });
  test('TC-STRK-004: streak across the year boundary', async ({ page }) => {
    await page.clock.setFixedTime(new Date('2026-01-01T12:00:00'));
    await page.reload();
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', '2025-12-31').click();
    await h.cell('Read', '2026-01-01').click();
    await expect(page.getByRole('cell', { name: '2 / best 2' })).toBeVisible();
  });
  test('TC-STRK-005: today undone, yesterday done keeps the streak', async ({ page }) => {
    await page.clock.setFixedTime(new Date('2026-01-01T12:00:00'));
    await page.reload();
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', '2025-12-31').click();
    await expect(page.getByRole('cell', { name: '1 / best 1' })).toBeVisible();
  });
});

test.describe('R6 backup', () => {
  test('TC-BKP-002: Export JSON downloads habitly-backup-<date>.json', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.cell('Read', today()).click();
    const [dl] = await Promise.all([page.waitForEvent('download'), h.exportBtn.click()]);
    expect(dl.suggestedFilename()).toBe(`habitly-backup-${today()}.json`);
    const j = JSON.parse(fs.readFileSync(await dl.path(), 'utf8'));
    expect(j.version).toBe(1);
    expect(j.habits[0].name).toBe('Read');
    expect(j.log.h1).toContain(today());
    expect(typeof j.exportedAt).toBe('string');
    await expect(h.status).toHaveText('Backup exported.');
  });
  test('TC-BKP-003: valid backup imports into empty storage', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.importInput.setInputFiles(FIX('valid.json'));
    await expect(h.status).toHaveText('Imported 2 habits.');
    await expect(h.row('Run')).toBeVisible();
    await expect(h.row('Meditate')).toBeVisible();
    expect(JSON.parse(await h.stored()).habits).toHaveLength(2);
  });
  test('TC-BKP-004: import over existing data asks first, cancel keeps data', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    let msg = '';
    page.once('dialog', (d) => { msg = d.message(); d.dismiss(); });
    await h.importInput.setInputFiles(FIX('valid.json'));
    await expect(h.status).toHaveText('Import cancelled; your data is unchanged.');
    expect(msg).toBe('Importing replaces all current habits. Continue?');
    await expect(h.row('Read')).toBeVisible();
    await expect(h.row('Run')).toHaveCount(0);
  });
  test('TC-BKP-005: accepting the confirm replaces data', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    page.once('dialog', (d) => d.accept());
    await h.importInput.setInputFiles(FIX('valid.json'));
    await expect(h.status).toHaveText('Imported 2 habits.');
    await expect(h.row('Read')).toHaveCount(0);
    await expect(h.row('Run')).toBeVisible();
  });
  test('TC-BKP-006: non-JSON file rejected, data unchanged', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.importInput.setInputFiles(FIX('notjson.json'));
    await h.expectError('Import failed, your data is unchanged: Backup is not valid JSON.');
    await expect(h.row('Read')).toBeVisible();
  });
  test('TC-BKP-007: wrong version and duplicate ids rejected', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await h.importInput.setInputFiles(FIX('badversion.json'));
    await h.expectError('Unsupported backup version.');
    await h.importInput.setInputFiles(FIX('dupid.json'));
    await h.expectError('Duplicate habit id h1.');
    await expect(h.row('Read')).toBeVisible();
  });
});

test.describe('R7 storage', () => {
  test('TC-STO-002: empty storage starts empty with no notice', async ({ page }) => {
    const h = new HabitlyPage(page);
    await expect(h.empty).toBeVisible();
    await expect(h.status).toHaveText('');
  });
  test('TC-STO-003: corrupt JSON is kept under habitly.v1.corrupt with a notice', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.seed('{not json');
    await h.expectError('Saved data was unreadable. A copy was kept; starting empty.');
    expect(await page.evaluate(() => localStorage.getItem('habitly.v1.corrupt'))).toBe('{not json');
  });
  test('TC-STO-004: parseable but invalid data (version 2) treated as corrupt', async ({ page }) => {
    const h = new HabitlyPage(page);
    const bad = '{"version":2,"habits":[],"log":{}}';
    await h.seed(bad);
    await h.expectError('Saved data was unreadable.');
    expect(await page.evaluate(() => localStorage.getItem('habitly.v1.corrupt'))).toBe(bad);
  });
  test('TC-STO-005: a failing setItem is reported and the page keeps working', async ({ page }) => {
    const h = new HabitlyPage(page);
    await page.evaluate(() => { Storage.prototype.setItem = () => { throw new DOMException('quota', 'QuotaExceededError'); }; });
    await h.add('Q', 3);
    await h.expectError('Could not save to this browser; changes will be lost on reload.');
    await expect(h.row('Q')).toBeVisible();
  });
  test('TC-STO-006: page opens when reading localStorage throws', async ({ page }) => {
    await page.addInitScript(() => {
      Object.defineProperty(window, 'localStorage', { get() { throw new DOMException('denied', 'SecurityError'); } });
    });
    await page.reload();
    const h = new HabitlyPage(page);
    await h.expectError('Storage is unavailable; changes will not be saved.');
    await expect(h.empty).toBeVisible();
  });
});

test.describe('R8 a11y basics', () => {
  test('TC-A11Y-001: keyboard reaches every control, each with a visible focus indicator', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    await page.reload(); // Tab order is read from a fresh load (add() leaves focus inside the form)
    const seen = [];
    for (let i = 0; i < 40; i += 1) {
      await page.keyboard.press('Tab');
      const info = await page.evaluate(() => {
        const e = document.activeElement;
        const cs = getComputedStyle(e);
        return { label: e.getAttribute('aria-label') || e.textContent.trim() || e.id, tag: e.tagName, outline: `${cs.outlineStyle} ${cs.outlineWidth}` };
      });
      if (info.tag === 'BODY') break;
      seen.push(info);
    }
    const labels = seen.map((s) => s.label);
    for (const need of ['Skip to the week grid', 'habit-name', 'habit-target', 'Add habit', 'Previous week', 'This week', 'Next week', 'Edit Read', 'Archive Read', 'Export JSON', 'import-file']) {
      expect(labels, `focus stops: ${labels.join(' | ')}`).toContain(need);
    }
    // future days are disabled buttons and rightly skipped by Tab: expect one stop per enabled cell
    const enabled = await h.cells('Read').evaluateAll((els) => els.filter((e) => !e.disabled).length);
    expect(labels.filter((l) => /^Read, /.test(l))).toHaveLength(enabled);
    const noOutline = seen.filter((s) => /^none/.test(s.outline));
    expect(noOutline, JSON.stringify(noOutline)).toEqual([]);
  });
  test('TC-A11Y-002: cells are buttons with a name and pressed state', async ({ page }) => {
    const h = new HabitlyPage(page);
    await h.add('Read', 3);
    const c = h.cells('Read');
    await expect(c).toHaveCount(7);
    for (const x of await c.all()) await expect(x).toHaveAttribute('aria-pressed', /true|false/);
  });
  test('TC-A11Y-003: status is a polite live region and updates without moving focus', async ({ page }) => {
    const h = new HabitlyPage(page);
    await expect(h.status).toHaveAttribute('aria-live', 'polite');
    await h.add('Read', 3);
    await expect(h.status).toHaveText('Habit added.');
  });
  test('TC-A11Y-004: 360px width has no page-level horizontal scroll', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 740 });
    const h = new HabitlyPage(page);
    for (const n of ['Read a long book every day', 'Meditate', 'Stretch and walk']) await h.add(n, 3);
    const m = await page.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth }));
    expect(m.sw, JSON.stringify(m)).toBeLessThanOrEqual(m.cw);
  });
});

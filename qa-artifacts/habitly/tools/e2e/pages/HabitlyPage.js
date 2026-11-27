// Page object for habitly. Locators are based on index.html and src/ui/app.js (real DOM read, see notes).
// index.html:21-22 label "Name" / "Target days per week"; app.js:62-64 cell aria-label "<habit>, <Dow> <date>".
const { expect } = require('@playwright/test');

const pad = (n) => String(n).padStart(2, '0');
const localDate = (d = new Date()) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

class HabitlyPage {
  constructor(page) {
    this.page = page;
    this.name = page.getByLabel('Name', { exact: true });
    this.target = page.getByLabel('Target days per week');
    this.submit = page.getByRole('button', { name: /^(Add habit|Save changes)$/ });
    this.cancelEdit = page.getByRole('button', { name: 'Cancel edit' });
    this.status = page.getByRole('status');
    this.prev = page.getByRole('button', { name: 'Previous week' });
    this.next = page.getByRole('button', { name: 'Next week' });
    this.thisWeek = page.getByRole('button', { name: 'This week' });
    this.weekHeading = page.getByRole('heading', { name: /^Week of/ });
    this.exportBtn = page.getByRole('button', { name: 'Export JSON' });
    this.importInput = page.getByLabel('Import JSON file');
    this.empty = page.getByText('No habits yet. Add one above.');
  }

  async goto() { await this.page.goto('/'); }

  async add(name, target = 3) {
    await this.name.fill(name);
    await this.target.fill(String(target));
    await this.submit.click();
  }

  row(name) { return this.page.getByRole('row').filter({ has: this.page.getByRole('rowheader', { name: new RegExp(`^${escapeRe(name)}`) }) }); }
  cells(name) { return this.page.getByRole('button', { name: new RegExp(`^${escapeRe(name)}, \\w{3} \\d{4}-\\d{2}-\\d{2}$`) }); }
  cell(name, date) { return this.page.getByRole('button', { name: new RegExp(`^${escapeRe(name)}, \\w{3} ${date}$`) }); }
  edit(name) { return this.page.getByRole('button', { name: `Edit ${name}` }); }
  archive(name) { return this.page.getByRole('button', { name: `Archive ${name}` }); }
  restore(name) { return this.page.getByRole('button', { name: `Restore ${name}` }); }

  async stored() { return this.page.evaluate(() => localStorage.getItem('habitly.v1')); }
  async seed(state) {
    await this.page.evaluate((s) => localStorage.setItem('habitly.v1', s), typeof state === 'string' ? state : JSON.stringify(state));
    await this.page.reload();
  }
  async tabTo(locator, max = 80) {
    for (let i = 0; i < max; i += 1) {
      await this.page.keyboard.press('Tab');
      if (await locator.evaluate((el) => el === document.activeElement)) return i + 1;
    }
    throw new Error('tabTo: element never received focus by keyboard');
  }
  async expectError(text) {
    await expect(this.status).toHaveClass(/error/);
    await expect(this.status).toContainText(text);
  }
}

function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

module.exports = { HabitlyPage, localDate, pad };

// Dates are local calendar days as "YYYY-MM-DD" strings. Math is done in UTC
// on those strings so DST shifts can never move a day.
const RE = /^(\d{4})-(\d{2})-(\d{2})$/;

export function isValidDate(s) {
  if (typeof s !== 'string') return false;
  const m = RE.exec(s);
  if (!m) return false;
  const [y, mo, d] = [Number(m[1]), Number(m[2]), Number(m[3])];
  const dt = new Date(Date.UTC(y, mo - 1, d));
  return dt.getUTCFullYear() === y && dt.getUTCMonth() === mo - 1 && dt.getUTCDate() === d;
}

function toUtc(s) {
  if (!isValidDate(s)) throw new RangeError(`invalid date: ${s}`);
  const [y, m, d] = s.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d));
}

function fmt(dt) {
  const p = (n, w) => String(n).padStart(w, '0');
  return `${p(dt.getUTCFullYear(), 4)}-${p(dt.getUTCMonth() + 1, 2)}-${p(dt.getUTCDate(), 2)}`;
}

export function addDays(s, n) {
  const dt = toUtc(s);
  dt.setUTCDate(dt.getUTCDate() + n);
  return fmt(dt);
}

/** Today as a local YYYY-MM-DD string (from a JS Date in local time). */
export function localDateString(date = new Date()) {
  const p = (n, w = 2) => String(n).padStart(w, '0');
  return `${p(date.getFullYear(), 4)}-${p(date.getMonth() + 1)}-${p(date.getDate())}`;
}

/** Monday of the week containing s. */
export function weekStart(s) {
  const dow = toUtc(s).getUTCDay(); // 0 = Sunday
  return addDays(s, -((dow + 6) % 7));
}

export function weekDays(s) {
  const start = weekStart(s);
  return Array.from({ length: 7 }, (_, i) => addDays(start, i));
}

export function compareDates(a, b) {
  toUtc(a);
  toUtc(b);
  return a < b ? -1 : a > b ? 1 : 0;
}

import { addDays, weekDays } from './dates.js';

/**
 * Current streak: consecutive done days ending today, or ending yesterday if
 * today is not done yet (today is still open, so it does not break the run).
 */
export function currentStreak(days, today) {
  const set = new Set(days);
  let cursor = set.has(today) ? today : addDays(today, -1);
  let n = 0;
  while (set.has(cursor)) {
    n += 1;
    cursor = addDays(cursor, -1);
  }
  return n;
}

export function bestStreak(days) {
  const sorted = [...new Set(days)].sort();
  let best = 0;
  let run = 0;
  let prev = null;
  for (const d of sorted) {
    run = prev !== null && addDays(prev, 1) === d ? run + 1 : 1;
    if (run > best) best = run;
    prev = d;
  }
  return best;
}

/** Number of done days within the week (Mon-Sun) containing `date`. */
export function weekCount(days, date) {
  const week = new Set(weekDays(date));
  return new Set(days.filter((d) => week.has(d))).size;
}

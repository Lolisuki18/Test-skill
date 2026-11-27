import { emptyState } from './domain/habits.js';
import { validateState } from './domain/backup.js';

export const KEY = 'habitly.v1';
export const CORRUPT_KEY = 'habitly.v1.corrupt';

/**
 * `store` is any object with getItem/setItem (localStorage, or a fake in tests).
 * Returns { state, notice }. Corrupt data is copied to CORRUPT_KEY, never lost.
 */
export function load(store) {
  let text;
  try {
    text = store.getItem(KEY);
  } catch {
    return { state: emptyState(), notice: 'Storage is unavailable; changes will not be saved.' };
  }
  if (text === null || text === undefined) return { state: emptyState(), notice: null };
  try {
    return { state: validateState(JSON.parse(text)), notice: null };
  } catch {
    try {
      store.setItem(CORRUPT_KEY, text);
    } catch {
      /* nothing more we can do */
    }
    return { state: emptyState(), notice: 'Saved data was unreadable. A copy was kept; starting empty.' };
  }
}

/** Returns true when saved, false when storage failed. */
export function save(store, state) {
  try {
    store.setItem(KEY, JSON.stringify(state));
    return true;
  } catch {
    return false;
  }
}

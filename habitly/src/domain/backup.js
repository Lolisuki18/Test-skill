import { isValidDate } from './dates.js';
import { NAME_MAX } from './habits.js';

export const MAX_BACKUP_BYTES = 2_000_000;

export function serialize(state, now = new Date()) {
  return JSON.stringify({ ...state, exportedAt: now.toISOString() }, null, 2);
}

/**
 * Validate an untrusted value into a clean state. Throws Error with a
 * user-readable message; never returns partial data.
 */
export function validateState(raw) {
  if (raw === null || typeof raw !== 'object' || Array.isArray(raw)) throw new Error('Backup must be a JSON object.');
  if (raw.version !== 1) throw new Error('Unsupported backup version.');
  if (!Array.isArray(raw.habits)) throw new Error('Backup has no habits list.');
  if (raw.log === null || typeof raw.log !== 'object' || Array.isArray(raw.log)) throw new Error('Backup has no log.');
  const ids = new Set();
  const habits = raw.habits.map((h) => {
    if (h === null || typeof h !== 'object') throw new Error('Habit entry is not an object.');
    if (typeof h.id !== 'string' || !/^h\d+$/.test(h.id)) throw new Error('Habit has a bad id.');
    if (ids.has(h.id)) throw new Error(`Duplicate habit id ${h.id}.`);
    ids.add(h.id);
    if (typeof h.name !== 'string' || h.name.trim() === '' || h.name.length > NAME_MAX) throw new Error(`Habit ${h.id} has a bad name.`);
    if (!Number.isInteger(h.target) || h.target < 1 || h.target > 7) throw new Error(`Habit ${h.id} has a bad target.`);
    if (!isValidDate(h.createdAt)) throw new Error(`Habit ${h.id} has a bad createdAt.`);
    return { id: h.id, name: h.name.trim(), target: h.target, archived: h.archived === true, createdAt: h.createdAt };
  });
  const log = {};
  for (const [id, days] of Object.entries(raw.log)) {
    if (!ids.has(id)) throw new Error(`Log refers to unknown habit ${id}.`);
    if (!Array.isArray(days) || !days.every(isValidDate)) throw new Error(`Log for ${id} has a bad date.`);
    log[id] = [...new Set(days)].sort();
  }
  return { version: 1, habits, log };
}

export function parseBackup(text) {
  if (typeof text !== 'string') throw new Error('Backup is not text.');
  if (text.length > MAX_BACKUP_BYTES) throw new Error('Backup file is too large.');
  let raw;
  try {
    raw = JSON.parse(text);
  } catch {
    throw new Error('Backup is not valid JSON.');
  }
  return validateState(raw);
}

import { isValidDate, compareDates } from './dates.js';

export const NAME_MAX = 60;

export function emptyState() {
  return { version: 1, habits: [], log: {} };
}

export class ValidationError extends Error {}

function cleanName(name) {
  if (typeof name !== 'string') throw new ValidationError('Name must be text.');
  const n = name.trim();
  if (n.length === 0) throw new ValidationError('Name is required.');
  if (n.length > NAME_MAX) throw new ValidationError(`Name must be at most ${NAME_MAX} characters.`);
  return n;
}

function cleanTarget(target) {
  if (!Number.isInteger(target) || target < 1 || target > 7) {
    throw new ValidationError('Target must be a whole number from 1 to 7.');
  }
  return target;
}

function assertUniqueName(state, name, exceptId) {
  const low = name.toLowerCase();
  if (state.habits.some((h) => h.id !== exceptId && h.name.toLowerCase() === low)) {
    throw new ValidationError('A habit with this name already exists.');
  }
}

function nextId(state) {
  const nums = state.habits.map((h) => Number(h.id.slice(1))).filter(Number.isFinite);
  return `h${(nums.length ? Math.max(...nums) : 0) + 1}`;
}

/** Returns a new state; the input is never mutated. Throws ValidationError. */
export function addHabit(state, { name, target }, today) {
  const n = cleanName(name);
  const t = cleanTarget(target);
  assertUniqueName(state, n);
  const habit = { id: nextId(state), name: n, target: t, archived: false, createdAt: today };
  return { ...state, habits: [...state.habits, habit] };
}

function mapHabit(state, id, fn) {
  if (!state.habits.some((h) => h.id === id)) throw new ValidationError('Unknown habit.');
  return { ...state, habits: state.habits.map((h) => (h.id === id ? fn(h) : h)) };
}

export function editHabit(state, id, { name, target }) {
  const n = cleanName(name);
  const t = cleanTarget(target);
  assertUniqueName(state, n, id);
  return mapHabit(state, id, (h) => ({ ...h, name: n, target: t }));
}

export function setArchived(state, id, archived) {
  return mapHabit(state, id, (h) => ({ ...h, archived: Boolean(archived) }));
}

/** Toggle done for a date. Future dates are rejected. */
export function toggleDone(state, id, date, today) {
  if (!state.habits.some((h) => h.id === id)) throw new ValidationError('Unknown habit.');
  if (!isValidDate(date)) throw new ValidationError('Invalid date.');
  if (compareDates(date, today) > 0) throw new ValidationError('Cannot mark a future day.');
  const days = state.log[id] ?? [];
  const next = days.includes(date)
    ? days.filter((d) => d !== date)
    : [...days, date].sort();
  return { ...state, log: { ...state.log, [id]: next } };
}

export function isDone(state, id, date) {
  return (state.log[id] ?? []).includes(date);
}

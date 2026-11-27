import { test } from 'node:test';
import assert from 'node:assert/strict';
import { addDays, weekStart, weekDays, isValidDate, localDateString } from '../src/domain/dates.js';
import { emptyState, addHabit, editHabit, setArchived, toggleDone, isDone, ValidationError } from '../src/domain/habits.js';
import { currentStreak, bestStreak, weekCount } from '../src/domain/streaks.js';

const TODAY = '2026-11-27'; // a Friday
const mk = (name = 'Read', target = 3) => addHabit(emptyState(), { name, target }, TODAY);

// ---- R1
test('R1 happy: add habit trims name and assigns id', () => {
  const s = addHabit(emptyState(), { name: '  Read  ', target: 3 }, TODAY);
  assert.deepEqual(s.habits, [{ id: 'h1', name: 'Read', target: 3, archived: false, createdAt: TODAY }]);
});
test('R1 boundary: 60-char name and targets 1 and 7 accepted', () => {
  const s = addHabit(addHabit(emptyState(), { name: 'x'.repeat(60), target: 1 }, TODAY), { name: 'b', target: 7 }, TODAY);
  assert.equal(s.habits.length, 2);
});
test('R1 negative: invalid name or target rejected, state not mutated', () => {
  const base = mk();
  for (const bad of [{ name: '', target: 3 }, { name: '   ', target: 3 }, { name: 'x'.repeat(61), target: 3 },
    { name: 'a', target: 0 }, { name: 'a', target: 8 }, { name: 'a', target: 2.5 }, { name: 'a', target: '3' }, { name: 'a', target: NaN }, { name: 5, target: 3 }]) {
    assert.throws(() => addHabit(base, bad, TODAY), ValidationError);
  }
  assert.equal(base.habits.length, 1);
});
test('R1 negative: duplicate name is case-insensitive', () => {
  assert.throws(() => addHabit(mk('Read'), { name: 'rEAD', target: 2 }, TODAY), /already exists/);
});

// ---- R2
test('R2 happy: edit, archive and restore keep data', () => {
  let s = mk();
  s = editHabit(s, 'h1', { name: 'Read more', target: 5 });
  assert.equal(s.habits[0].name, 'Read more');
  assert.equal(s.habits[0].target, 5);
  s = setArchived(s, 'h1', true);
  assert.equal(s.habits[0].archived, true);
  s = setArchived(s, 'h1', false);
  assert.equal(s.habits[0].archived, false);
});
test('R2 boundary: renaming to its own name is allowed', () => {
  assert.doesNotThrow(() => editHabit(mk(), 'h1', { name: 'Read', target: 4 }));
});
test('R2 negative: unknown id and duplicate rename rejected', () => {
  assert.throws(() => editHabit(mk(), 'h9', { name: 'a', target: 1 }), /Unknown habit/);
  assert.throws(() => setArchived(mk(), 'h9', true), /Unknown habit/);
  const two = addHabit(mk('A'), { name: 'B', target: 1 }, TODAY);
  assert.throws(() => editHabit(two, 'h2', { name: 'a', target: 1 }), /already exists/);
});

// ---- R3
test('R3 happy: toggle twice returns to the original state', () => {
  const s = mk();
  const on = toggleDone(s, 'h1', '2026-11-26', TODAY);
  assert.equal(isDone(on, 'h1', '2026-11-26'), true);
  assert.deepEqual(toggleDone(on, 'h1', '2026-11-26', TODAY).log, { h1: [] });
});
test('R3 boundary: today allowed, tomorrow rejected, log kept sorted', () => {
  let s = toggleDone(mk(), 'h1', TODAY, TODAY);
  s = toggleDone(s, 'h1', '2025-12-31', TODAY);
  assert.deepEqual(s.log.h1, ['2025-12-31', TODAY]);
  assert.throws(() => toggleDone(s, 'h1', '2026-11-28', TODAY), /future/);
});
test('R3 negative: bad date or unknown habit rejected', () => {
  assert.throws(() => toggleDone(mk(), 'h1', '2026-02-30', TODAY), /Invalid date/);
  assert.throws(() => toggleDone(mk(), 'h1', 'yesterday', TODAY), /Invalid date/);
  assert.throws(() => toggleDone(mk(), 'zz', TODAY, TODAY), /Unknown habit/);
});

// ---- R4
test('R4 happy: week of Fri 2026-11-27 runs Mon 11-23 to Sun 11-29', () => {
  assert.equal(weekStart('2026-11-27'), '2026-11-23');
  assert.deepEqual(weekDays('2026-11-27'), ['2026-11-23', '2026-11-24', '2026-11-25', '2026-11-26', '2026-11-27', '2026-11-28', '2026-11-29']);
});
test('R4 boundary: Sunday belongs to the previous Monday; month and leap-year math', () => {
  assert.equal(weekStart('2026-11-29'), '2026-11-23');
  assert.equal(weekStart('2026-11-23'), '2026-11-23');
  assert.equal(addDays('2024-02-28', 1), '2024-02-29');
  assert.equal(addDays('2026-12-31', 1), '2027-01-01');
  assert.equal(addDays('2026-03-01', -1), '2026-02-28');
});
test('R4 boundary: weekCount counts only days inside the viewed week, ignoring duplicates', () => {
  assert.equal(weekCount(['2026-11-22', '2026-11-23', '2026-11-23', '2026-11-29', '2026-11-30'], '2026-11-25'), 2);
});
test('R4 negative: invalid dates throw / are detected', () => {
  assert.throws(() => weekStart('nope'), RangeError);
  assert.equal(isValidDate('2026-13-01'), false);
  assert.equal(isValidDate('2026-02-29'), false);
  assert.equal(isValidDate('2024-02-29'), true);
  assert.equal(isValidDate(20261127), false);
});
test('R4 happy: localDateString formats local date with padding', () => {
  assert.equal(localDateString(new Date(2026, 0, 5, 23, 59)), '2026-01-05');
});

// ---- R5
test('R5 happy: 3-day run ending today', () => {
  const d = ['2026-11-25', '2026-11-26', '2026-11-27'];
  assert.equal(currentStreak(d, TODAY), 3);
  assert.equal(bestStreak(d), 3);
});
test('R5 boundary: today not yet done keeps the run alive; a missed day resets it', () => {
  assert.equal(currentStreak(['2026-11-25', '2026-11-26'], TODAY), 2);
  assert.equal(currentStreak(['2026-11-24', '2026-11-25'], TODAY), 0);
  assert.equal(bestStreak(['2026-11-01', '2026-11-02', '2026-11-04', '2026-11-05', '2026-11-06']), 3);
  assert.equal(bestStreak(['2026-12-31', '2027-01-01']), 2);
});
test('R5 negative: no logs gives 0 and 0; duplicates not double counted', () => {
  assert.equal(currentStreak([], TODAY), 0);
  assert.equal(bestStreak([]), 0);
  assert.equal(bestStreak(['2026-11-01', '2026-11-01']), 1);
});

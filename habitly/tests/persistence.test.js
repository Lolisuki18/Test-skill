import { test } from 'node:test';
import assert from 'node:assert/strict';
import { emptyState, addHabit, toggleDone } from '../src/domain/habits.js';
import { serialize, parseBackup, validateState, MAX_BACKUP_BYTES } from '../src/domain/backup.js';
import { load, save, KEY, CORRUPT_KEY } from '../src/storage.js';

const TODAY = '2026-11-27';
const sample = () => toggleDone(addHabit(emptyState(), { name: 'Read', target: 3 }, TODAY), 'h1', '2026-11-26', TODAY);
const fakeStore = (init = {}) => {
  const m = new Map(Object.entries(init));
  return { getItem: (k) => (m.has(k) ? m.get(k) : null), setItem: (k, v) => m.set(k, v), m };
};
const clone = (o) => JSON.parse(JSON.stringify(o));

// ---- R6
test('R6 happy: export then import round-trips equal state', () => {
  const s = sample();
  assert.deepEqual(parseBackup(serialize(s, new Date('2026-11-27T10:00:00Z'))), s);
  assert.match(serialize(s, new Date('2026-11-27T10:00:00Z')), /"exportedAt": "2026-11-27T10:00:00.000Z"/);
});
test('R6 boundary: empty state and archived flag survive; unknown extra fields are dropped', () => {
  assert.deepEqual(parseBackup(serialize(emptyState())), emptyState());
  const raw = clone(sample());
  raw.habits[0].archived = true;
  raw.habits[0].evil = '<script>';
  assert.equal(validateState(raw).habits[0].archived, true);
  assert.equal('evil' in validateState(raw).habits[0], false);
});
test('R6 negative: malformed backups are rejected with a specific message', () => {
  const base = clone(sample());
  const cases = [
    ['not json{', /not valid JSON/],
    ['[]', /JSON object/],
    [JSON.stringify({ ...base, version: 2 }), /version/],
    [JSON.stringify({ ...base, habits: 'x' }), /habits/],
    [JSON.stringify({ ...base, habits: [base.habits[0], base.habits[0]] }), /Duplicate/],
    [JSON.stringify({ ...base, habits: [{ ...base.habits[0], target: 9 }] }), /target/],
    [JSON.stringify({ ...base, habits: [{ ...base.habits[0], name: ' ' }] }), /name/],
    [JSON.stringify({ ...base, log: { h1: ['2026-02-30'] } }), /bad date/],
    [JSON.stringify({ ...base, log: { h7: [] } }), /unknown habit/],
    ['x'.repeat(MAX_BACKUP_BYTES + 1), /too large/],
  ];
  for (const [text, re] of cases) assert.throws(() => parseBackup(text), re, text.slice(0, 40));
  assert.throws(() => parseBackup(null), /not text/);
});

// ---- R7
test('R7 happy: save then load round-trips', () => {
  const st = fakeStore();
  assert.equal(save(st, sample()), true);
  assert.deepEqual(load(st), { state: sample(), notice: null });
});
test('R7 boundary: empty storage gives empty state and no notice', () => {
  assert.deepEqual(load(fakeStore()), { state: emptyState(), notice: null });
});
test('R7 negative: corrupt data is kept under a backup key, not lost', () => {
  const st = fakeStore({ [KEY]: '{broken' });
  const r = load(st);
  assert.deepEqual(r.state, emptyState());
  assert.match(r.notice, /unreadable/);
  assert.equal(st.m.get(CORRUPT_KEY), '{broken');
});
test('R7 negative: invalid-but-parseable stored data is treated as corrupt', () => {
  const st = fakeStore({ [KEY]: JSON.stringify({ version: 1, habits: [{ id: 'x' }], log: {} }) });
  assert.match(load(st).notice, /unreadable/);
});
test('R7 negative: throwing storage degrades without throwing', () => {
  const bad = { getItem() { throw new Error('denied'); }, setItem() { throw new Error('full'); } };
  assert.match(load(bad).notice, /unavailable/);
  assert.equal(save(bad, emptyState()), false);
});

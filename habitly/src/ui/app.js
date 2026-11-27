import { emptyState, addHabit, editHabit, setArchived, toggleDone, isDone } from '../domain/habits.js';
import { localDateString, weekDays, addDays } from '../domain/dates.js';
import { currentStreak, bestStreak, weekCount } from '../domain/streaks.js';
import { serialize, parseBackup } from '../domain/backup.js';
import { load, save, getStore } from '../storage.js';

const $ = (id) => document.getElementById(id);
const DAY = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

let state = emptyState();
let anchor = localDateString(); // any day inside the viewed week
let editingId = null;
const store = getStore(); // null when even reading window.localStorage throws

const today = () => localDateString();

function say(msg, isError = false) {
  const el = $('status');
  el.textContent = msg;
  el.classList.toggle('error', isError);
}

function commit(next, msg) {
  state = next;
  if (!save(store, state)) say('Could not save to this browser; changes will be lost on reload.', true);
  else if (msg) say(msg);
  render();
}

function el(tag, props = {}, ...kids) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') e.className = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v);
  }
  for (const kid of kids) e.append(kid);
  return e;
}

function render() {
  const days = weekDays(anchor);
  const t = today();
  $('week-label').textContent = `${days[0]} to ${days[6]}`;

  const head = $('grid-head');
  head.replaceChildren();
  const hr = el('tr', {}, el('th', { scope: 'col' }, 'Habit'));
  days.forEach((d, i) => hr.append(el('th', { scope: 'col', class: d === t ? 'today' : '' }, `${DAY[i]} ${d.slice(8)}`)));
  hr.append(el('th', { scope: 'col' }, 'Streak'), el('th', { scope: 'col' }, 'Manage'));
  head.append(hr);

  const body = $('grid-body');
  body.replaceChildren();
  const active = state.habits.filter((h) => !h.archived);
  $('empty').hidden = active.length > 0;
  for (const h of active) {
    const log = state.log[h.id] ?? [];
    const row = el('tr', {});
    row.append(el('th', { scope: 'row' }, h.name, el('span', { class: 'meta' }, `${weekCount(log, anchor)}/${h.target} this week`)));
    days.forEach((d, i) => {
      const done = isDone(state, h.id, d);
      const b = el('button', {
        type: 'button', class: 'cell', 'aria-pressed': String(done),
        'aria-label': `${h.name}, ${DAY[i]} ${d}`, 'data-habit': h.id, 'data-date': d,
      }, done ? '✓' : '');
      if (d > t) b.disabled = true;
      b.addEventListener('click', () => onToggle(h.id, d));
      row.append(el('td', {}, b));
    });
    row.append(el('td', {}, `${currentStreak(log, t)} / best ${bestStreak(log)}`));
    row.append(el('td', {}, el('div', { class: 'actions' },
      el('button', { type: 'button', class: 'secondary', 'aria-label': `Edit ${h.name}`, onclick: () => startEdit(h.id) }, 'Edit'),
      el('button', { type: 'button', class: 'secondary', 'aria-label': `Archive ${h.name}`, onclick: () => onArchive(h.id, true) }, 'Archive'))));
    body.append(row);
  }

  const arch = $('archived');
  arch.replaceChildren();
  const archived = state.habits.filter((h) => h.archived);
  if (archived.length === 0) arch.append(el('li', {}, 'None'));
  for (const h of archived) {
    arch.append(el('li', {}, `${h.name} `, el('button', { type: 'button', class: 'secondary', 'aria-label': `Restore ${h.name}`, onclick: () => onArchive(h.id, false) }, 'Restore')));
  }
}

function guard(fn, onError) {
  try {
    fn();
  } catch (e) {
    say(e.message, true);
    if (onError) onError(e);
  }
}

const FIELDS = ['habit-name', 'habit-target'];
function clearInvalid() {
  for (const id of FIELDS) {
    $(id).removeAttribute('aria-invalid');
    $(id).removeAttribute('aria-describedby');
  }
}
function markInvalid(e) {
  const f = $(/^Target/.test(e.message) ? 'habit-target' : 'habit-name');
  f.setAttribute('aria-invalid', 'true');
  f.setAttribute('aria-describedby', 'status');
  f.focus();
}

function onToggle(id, date) {
  guard(() => {
    const h = state.habits.find((x) => x.id === id);
    const next = toggleDone(state, id, date, today());
    commit(next, `${h.name} ${isDone(next, id, date) ? 'done' : 'not done'} on ${date}.`);
    const b = document.querySelector(`button[data-habit="${id}"][data-date="${date}"]`);
    if (b) b.focus();
  });
}

function onArchive(id, archived) {
  guard(() => {
    commit(setArchived(state, id, archived), archived ? 'Habit archived.' : 'Habit restored.');
    $('habit-name').focus();
  });
}

function startEdit(id) {
  const h = state.habits.find((x) => x.id === id);
  editingId = id;
  $('habit-name').value = h.name;
  $('habit-target').value = String(h.target);
  $('habit-submit').textContent = 'Save changes';
  $('habit-cancel').hidden = false;
  $('habit-name').focus();
  say(`Editing ${h.name}.`);
}

function endEdit() {
  editingId = null;
  clearInvalid();
  $('habit-form').reset();
  $('habit-submit').textContent = 'Add habit';
  $('habit-cancel').hidden = true;
}

$('habit-form').addEventListener('submit', (ev) => {
  ev.preventDefault();
  clearInvalid();
  guard(() => {
    const raw = $('habit-target').value.trim();
    const input = { name: $('habit-name').value, target: raw === '' ? NaN : Number(raw) };
    const next = editingId ? editHabit(state, editingId, input) : addHabit(state, input, today());
    const verb = editingId ? 'updated' : 'added';
    endEdit();
    commit(next, `Habit ${verb}.`);
    $('habit-name').focus();
  }, markInvalid);
});
$('habit-cancel').addEventListener('click', () => { endEdit(); say('Edit cancelled.'); });
$('prev-week').addEventListener('click', () => { anchor = addDays(anchor, -7); render(); say('Showing previous week.'); });
$('next-week').addEventListener('click', () => { anchor = addDays(anchor, 7); render(); say('Showing next week.'); });
$('this-week').addEventListener('click', () => { anchor = today(); render(); say('Showing this week.'); });

$('export').addEventListener('click', () => {
  const blob = new Blob([serialize(state)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = el('a', { href: url, download: `habitly-backup-${today()}.json` });
  document.body.append(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
  say('Backup exported.');
});

$('import-file').addEventListener('change', async (ev) => {
  const file = ev.target.files[0];
  if (!file) return;
  try {
    const next = parseBackup(await file.text());
    if (state.habits.length > 0 && !window.confirm('Importing replaces all current habits. Continue?')) {
      say('Import cancelled; your data is unchanged.');
      ev.target.value = '';
      return;
    }
    commit(next, `Imported ${next.habits.length} habits.`);
  } catch (e) {
    say(`Import failed, your data is unchanged: ${e.message}`, true);
  }
  ev.target.value = '';
});

const loaded = load(store);
state = loaded.state;
render();
if (loaded.notice) say(loaded.notice, true);

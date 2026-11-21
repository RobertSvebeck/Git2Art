// Git2Art Museum, 2D: one room at a time, walked along the wall with arrow keys.

import { loadData, SculptureCanvas } from './sculptureCanvas.js';
import { LightCanvas } from './lightCanvas.js';
import { sculptureLines } from '../shared/repoform.js';

const $ = (id) => document.getElementById(id);
const rooms = [...document.querySelectorAll('.m2-room')];
const sculptures = new Map();
let current = -1;
let focus = 0;

document.body.classList.add('m2-js');

function items(room = rooms[current]) {
  return [...room.querySelectorAll('[data-item]')];
}

function labelIndex(room) {
  return items(room).findIndex((el) => el.classList.contains('m2-room-label'));
}

function openRoom(index, focusAt = null, push = true) {
  if (index < 0 || index >= rooms.length) return;
  if (current >= 0) rooms[current].classList.remove('active');
  current = index;
  const room = rooms[current];
  room.classList.add('active');
  $('m2-wing').textContent = room.dataset.wing;
  $('m2-room').textContent = room.dataset.name;
  document.title = `${room.dataset.name} | Git2Art Museum`;
  document.querySelectorAll('.m2-plan-room').forEach((el) => el.classList.toggle('current', el.dataset.room === room.id));
  if (push && location.hash !== `#${room.id}`) history.pushState(null, '', `#${room.id}`);
  wakeSculptures(room);
  setFocus(focusAt === 'end' ? items(room).length - 1 : focusAt ?? labelIndex(room), 'auto');
}

function setFocus(index, behavior = 'smooth') {
  const list = items();
  focus = Math.max(0, Math.min(list.length - 1, index));
  list.forEach((el, i) => el.classList.toggle('focused', i === focus));
  const target = list[focus];
  if (!target) return;
  target.scrollIntoView({ behavior, inline: 'center', block: 'nearest' });
  for (const [canvas, sculpture] of sculptures) sculpture.setActive(target.contains(canvas));
}

function step(direction) {
  const list = items();
  const target = list[focus + direction];
  if (!target) {
    const door = list[focus];
    if (door && door.classList.contains('m2-door')) enterDoor(door);
    return;
  }
  setFocus(focus + direction);
}

function enterDoor(door) {
  const id = door.getAttribute('href').slice(1);
  const index = rooms.findIndex((r) => r.id === id);
  const back = door.classList.contains('m2-door-back');
  openRoom(index, back ? 'end' : null);
}

function activate(el) {
  if (!el) return;
  if (el.classList.contains('m2-door')) enterDoor(el);
  else if (el.classList.contains('m2-work')) showWork(el);
}

async function showWork(figure) {
  const d = figure.dataset;
  const media = $('m2-panel-media');
  media.replaceChildren();
  $('m2-panel-title').textContent = d.title;
  $('m2-panel-style').textContent = d.style;
  $('m2-panel-likes').textContent = `${d.likes} ${d.likes === '1' ? 'like' : 'likes'}`;
  $('m2-panel-view').href = `/artwork/${d.id}`;
  $('m2-panel-view').textContent = figure.classList.contains('m2-sculpture') || figure.classList.contains('m2-light') ? 'View painting' : 'View artwork';
  $('m2-panel-repo').href = d.repo;
  $('m2-panel-stats').hidden = true;
  const living = figure.classList.contains('m2-sculpture') || figure.classList.contains('m2-light');
  if (living && d.data) {
    const light = figure.classList.contains('m2-light');
    const canvas = document.createElement('canvas');
    [canvas.width, canvas.height] = light ? [900, 600] : [560, 700];
    media.append(canvas);
    const data = await loadData(d.data);
    const big = light ? new LightCanvas(canvas, data) : new SculptureCanvas(canvas, data);
    big.setActive(true);
    sculptures.set(canvas, big);
    $('m2-panel-stats').textContent = sculptureLines(data).join('. ');
    $('m2-panel-stats').hidden = false;
  } else {
    const img = document.createElement('img');
    img.src = d.image;
    img.alt = `${d.title}, ${d.style}`;
    media.append(img);
  }
  $('m2-panel').hidden = false;
}

function closeOverlays() {
  for (const id of ['m2-panel', 'm2-plan']) $(id).hidden = true;
  for (const canvas of sculptures.keys()) if (!canvas.isConnected) sculptures.delete(canvas);
}

function overlayOpen() {
  return !$('m2-panel').hidden || !$('m2-plan').hidden;
}

function wakeSculptures(room) {
  room.querySelectorAll('.m2-sculpture canvas, .m2-light canvas').forEach((canvas) => {
    if (sculptures.has(canvas) || canvas.dataset.loading) return;
    canvas.dataset.loading = '1';
    const figure = canvas.closest('.m2-work');
    const url = figure.dataset.data;
    if (!url) return;
    const Kind = figure.classList.contains('m2-light') ? LightCanvas : SculptureCanvas;
    loadData(url).then((data) => {
      const work = new Kind(canvas, data);
      sculptures.set(canvas, work);
      work.setActive(items()[focus]?.contains(canvas));
    }).catch(() => {});
  });
}

document.addEventListener('keydown', (e) => {
  if (e.altKey || e.ctrlKey || e.metaKey) return;
  if (overlayOpen()) {
    if (e.key === 'Escape' || e.key === 'ArrowDown' || (e.key === 'm' && !$('m2-plan').hidden)) {
      closeOverlays();
      e.preventDefault();
    }
    return;
  }
  const keys = {
    ArrowRight: () => step(1),
    ArrowLeft: () => step(-1),
    ArrowUp: () => activate(items()[focus]),
    Enter: () => activate(items()[focus]),
    m: () => { $('m2-plan').hidden = false; },
    M: () => { $('m2-plan').hidden = false; },
  };
  if (keys[e.key]) {
    keys[e.key]();
    e.preventDefault();
  }
});

for (const room of rooms) {
  room.addEventListener('click', (e) => {
    const el = e.target.closest('[data-item]');
    if (!el) return;
    if (el.classList.contains('m2-door')) e.preventDefault();
    const index = items().indexOf(el);
    if (index === focus || el.classList.contains('m2-door')) activate(el);
    else setFocus(index);
  });
  const wall = room.querySelector('.m2-wall');
  wall.addEventListener('wheel', (e) => {
    if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
      wall.scrollLeft += e.deltaY;
      e.preventDefault();
    }
  }, { passive: false });
}

document.querySelectorAll('[data-close]').forEach((b) => b.addEventListener('click', closeOverlays));
document.querySelectorAll('.m2-overlay').forEach((o) => o.addEventListener('click', (e) => { if (e.target === o) closeOverlays(); }));
$('m2-plan-button').addEventListener('click', () => { $('m2-plan').hidden = false; });
document.querySelectorAll('.m2-plan-room').forEach((a) => a.addEventListener('click', (e) => {
  e.preventDefault();
  closeOverlays();
  openRoom(rooms.findIndex((r) => r.id === a.dataset.room));
}));
window.addEventListener('popstate', () => {
  const index = rooms.findIndex((r) => `#${r.id}` === location.hash);
  if (index >= 0 && index !== current) openRoom(index, null, false);
});

let last = performance.now();
function loop(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  for (const [canvas, sculpture] of sculptures) if (canvas.isConnected) sculpture.tick(dt);
  requestAnimationFrame(loop);
}

if (rooms.length) {
  const start = rooms.findIndex((r) => `#${r.id}` === location.hash);
  openRoom(start >= 0 ? start : 0, null, false);
  requestAnimationFrame(loop);
}

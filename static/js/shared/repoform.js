// Repository -> 3D form. Shared by the 3D museum (sculptures) and the 2D
// museum (drawings of the sculptures). Plain JS, no three.js dependency.
//
// Every position is a pure function of a path, so a small change in a repo is
// a small change in its form. Directories branch upwards and outwards from the
// root; files cluster around their directory.

const LANGUAGE_COLOURS = {
  '.py': '#4f8fe0', '.ipynb': '#f08a4b', '.js': '#f2d64b', '.mjs': '#f2d64b', '.jsx': '#f2d64b',
  '.ts': '#5aa2ff', '.tsx': '#5aa2ff', '.html': '#f06a3c', '.css': '#a77bf3', '.scss': '#e06aa8',
  '.vue': '#4fd39a', '.svelte': '#ff6a3d', '.java': '#e3a24a', '.kt': '#b18cff', '.scala': '#e5505f',
  '.go': '#3fd0e8', '.rs': '#f0b58a', '.c': '#9fb4c8', '.h': '#9fb4c8', '.cpp': '#f26a96', '.cc': '#f26a96',
  '.hpp': '#f26a96', '.cs': '#4cc26a', '.swift': '#ff7a52', '.m': '#6fa8ff', '.dart': '#3fd3c4',
  '.rb': '#e8475a', '.php': '#8e9cf0', '.lua': '#6a7cf5', '.r': '#4aa8f5', '.sh': '#9be36a',
  '.sql': '#f0a23a', '.json': '#e8c27a', '.yml': '#e9746a', '.yaml': '#e9746a', '.toml': '#d9a27a',
  '.xml': '#7ac0a8', '.md': '#d8ccb0', '.rst': '#d8ccb0', '.txt': '#bdb6a4',
};

export const LANGUAGE_NAMES = {
  '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript', '.jsx': 'JavaScript',
  '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS', '.java': 'Java', '.kt': 'Kotlin', '.go': 'Go',
  '.rs': 'Rust', '.c': 'C', '.cpp': 'C++', '.cs': 'C#', '.swift': 'Swift', '.rb': 'Ruby', '.php': 'PHP',
  '.md': 'Markdown', '.json': 'JSON', '.vue': 'Vue', '.svelte': 'Svelte', '.dart': 'Dart', '.sh': 'Shell',
};

export function hashUnit(text, salt = '') {
  let h = 2166136261;
  const s = `${salt}:${text}`;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  h ^= h >>> 15; h = Math.imul(h, 2246822507); h ^= h >>> 13; h = Math.imul(h, 3266489909); h ^= h >>> 16;
  return (h >>> 0) / 4294967296;
}

function hexToRgb(hex) {
  return [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255);
}

export function fileColour(path) {
  const dot = path.lastIndexOf('.');
  const ext = dot > path.lastIndexOf('/') ? path.slice(dot).toLowerCase() : '';
  if (LANGUAGE_COLOURS[ext]) {
    const rgb = hexToRgb(LANGUAGE_COLOURS[ext]);
    const jitter = (hashUnit(path, 'light') - 0.5) * 0.14;
    return rgb.map((c) => Math.min(1, Math.max(0, c + jitter)));
  }
  const hue = hashUnit(ext || 'none', 'hue');
  return hsvToRgb(hue, 0.3, 0.8);
}

function hsvToRgb(h, s, v) {
  const i = Math.floor(h * 6), f = h * 6 - i;
  const p = v * (1 - s), q = v * (1 - f * s), t = v * (1 - (1 - f) * s);
  return [[v, t, p], [q, v, p], [p, v, t], [p, q, v], [t, p, v], [v, p, q]][i % 6];
}

function parentDir(path) {
  const slash = path.lastIndexOf('/');
  return slash < 0 ? '' : path.slice(0, slash);
}

function depthOf(dir) {
  return dir === '' ? 0 : dir.split('/').length;
}

function dirPosition(dir, cache) {
  if (cache.has(dir)) return cache.get(dir);
  let position = [0, 0, 0];
  if (dir !== '') {
    const [px, py, pz] = dirPosition(parentDir(dir), cache);
    const depth = depthOf(dir);
    const azimuth = 2 * Math.PI * hashUnit(dir, 'az');
    const rise = 0.5 + 0.45 * hashUnit(dir, 'el');
    const spread = Math.sqrt(1 - rise * rise);
    const distance = 0.9 * 0.64 ** (depth - 1) * (0.7 + 0.3 * hashUnit(dir, 'dist'));
    position = [px + Math.cos(azimuth) * spread * distance, py + rise * distance, pz + Math.sin(azimuth) * spread * distance];
  }
  cache.set(dir, position);
  return position;
}

function filePosition(path, cache) {
  const dir = parentDir(path);
  const [cx, cy, cz] = dirPosition(dir, cache);
  const spread = 0.34 * 0.7 ** depthOf(dir);
  const u = hashUnit(path, 'u'), v = hashUnit(path, 'v');
  const theta = 2 * Math.PI * u, phi = Math.acos(2 * v - 1);
  const r = spread * (0.3 + 0.7 * Math.cbrt(hashUnit(path, 'r')));
  return [cx + r * Math.sin(phi) * Math.cos(theta), cy + Math.abs(r * Math.cos(phi)) * 0.8 + 0.04, cz + r * Math.sin(phi) * Math.sin(theta)];
}

// Returns stars (files) and branches (directory edges), normalised so the form
// stands on y = 0 and fits within the given height and radius.
export function buildForm(data, { height = 1.7, radius = 0.75 } = {}) {
  const cache = new Map();
  const files = data.files || [];
  const commits = Math.max(1, data.commits || 1);
  const totalBytes = files.reduce((sum, f) => sum + f[1], 0) || 1;
  const scale = Math.sqrt(0.022 / totalBytes);

  const stars = files.map(([path, bytes, born, touches]) => ({
    path,
    position: filePosition(path, cache),
    radius: Math.min(0.12, Math.max(0.009, scale * Math.sqrt(bytes))),
    colour: fileColour(path),
    born: born / commits,
    heat: Math.min(1, Math.log1p(touches) / Math.log1p(commits / 4 + 1)),
  }));

  const subtree = new Map();
  const dirBorn = new Map();
  for (const star of stars) {
    let dir = parentDir(star.path);
    while (true) {
      subtree.set(dir, (subtree.get(dir) || 0) + star.radius ** 2);
      dirBorn.set(dir, Math.min(dirBorn.get(dir) ?? 1, star.born));
      if (dir === '') break;
      dir = parentDir(dir);
    }
  }
  const branches = [];
  for (const [dir, weight] of subtree) {
    if (dir === '') continue;
    branches.push({
      from: dirPosition(parentDir(dir), cache),
      to: dirPosition(dir, cache),
      weight: Math.sqrt(weight),
      bend: hashUnit(dir, 'bend') - 0.5,
      born: dirBorn.get(dir),
    });
  }

  normalise(stars, branches, cache, height, radius);
  return { stars, branches, dirs: cache };
}

function normalise(stars, branches, cache, height, radius) {
  let minY = Infinity, maxY = -Infinity, maxR = 0, cx = 0, cz = 0;
  for (const s of stars) { cx += s.position[0]; cz += s.position[2]; }
  cx /= stars.length || 1; cz /= stars.length || 1;
  const points = [...stars.map((s) => [s.position, s.radius]), ...[...cache.values()].map((p) => [p, 0])];
  for (const [[x, y, z], r] of points) {
    minY = Math.min(minY, y - r);
    maxY = Math.max(maxY, y + r);
    maxR = Math.max(maxR, Math.hypot(x - cx, z - cz) + r);
  }
  const k = Math.min(height / Math.max(maxY - minY, 1e-6), radius / Math.max(maxR, 1e-6));
  const map = ([x, y, z]) => [(x - cx) * k, (y - minY) * k, (z - cz) * k];
  for (const s of stars) { s.position = map(s.position); s.radius *= k; }
  for (const [key, p] of cache) cache.set(key, map(p));
  for (const b of branches) { b.from = map(b.from); b.to = map(b.to); b.weight *= k; }
}

export function languageSummary(data, count = 3) {
  return Object.entries(data.languages || {})
    .filter(([ext]) => LANGUAGE_NAMES[ext])
    .slice(0, count)
    .map(([ext]) => LANGUAGE_NAMES[ext]);
}

export function sculptureLines(data) {
  const since = data.first_commit ? new Date(data.first_commit * 1000).getUTCFullYear() : null;
  const languages = languageSummary(data, 2).join(', ');
  const count = (n, noun) => `${n.toLocaleString('en-GB')} ${noun}${n === 1 ? '' : 's'}`;
  return [
    `${count(data.total_files, 'file')}, ${count(data.commits, 'commit')}`,
    [count(data.authors, 'author'), since ? `since ${since}` : null, languages || null].filter(Boolean).join(', '),
  ];
}

// Light installation: the commit history as a rising spiral of lights.
// Returns flat arrays: positions (x, y, z), colours (r, g, b), times (0..1), sizes.
export function commitField(data, { radius = 4.5, bottom = 0.5, top = 3.4, turns = 2.25, maxPoints = 9000 } = {}) {
  const timeline = data.timeline || [];
  const palette = languagePalette(data);
  const weights = timeline.map(([, changed]) => Math.min(70, Math.max(2, Math.round(Math.sqrt(changed) * 3))));
  const total = weights.reduce((a, b) => a + b, 0) || 1;
  const thin = Math.min(maxPoints / total, Math.max(1, 1800 / total));
  const positions = [], colours = [], times = [], sizes = [];
  const span = (Math.PI * 2 * turns) / Math.max(1, timeline.length);
  const rise = (top - bottom) / Math.max(1, timeline.length);
  timeline.forEach(([timestamp], i) => {
    const u = timeline.length > 1 ? i / (timeline.length - 1) : 0;
    const count = Math.max(1, Math.round(weights[i] * thin));
    for (let j = 0; j < count; j++) {
      const key = `${timestamp}:${i}:${j}`;
      const angle = u * Math.PI * 2 * turns + (hashUnit(key, 'a') - 0.5) * Math.max(0.18, span);
      const r = radius + (hashUnit(key, 'r') - 0.5) * 1.3;
      const y = bottom + u * (top - bottom) + (hashUnit(key, 'y') - 0.5) * Math.max(0.55, rise);
      positions.push(Math.cos(angle) * r, y, Math.sin(angle) * r);
      const colour = palette[Math.floor(hashUnit(key, 'c') * palette.length)];
      const glow = 0.55 + 0.45 * hashUnit(key, 'g');
      colours.push(colour[0] * glow, colour[1] * glow, colour[2] * glow);
      times.push(u);
      sizes.push(0.5 + 1.5 * hashUnit(key, 's') ** 3);
    }
  });
  return { positions, colours, times, sizes, count: times.length };
}

// Language colours weighted by bytes, so the light takes the repo's palette.
export function languagePalette(data, slots = 24) {
  const entries = Object.entries(data.languages || {}).filter(([, bytes]) => bytes > 0);
  const total = entries.reduce((sum, [, bytes]) => sum + bytes, 0);
  const palette = [];
  for (const [ext, bytes] of entries) {
    const share = Math.max(1, Math.round((bytes / total) * slots));
    for (let i = 0; i < share; i++) palette.push(fileColour(`x${ext}`));
  }
  return palette.length ? palette : [[0.7, 0.8, 1.0]];
}

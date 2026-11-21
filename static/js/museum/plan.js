// Room layout as a pure function of (world seed, cell). No three.js here.
//
// Rooms sit on an infinite grid with pitch CELL. Every room has a door in the
// middle of each wall and a half-corridor out to the cell boundary, where it
// meets the neighbour's half-corridor. Door size is global, so corridors line up.

import { MOODS, VOID_MOOD } from './moods.js';
import { Rng, hashInts } from './rng.js';

export const CELL = 26;
export const DOOR_WIDTH = 3.0;
export const DOOR_HEIGHT = 3.8;
export const WALL_THICKNESS = 0.3;
export const PLAYER_RADIUS = 0.35;

const WALL_END_MARGIN = 0.7;
const DOOR_MARGIN = 0.8;
const PIECE_GAP = 0.7;

export const WALLS = [
  // normal points into the room; along is the wall's horizontal axis
  { side: 'north', normal: [0, 1], along: [1, 0] },
  { side: 'south', normal: [0, -1], along: [-1, 0] },
  { side: 'east', normal: [-1, 0], along: [0, 1] },
  { side: 'west', normal: [1, 0], along: [0, -1] },
];

const planCache = new Map();

export function cellKey(cx, cz) {
  return `${cx},${cz}`;
}

export function cellOf(x, z) {
  return [Math.round(x / CELL), Math.round(z / CELL)];
}

export function planRoom(worldSeed, cx, cz) {
  const key = cellKey(cx, cz);
  if (planCache.has(key)) return planCache.get(key);
  const rng = new Rng(hashInts(worldSeed, cx, cz));
  const isEntrance = cx === 0 && cz === 0;
  const wing = wingOf(cx, cz);
  const isCourt = wing === 'sculpture';
  const isLight = wing === 'light';

  const mood = isLight ? VOID_MOOD : MOODS[isCourt ? courtMoodIndex(cx, cz) : moodIndex(worldSeed, cx, cz)];
  const width = round2(rng.range(13, 19));
  const depth = round2(rng.range(13, 19));
  const height = round2(rng.range(5.2, 7.6));
  const ceiling = rng.pick(mood.ceilings);
  const frame = rng.pick(mood.frames);
  const wallTint = rng.range(-0.05, 0.05);
  const pieceCount = isLight ? 0 : isCourt ? rng.int(4, 6) : rng.int(5, 10);
  const pieceHeight = Math.min(2.7, height * 0.4) * rng.range(0.85, 1.0);

  const furniture = [];
  if (isCourt) {
    for (const [sx, sz] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) {
      furniture.push({ type: 'plinth', x: sx * width * 0.24, z: sz * depth * 0.24, half: [0.62, 0.62] });
    }
  } else if (isLight) {
    // nothing to bump into: the installation is walked through
  } else if (!isEntrance && rng.chance(0.4)) {
    furniture.push({ type: 'abstract', x: 0, z: 0, half: [0.7, 0.7], shape: rng.int(0, 3), spin: rng.range(0.1, 0.3) });
    if (rng.chance(0.6)) {
      const along = rng.chance(0.5);
      const offset = (along ? width : depth) * 0.25;
      furniture.push(bench(along ? -offset : 0, along ? 0 : -offset, along));
      furniture.push(bench(along ? offset : 0, along ? 0 : offset, along));
    }
  } else if (!isEntrance && rng.chance(0.65)) {
    furniture.push(bench(0, 0, rng.chance(0.5)));
  }

  const plan = {
    cx, cz, key, wing, mood, width, depth, height, ceiling, frame, wallTint,
    accent: mood.accent, furniture,
    slots: planSlots(rng, width, depth, pieceCount, pieceHeight),
    seed: hashInts(worldSeed, cx, cz, 7),
  };
  planCache.set(key, plan);
  return plan;
}

export const WING_NAMES = { paintings: 'Painting Galleries', sculpture: 'Sculpture Court', light: 'Light Installations' };

// South of the entrance: sculpture court. East (and not south): light
// installations. Everything else: painting galleries.
export function wingOf(cx, cz) {
  if (cz > 0) return 'sculpture';
  if (cx > 0) return 'light';
  return 'paintings';
}

// Dark moods make the glowing sculptures read best; mod-4 lattice keeps
// neighbours different (steps of +-1 and +-3 are never 0 mod 4).
const COURT_MOODS = ['Nocturne', 'Graphite', 'Ultraviolet', 'Salon'].map((name) => MOODS.findIndex((m) => m.name === name));

function courtMoodIndex(cx, cz) {
  return COURT_MOODS[(((cx + 3 * cz) % 4) + 4) % 4];
}

// Lattice colouring: neighbours differ by +-1 or +-3 (mod 8), never 0, so
// adjacent rooms never share a mood. A per-world shuffle keeps visits different.
const moodOrders = new Map();

function moodIndex(worldSeed, cx, cz) {
  if (!moodOrders.has(worldSeed)) {
    const rest = new Rng(hashInts(worldSeed, 11)).shuffle(MOODS.map((_, i) => i).slice(1));
    moodOrders.set(worldSeed, [0, ...rest]);
  }
  const slot = (((cx + 3 * cz) % MOODS.length) + MOODS.length) % MOODS.length;
  return moodOrders.get(worldSeed)[slot];
}

function bench(x, z, alongX) {
  return { type: 'bench', x, z, alongX, half: alongX ? [1.2, 0.35] : [0.35, 1.2] };
}

function round2(value) {
  return Math.round(value * 100) / 100;
}

function planSlots(rng, width, depth, pieceCount, pieceHeight) {
  const segments = [];
  for (const wall of WALLS) {
    const length = wall.side === 'north' || wall.side === 'south' ? width : depth;
    const segment = length / 2 - DOOR_WIDTH / 2 - WALL_END_MARGIN - DOOR_MARGIN;
    const centre = DOOR_WIDTH / 2 + DOOR_MARGIN + segment / 2;
    segments.push({ wall, length, segment, offset: -centre });
    segments.push({ wall, length, segment, offset: centre });
  }

  const order = rng.shuffle(segments);
  const counts = new Map(order.map((s) => [s, 0]));
  for (let i = 0; i < Math.min(pieceCount, order.length); i++) counts.set(order[i], 1);
  const roomy = order.filter((s) => s.segment > 2 * 1.7 + PIECE_GAP).sort((a, b) => b.segment - a.segment);
  for (let i = 0; i < pieceCount - order.length && i < roomy.length; i++) counts.set(roomy[i], 2);

  const slots = [];
  for (const [segment, count] of counts) {
    for (let i = 0; i < count; i++) {
      const share = segment.segment / count;
      const offset = segment.offset - segment.segment / 2 + share * (i + 0.5);
      slots.push({
        side: segment.wall.side,
        normal: segment.wall.normal,
        along: segment.wall.along,
        wallLength: segment.length,
        offset,
        maxWidth: share - (count > 1 ? PIECE_GAP : 0.3),
        maxHeight: pieceHeight * rng.range(0.82, 1.0),
        centreY: 1.75 + rng.range(-0.05, 0.12),
      });
    }
  }
  return slots;
}

// Is a point free for the player? Rooms, plus N/S and E/W corridor strips.
export function isWalkable(worldSeed, x, z) {
  const [cx, cz] = cellOf(x, z);
  const plan = planRoom(worldSeed, cx, cz);
  const lx = x - cx * CELL;
  const lz = z - cz * CELL;
  const r = PLAYER_RADIUS;
  const inRoom = Math.abs(lx) < plan.width / 2 - WALL_THICKNESS / 2 - r
    && Math.abs(lz) < plan.depth / 2 - WALL_THICKNESS / 2 - r;
  if (inRoom) {
    for (const item of plan.furniture) {
      if (Math.abs(lx - item.x) < item.half[0] + r && Math.abs(lz - item.z) < item.half[1] + r) return false;
    }
    return true;
  }
  const corridorHalf = DOOR_WIDTH / 2 - r;
  return Math.abs(lx) < corridorHalf || Math.abs(lz) < corridorHalf;
}

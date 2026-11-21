// Streams rooms around the visitor and hangs art from a shuffled deck.

import { cellKey, cellOf, planRoom } from './plan.js';
import { buildRoom } from './room.js';
import { Rng, hashInts } from './rng.js';

const LOAD_RADIUS = 1;
const UNLOAD_RADIUS = 2;

class ArtDeck {
  constructor(artworks, seed) {
    this.artworks = artworks;
    this.rng = new Rng(seed);
    this.cards = [];
  }

  draw(count) {
    const hand = [];
    const ids = new Set();
    let guard = 0;
    while (hand.length < count && guard++ < count * 4) {
      if (this.cards.length === 0) this.cards = this.rng.shuffle(this.artworks);
      const card = this.cards.pop();
      if (ids.has(card.id) && this.artworks.length > count) continue;
      ids.add(card.id);
      hand.push(card);
    }
    return hand;
  }
}

export class World {
  constructor(scene, artworks, worldSeed) {
    this.scene = scene;
    this.worldSeed = worldSeed;
    this.deck = new ArtDeck(artworks, hashInts(worldSeed, 99));
    this.hung = new Map();
    this.rooms = new Map();
    this.queue = [];
    this.visited = new Set();
    this.current = null;
  }

  roomAt(x, z) {
    const [cx, cz] = cellOf(x, z);
    return this.rooms.get(cellKey(cx, cz)) || null;
  }

  // Returns the room the visitor is in when it changes, otherwise null.
  update(position) {
    const [cx, cz] = cellOf(position.x, position.z);
    const key = cellKey(cx, cz);
    let entered = null;
    if (!this.current || this.current.key !== key) {
      this.current = { cx, cz, key };
      this.visited.add(key);
      this.schedule(cx, cz);
      this.unloadFar(cx, cz);
      this.buildNow(cx, cz);
      entered = this.rooms.get(key);
    }
    if (this.queue.length) {
      const [qx, qz] = this.queue.shift();
      this.buildNow(qx, qz);
    }
    return entered;
  }

  schedule(cx, cz) {
    const wanted = [];
    for (let dx = -LOAD_RADIUS; dx <= LOAD_RADIUS; dx++) {
      for (let dz = -LOAD_RADIUS; dz <= LOAD_RADIUS; dz++) {
        if (!this.rooms.has(cellKey(cx + dx, cz + dz))) wanted.push([cx + dx, cz + dz, Math.abs(dx) + Math.abs(dz)]);
      }
    }
    wanted.sort((a, b) => a[2] - b[2]);
    this.queue = wanted.map(([x, z]) => [x, z]);
  }

  buildNow(cx, cz) {
    const key = cellKey(cx, cz);
    if (this.rooms.has(key)) return;
    const plan = planRoom(this.worldSeed, cx, cz);
    if (!this.hung.has(key)) this.hung.set(key, this.deck.draw(plan.slots.length));
    const room = buildRoom(plan, this.hung.get(key));
    this.scene.add(room.group);
    this.rooms.set(key, room);
  }

  unloadFar(cx, cz) {
    for (const [key, room] of this.rooms) {
      const far = Math.max(Math.abs(room.plan.cx - cx), Math.abs(room.plan.cz - cz)) > UNLOAD_RADIUS;
      if (far) {
        this.scene.remove(room.group);
        room.dispose();
        this.rooms.delete(key);
      }
    }
  }

  artMeshes() {
    const meshes = [];
    for (const room of this.rooms.values()) meshes.push(...room.artMeshes);
    return meshes;
  }

  tick(dt, time) {
    const room = this.current && this.rooms.get(this.current.key);
    if (room) for (const update of room.updaters) update(dt, time);
  }
}

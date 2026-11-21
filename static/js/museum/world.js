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
    if (this.artworks.length === 0) return [];
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
  constructor(scene, artworks, worldSeed, renderer, camera) {
    this.scene = scene;
    this.renderer = renderer;
    this.camera = camera;
    this.worldSeed = worldSeed;
    this.deck = new ArtDeck(artworks, hashInts(worldSeed, 99));
    this.byRepo = new Map();
    for (const artwork of artworks) {
      if (!this.byRepo.has(artwork.repo_url)) this.byRepo.set(artwork.repo_url, []);
      this.byRepo.get(artwork.repo_url).push(artwork);
    }
    const sculptures = [...this.byRepo.values()]
      .map((works) => works.find((w) => w.data))
      .filter(Boolean)
      .map((w) => ({ id: w.id, title: w.title, repo_url: w.repo_url, data: w.data, image: w.image, likes: w.likes }));
    this.sculptureDeck = new ArtDeck(sculptures, hashInts(worldSeed, 77));
    this.installationDeck = new ArtDeck(sculptures, hashInts(worldSeed, 55));
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
      if (this.current) this.rooms.get(this.current.key)?.rest();
      this.current = { cx, cz, key };
      this.visited.add(key);
      this.schedule(cx, cz);
      this.unloadFar(cx, cz);
      this.buildNow(cx, cz, true);
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

  // Neighbours stay hidden until their shaders are compiled, so they never stall a frame.
  buildNow(cx, cz, visibleNow = false) {
    const key = cellKey(cx, cz);
    if (this.rooms.has(key)) {
      this.rooms.get(key).group.visible = true;
      return;
    }
    const plan = planRoom(this.worldSeed, cx, cz);
    if (!this.hung.has(key)) this.hung.set(key, this.dealFor(plan));
    const room = buildRoom(plan, this.hung.get(key));
    room.group.visible = visibleNow;
    this.scene.add(room.group);
    this.rooms.set(key, room);
    if (!visibleNow) {
      this.renderer.compileAsync(room.group, this.camera, this.scene)
        .catch(() => {})
        .finally(() => { if (!room.disposed) room.group.visible = true; });
    }
  }

  dealFor(plan) {
    if (plan.wing === 'light') return { paintings: [], sculptures: [], installation: this.installationDeck.draw(1)[0] };
    if (plan.wing !== 'sculpture') return { paintings: this.deck.draw(plan.slots.length), sculptures: [] };
    const plinthCount = plan.furniture.filter((f) => f.type === 'plinth').length;
    const sculptures = this.sculptureDeck.draw(plinthCount);
    const paintings = sculptures.flatMap((s) => this.byRepo.get(s.repo_url) || []).slice(0, plan.slots.length);
    const ids = new Set(paintings.map((p) => p.id));
    for (const extra of this.deck.draw(plan.slots.length)) {
      if (paintings.length >= plan.slots.length) break;
      if (!ids.has(extra.id)) paintings.push(extra);
    }
    return { paintings, sculptures };
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

  roomContaining(mesh) {
    for (const room of this.rooms.values()) if (room.artMeshes.includes(mesh)) return room;
    return null;
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

// Builds the architecture of one room (walls, doors, corridors, floor, ceiling).

import * as THREE from 'three';
import { CELL, DOOR_HEIGHT, DOOR_WIDTH, WALL_THICKNESS as T, WING_NAMES, wingOf } from './plan.js';
import { addPlinths } from './court.js';
import { addInstallation } from './installation.js';
import { floorTexture, plasterTexture, signTexture } from './textures.js';
import { addArtAndFurniture } from './roomArt.js';
import { makeDust } from './lightfx.js';
import { mergeStatic } from './batch.js';
import { addArtistWalls } from './artist.js';

const CORRIDOR_FLOOR = 0x1c1b1a;

export function buildRoom(plan, hung) {
  const group = new THREE.Group();
  group.position.set(plan.cx * CELL, 0, plan.cz * CELL);
  const disposables = [];
  const track = (thing) => { disposables.push(thing); return thing; };

  const wallColour = new THREE.Color(plan.mood.wall).offsetHSL(0, 0, plan.wallTint);
  const materials = {
    wall: track(new THREE.MeshStandardMaterial({ color: wallColour, map: plasterTexture(), roughness: 0.92 })),
    trim: track(new THREE.MeshStandardMaterial({ color: plan.mood.trim, roughness: 0.6 })),
    ceiling: track(new THREE.MeshStandardMaterial({
      color: plan.ceiling === 'dark' ? new THREE.Color(plan.mood.trim).multiplyScalar(0.6) : wallColour.clone().offsetHSL(0, -0.05, 0.06),
      roughness: 0.95,
    })),
    corridor: track(new THREE.MeshStandardMaterial({ color: CORRIDOR_FLOOR, roughness: 0.8 })),
  };
  const box = (w, h, d, material, x, y, z) => {
    const mesh = new THREE.Mesh(track(new THREE.BoxGeometry(w, h, d)), material);
    mesh.position.set(x, y, z);
    group.add(mesh);
    return mesh;
  };

  addFloor(group, plan, track);
  addWalls(plan, materials, box);
  addCorridors(plan, materials, box, group, track);
  addCeiling(plan, materials, box, group, track);
  if (plan.accent) addAccentStrips(plan, box, track);

  const room = {
    plan, group, artMeshes: [], fixtures: [], updaters: [], disposed: false, rest: () => {},
  };
  addArtAndFurniture(room, hung.paintings, materials, track);
  if (plan.wing === 'sculpture') addPlinths(room, hung.sculptures, track);
  if (plan.wing === 'light') addInstallation(room, hung.installation, track);
  if (plan.artist) addArtistWalls(plan, group, track);
  else addWingSigns(plan, group, track);

  const dust = makeDust(plan.width - 1, plan.height, plan.depth - 1, 260, plan.mood.light);
  track(dust.geometry); track(dust.material);
  group.add(dust);
  room.updaters.push(dust.userData.update);

  for (const geometry of mergeStatic(group)) track(geometry);

  room.dispose = () => {
    room.disposed = true;
    for (const item of disposables) item.dispose();
    for (const release of room.releases || []) release();
  };
  return room;
}

function addFloor(group, plan, track) {
  const floor = floorTexture(plan.mood.floor);
  const geometry = track(new THREE.PlaneGeometry(plan.width, plan.depth));
  const uv = geometry.attributes.uv;
  for (let i = 0; i < uv.count; i++) {
    uv.setXY(i, uv.getX(i) * plan.width / floor.metres, uv.getY(i) * plan.depth / floor.metres);
  }
  const material = track(new THREE.MeshStandardMaterial({ map: floor.texture, roughness: floor.roughness, metalness: 0.0 }));
  const mesh = new THREE.Mesh(geometry, material);
  mesh.rotation.x = -Math.PI / 2;
  group.add(mesh);
}

// A wall with a centred door: two side pieces plus a lintel.
function wallWithDoor(length, height, place) {
  const side = (length - DOOR_WIDTH) / 2;
  place(side, height, -(DOOR_WIDTH / 2 + side / 2), height / 2);
  place(side, height, DOOR_WIDTH / 2 + side / 2, height / 2);
  place(DOOR_WIDTH, height - DOOR_HEIGHT, 0, DOOR_HEIGHT + (height - DOOR_HEIGHT) / 2);
}

function addWalls(plan, materials, box) {
  const { width: W, depth: D, height: H } = plan;
  for (const sign of [-1, 1]) {
    wallWithDoor(W + T, H, (len, h, offset, y) => box(len, h, T, materials.wall, offset, y, sign * D / 2));
    wallWithDoor(D + T, H, (len, h, offset, y) => box(T, h, len, materials.wall, sign * W / 2, y, offset));
    for (const along of [-1, 1]) {
      const segment = (W - DOOR_WIDTH) / 2;
      box(segment, 0.14, 0.04, materials.trim, along * (DOOR_WIDTH / 2 + segment / 2), 0.07, sign * (D / 2 - T / 2 - 0.02));
      const segmentD = (D - DOOR_WIDTH) / 2;
      box(0.04, 0.14, segmentD, materials.trim, sign * (W / 2 - T / 2 - 0.02), 0.07, along * (DOOR_WIDTH / 2 + segmentD / 2));
    }
    addDoorFrame(materials.trim, box, (dx, y, w, h) => [dx, y, sign * (D / 2 - T / 2 - 0.05), w, h, 0.1]);
    addDoorFrame(materials.trim, box, (dx, y, w, h) => [sign * (W / 2 - T / 2 - 0.05), y, dx, 0.1, h, w]);
  }
}

function addDoorFrame(material, box, orient) {
  const jamb = 0.16;
  const parts = [
    orient(-(DOOR_WIDTH / 2 + jamb / 2), DOOR_HEIGHT / 2, jamb, DOOR_HEIGHT),
    orient(DOOR_WIDTH / 2 + jamb / 2, DOOR_HEIGHT / 2, jamb, DOOR_HEIGHT),
    orient(0, DOOR_HEIGHT + jamb / 2, DOOR_WIDTH + jamb * 2, jamb),
  ];
  for (const [x, y, z, w, h, d] of parts) box(w, h, d, material, x, y, z);
}

function addCorridors(plan, materials, box, group, track) {
  const { width: W, depth: D } = plan;
  const strip = track(new THREE.MeshBasicMaterial({ color: new THREE.Color(plan.mood.light).multiplyScalar(2.2) }));
  const side = DOOR_WIDTH / 2 + T / 2;
  for (const sign of [-1, 1]) {
    const lenZ = CELL / 2 - D / 2;
    const midZ = sign * (D / 2 + lenZ / 2);
    for (const s of [-1, 1]) box(T, DOOR_HEIGHT, lenZ, materials.wall, s * side, DOOR_HEIGHT / 2, midZ);
    box(DOOR_WIDTH + 2 * T, T, lenZ, materials.ceiling, 0, DOOR_HEIGHT + T / 2, midZ);
    box(DOOR_WIDTH, 0.02, lenZ, materials.corridor, 0, 0.01, midZ);
    box(0.08, 0.02, lenZ, strip, 0, DOOR_HEIGHT - 0.01, midZ);

    const lenX = CELL / 2 - W / 2;
    const midX = sign * (W / 2 + lenX / 2);
    for (const s of [-1, 1]) box(lenX, DOOR_HEIGHT, T, materials.wall, midX, DOOR_HEIGHT / 2, s * side);
    box(lenX, T, DOOR_WIDTH + 2 * T, materials.ceiling, midX, DOOR_HEIGHT + T / 2, 0);
    box(lenX, 0.02, DOOR_WIDTH, materials.corridor, midX, 0.01, 0);
    box(lenX, 0.02, 0.08, strip, midX, DOOR_HEIGHT - 0.01, 0);
  }
}

function addCeiling(plan, materials, box, group, track) {
  const { width: W, depth: D, height: H } = plan;
  const ceiling = new THREE.Mesh(track(new THREE.PlaneGeometry(W, D)), materials.ceiling);
  ceiling.rotation.x = Math.PI / 2;
  ceiling.position.y = H;
  group.add(ceiling);

  if (plan.ceiling === 'skylight') {
    const glow = track(new THREE.MeshBasicMaterial({ color: new THREE.Color(plan.mood.sky).multiplyScalar(1.6) }));
    const sw = W * 0.42, sd = D * 0.42;
    const panel = new THREE.Mesh(track(new THREE.PlaneGeometry(sw, sd)), glow);
    panel.rotation.x = Math.PI / 2;
    panel.position.y = H - 0.02;
    group.add(panel);
    const bars = 4;
    for (let i = 0; i <= bars; i++) {
      box(0.08, 0.1, sd, materials.trim, -sw / 2 + (sw * i) / bars, H - 0.06, 0);
      box(sw, 0.1, 0.08, materials.trim, 0, H - 0.06, -sd / 2 + (sd * i) / bars);
    }
  } else if (plan.ceiling === 'coffered') {
    const step = 2.2;
    for (let x = -W / 2 + step; x < W / 2 - 0.5; x += step) box(0.22, 0.32, D, materials.trim, x, H - 0.16, 0);
    for (let z = -D / 2 + step; z < D / 2 - 0.5; z += step) box(W, 0.32, 0.22, materials.trim, 0, H - 0.16, z);
  } else if (plan.ceiling === 'beams') {
    for (let x = -W / 2 + 1.8; x < W / 2 - 0.8; x += 1.8) box(0.3, 0.45, D, materials.ceiling, x, H - 0.22, 0);
  }
}

function addAccentStrips(plan, box, track) {
  const { width: W, depth: D } = plan;
  const neon = track(new THREE.MeshBasicMaterial({ color: new THREE.Color(plan.accent).multiplyScalar(3.0) }));
  for (const sign of [-1, 1]) {
    for (const along of [-1, 1]) {
      const segment = (W - DOOR_WIDTH) / 2 - 0.4;
      box(segment, 0.035, 0.03, neon, along * (DOOR_WIDTH / 2 + 0.2 + segment / 2), 0.2, sign * (D / 2 - T / 2 - 0.03));
      const segmentD = (D - DOOR_WIDTH) / 2 - 0.4;
      box(0.03, 0.035, segmentD, neon, sign * (W / 2 - T / 2 - 0.03), 0.2, along * (DOOR_WIDTH / 2 + 0.2 + segmentD / 2));
    }
  }
}

const SIGN_SIDES = [
  { dx: 0, dz: -1, rotation: 0 },
  { dx: 0, dz: 1, rotation: Math.PI },
  { dx: 1, dz: 0, rotation: -Math.PI / 2 },
  { dx: -1, dz: 0, rotation: Math.PI / 2 },
];

// Above a door, name the wing beyond it when it differs (and always at the entrance).
function addWingSigns(plan, group, track) {
  const isEntrance = plan.cx === 0 && plan.cz === 0;
  for (const side of SIGN_SIDES) {
    const wing = wingOf(plan.cx + side.dx, plan.cz + side.dz);
    if (!isEntrance && wing === plan.wing) continue;
    const texture = track(signTexture(WING_NAMES[wing], new THREE.Color(plan.mood.wall).getHSL({}).l > 0.5));
    const material = track(new THREE.MeshBasicMaterial({ map: texture, transparent: true }));
    const sign = new THREE.Mesh(track(new THREE.PlaneGeometry(3.6, 0.45)), material);
    const inset = (side.dx !== 0 ? plan.width : plan.depth) / 2 - T / 2 - 0.02;
    sign.position.set(side.dx * inset, DOOR_HEIGHT + 0.5, side.dz * inset);
    sign.rotation.y = side.rotation;
    group.add(sign);
  }
}

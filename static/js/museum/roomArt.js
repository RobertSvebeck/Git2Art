// Artworks (frames, plaques, beams, halos) and furniture for one room.

import * as THREE from 'three';
import { FRAME_STYLES } from './moods.js';
import { WALL_THICKNESS as T } from './plan.js';
import { acquireArt, plaqueTexture, releaseArt } from './textures.js';
import { makeBeam, makeHalo } from './lightfx.js';

const FIXTURE_OUT = 2.3;
const PLAQUE_W = 0.36;
const PLAQUE_H = 0.1125;
const STYLE_LABELS = {
  expressionist: 'Expressionist', impressionist: 'Impressionist', watercolor: 'Watercolour',
  pixel: 'Pixel', face: 'Face', nature: 'Nature', psychedelic: 'Psychedelic', constellation: 'Constellation',
  sculpture: 'Repository sculpture',
};

export function styleLabel(style) {
  return STYLE_LABELS[style] || style;
}

export function addArtAndFurniture(room, artworks, materials, track) {
  const { plan, group } = room;
  room.releases = [];
  const frameSpec = FRAME_STYLES[plan.frame];
  const frameMaterial = track(new THREE.MeshStandardMaterial({
    color: frameSpec.color, metalness: frameSpec.metalness, roughness: frameSpec.roughness,
  }));
  const matMaterial = track(new THREE.MeshStandardMaterial({ color: 0xf7f5f0, roughness: 0.9 }));
  const fixtureMaterial = track(new THREE.MeshStandardMaterial({ color: 0x151515, metalness: 0.6, roughness: 0.4 }));
  const lensMaterial = track(new THREE.MeshBasicMaterial({ color: new THREE.Color(plan.mood.light).multiplyScalar(4) }));

  plan.slots.forEach((slot, index) => {
    const artwork = artworks[index % artworks.length];
    if (!artwork) return;
    const piece = buildPiece(room, slot, artwork, frameSpec, frameMaterial, matMaterial, track);
    addFixture(room, slot, piece, fixtureMaterial, lensMaterial, track);
  });

  for (const item of plan.furniture) {
    if (item.type === 'bench') addBench(group, item, materials, track);
    else if (item.type === 'abstract') addSculpture(room, item, materials, track);
  }
}

function slotTransform(plan, slot) {
  const wallDistance = (slot.side === 'north' || slot.side === 'south' ? plan.depth : plan.width) / 2 - T / 2;
  const [nx, nz] = slot.normal;
  const [ax, az] = slot.along;
  return {
    x: -nx * wallDistance + ax * slot.offset,
    z: -nz * wallDistance + az * slot.offset,
    rotationY: Math.atan2(nx, nz),
  };
}

function buildPiece(room, slot, artwork, spec, frameMaterial, matMaterial, track) {
  const { plan, group } = room;
  const aspect = artwork.aspect || 1;
  const inset = 2 * (spec.border + spec.mat);
  let height = Math.min(slot.maxHeight - inset, (slot.maxWidth - inset) / aspect);
  height = Math.max(0.6, height);
  const width = height * aspect;

  const { x, z, rotationY } = slotTransform(plan, slot);
  const piece = new THREE.Group();
  piece.position.set(x, slot.centreY, z);
  piece.rotation.y = rotationY;
  group.add(piece);

  const outerW = width + inset, outerH = height + inset;
  const frame = new THREE.Mesh(track(new THREE.BoxGeometry(outerW, outerH, spec.depth)), frameMaterial);
  frame.position.z = spec.depth / 2 + 0.02;
  piece.add(frame);
  let front = spec.depth + 0.021;
  if (spec.mat > 0) {
    const mat = new THREE.Mesh(track(new THREE.PlaneGeometry(width + 2 * spec.mat, height + 2 * spec.mat)), matMaterial);
    mat.position.z = front;
    piece.add(mat);
    front += 0.002;
  }

  const artMaterial = track(new THREE.MeshStandardMaterial({
    color: new THREE.Color(plan.mood.trim), roughness: 0.62, emissive: 0x000000,
  }));
  const art = new THREE.Mesh(track(new THREE.PlaneGeometry(width, height)), artMaterial);
  art.position.z = front;
  art.userData.artwork = artwork;
  piece.add(art);
  room.artMeshes.push(art);

  acquireArt(artwork.image).then((texture) => {
    if (room.disposed) return;
    artMaterial.map = texture;
    artMaterial.emissiveMap = texture;
    artMaterial.emissive.set(0xffffff);
    artMaterial.emissiveIntensity = 0.05;
    artMaterial.color.set(0xffffff);
    artMaterial.needsUpdate = true;
  }).catch(() => {});
  room.releases.push(() => releaseArt(artwork.image));

  const plaqueTex = track(plaqueTexture(artwork.title, `${styleLabel(artwork.style)}  |  git2art`));
  const plaque = new THREE.Mesh(
    track(new THREE.PlaneGeometry(PLAQUE_W, PLAQUE_H)),
    track(new THREE.MeshStandardMaterial({ map: plaqueTex, roughness: 0.7 })),
  );
  plaque.position.set(outerW / 2 + 0.25 + PLAQUE_W / 2, 1.38 - slot.centreY, 0.025);
  plaque.userData.artwork = artwork;
  piece.add(plaque);
  room.artMeshes.push(plaque);

  const halo = makeHalo(outerW * 2.0, outerH * 1.9, plan.mood.light, 0.07 * plan.mood.spot);
  track(halo.geometry); track(halo.material);
  halo.position.set(0, 0.15, 0.005);
  piece.add(halo);

  return { piece, width: outerW, height: outerH, art };
}

function addFixture(room, slot, built, fixtureMaterial, lensMaterial, track) {
  const { plan, group } = room;
  const { x, z } = slotTransform(plan, slot);
  const [nx, nz] = slot.normal;
  const target = new THREE.Vector3(x + nx * 0.05, slot.centreY + 0.1, z + nz * 0.05);
  const from = new THREE.Vector3(x + nx * FIXTURE_OUT, plan.height - 0.35, z + nz * FIXTURE_OUT);

  const rod = new THREE.Mesh(track(new THREE.CylinderGeometry(0.015, 0.015, 0.3)), fixtureMaterial);
  rod.position.set(from.x, plan.height - 0.15, from.z);
  group.add(rod);
  const direction = new THREE.Vector3().subVectors(target, from).normalize();
  const can = new THREE.Mesh(track(new THREE.CylinderGeometry(0.07, 0.1, 0.26, 20)), fixtureMaterial);
  can.position.copy(from);
  can.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), direction);
  group.add(can);
  const lens = new THREE.Mesh(track(new THREE.CircleGeometry(0.085, 20)), lensMaterial);
  lens.position.copy(from).addScaledVector(direction, 0.135);
  lens.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), direction);
  group.add(lens);

  const spread = Math.max(built.width, built.height) * 0.62;
  const beam = makeBeam(from, target, spread, plan.mood.light, 0.05 * plan.mood.spot);
  track(beam.geometry); track(beam.material);
  group.add(beam);

  room.fixtures.push({
    position: from.clone().add(group.position),
    target: target.clone().add(group.position),
    angle: Math.atan2(spread * 0.9, from.distanceTo(target)),
  });
}

function addBench(group, item, materials, track) {
  const bench = new THREE.Group();
  bench.position.set(item.x, 0, item.z);
  if (!item.alongX) bench.rotation.y = Math.PI / 2;
  const seatMaterial = track(new THREE.MeshStandardMaterial({ color: 0x2a211b, roughness: 0.45 }));
  const seat = new THREE.Mesh(track(new THREE.BoxGeometry(2.4, 0.1, 0.62)), seatMaterial);
  seat.position.y = 0.46;
  bench.add(seat);
  for (const s of [-1, 1]) {
    const leg = new THREE.Mesh(track(new THREE.BoxGeometry(0.08, 0.42, 0.56)), materials.trim);
    leg.position.set(s * 1.0, 0.21, 0);
    bench.add(leg);
  }
  group.add(bench);
}

function addSculpture(room, item, materials, track) {
  const { group, plan } = room;
  const plinth = new THREE.Mesh(
    track(new THREE.BoxGeometry(1.1, 1.0, 1.1)),
    track(new THREE.MeshStandardMaterial({ color: 0xefede8, roughness: 0.8 })),
  );
  plinth.position.set(item.x, 0.5, item.z);
  group.add(plinth);

  const geometries = [
    () => new THREE.TorusKnotGeometry(0.34, 0.11, 220, 32, 2, 3),
    () => new THREE.IcosahedronGeometry(0.55, 0),
    () => new THREE.TorusGeometry(0.42, 0.07, 32, 120),
    () => new THREE.OctahedronGeometry(0.55, 0),
  ];
  const material = track(new THREE.MeshPhysicalMaterial({
    color: plan.accent || 0xd9d9e0, metalness: 1.0, roughness: 0.12, clearcoat: 1.0, clearcoatRoughness: 0.08,
  }));
  const sculpture = new THREE.Group();
  sculpture.position.set(item.x, 1.65, item.z);
  const copies = item.shape === 2 ? 3 : 1;
  for (let i = 0; i < copies; i++) {
    const mesh = new THREE.Mesh(track(geometries[item.shape]()), material);
    mesh.rotation.set(i * 1.1, i * 0.7, 0);
    sculpture.add(mesh);
  }
  group.add(sculpture);
  room.updaters.push((dt) => {
    sculpture.rotation.y += item.spin * dt;
    sculpture.rotation.x += item.spin * 0.37 * dt;
  });
}

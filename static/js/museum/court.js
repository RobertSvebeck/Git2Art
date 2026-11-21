// Sculpture court: plinths carrying repository sculptures.

import * as THREE from 'three';
import { buildSculpture, loadRepoData } from './sculpture.js';
import { makeBeam } from './lightfx.js';
import { plaqueTexture } from './textures.js';
import { sculptureLines } from '../shared/repoform.js';

const PLINTH_HEIGHT = 0.9;
const PLINTH_SIZE = 1.0;
const SCULPTURE_HEIGHT = 2.0;

export function addPlinths(room, sculptures, track) {
  const { plan, group } = room;
  room.sculptures = [];
  const stone = track(new THREE.MeshPhysicalMaterial({ color: 0x111114, roughness: 0.35, clearcoat: 0.6, clearcoatRoughness: 0.25 }));
  const brass = track(new THREE.MeshStandardMaterial({ color: 0xb08d4c, metalness: 1.0, roughness: 0.3 }));
  const proxyMaterial = track(new THREE.MeshBasicMaterial({ visible: false }));
  const plinths = plan.furniture.filter((f) => f.type === 'plinth');

  plinths.forEach((item, index) => {
    const entry = sculptures[index];
    const base = new THREE.Mesh(track(new THREE.BoxGeometry(PLINTH_SIZE, PLINTH_HEIGHT, PLINTH_SIZE)), stone);
    base.position.set(item.x, PLINTH_HEIGHT / 2, item.z);
    group.add(base);
    const cap = new THREE.Mesh(track(new THREE.BoxGeometry(PLINTH_SIZE + 0.04, 0.03, PLINTH_SIZE + 0.04)), brass);
    cap.position.set(item.x, PLINTH_HEIGHT + 0.015, item.z);
    group.add(cap);
    addFixture(room, item, track);
    if (!entry) return;

    const info = { ...entry, style: 'sculpture', stats: '' };
    const proxy = new THREE.Mesh(track(new THREE.CylinderGeometry(1.0, 1.0, PLINTH_HEIGHT + SCULPTURE_HEIGHT, 12)), proxyMaterial);
    proxy.position.set(item.x, (PLINTH_HEIGHT + SCULPTURE_HEIGHT) / 2, item.z);
    proxy.userData.artwork = info;
    group.add(proxy);
    room.artMeshes.push(proxy);

    loadRepoData(entry.data).then((data) => {
      if (room.disposed) return;
      const lines = sculptureLines(data);
      info.stats = lines.join('. ');
      const sculpture = buildSculpture(data, { height: SCULPTURE_HEIGHT, radius: 1.05 });
      sculpture.position.set(item.x, PLINTH_HEIGHT + 0.03, item.z);
      sculpture.rotation.y = index * 1.3;
      group.add(sculpture);
      room.sculptures.push(sculpture);
      addPlaque(room, item, entry.title, ['Repository sculpture', ...lines], track);
    }).catch(() => addPlaque(room, item, entry.title, ['Repository sculpture'], track));
  });

  room.updaters.push((dt) => {
    for (const sculpture of room.sculptures) sculpture.userData.update(dt, true);
  });
  room.rest = () => {
    for (const sculpture of room.sculptures) sculpture.userData.update(0, false);
  };
  room.releases.push(() => {
    for (const sculpture of room.sculptures) sculpture.userData.dispose();
  });
}

function addPlaque(room, item, title, lines, track) {
  const texture = track(plaqueTexture(title, ...lines));
  const width = 0.7;
  const plaque = new THREE.Mesh(
    track(new THREE.PlaneGeometry(width, width / texture.userData.aspect)),
    track(new THREE.MeshStandardMaterial({ map: texture, roughness: 0.6 })),
  );
  const facing = item.z < 0 ? 1 : -1;
  plaque.position.set(item.x, PLINTH_HEIGHT * 0.62, item.z + facing * (PLINTH_SIZE / 2 + 0.005));
  plaque.rotation.y = facing > 0 ? 0 : Math.PI;
  room.group.add(plaque);
}

function addFixture(room, item, track) {
  const { plan, group } = room;
  const from = new THREE.Vector3(item.x, plan.height - 0.3, item.z);
  const target = new THREE.Vector3(item.x, PLINTH_HEIGHT + 0.6, item.z);
  const can = new THREE.Mesh(
    track(new THREE.CylinderGeometry(0.08, 0.11, 0.28, 20)),
    track(new THREE.MeshStandardMaterial({ color: 0x151515, metalness: 0.6, roughness: 0.4 })),
  );
  can.position.copy(from);
  group.add(can);
  const beam = makeBeam(from, new THREE.Vector3(item.x, 0, item.z), 0.95, plan.mood.light, 0.05 * plan.mood.spot);
  track(beam.geometry); track(beam.material);
  group.add(beam);
  room.fixtures.push({
    position: from.clone().add(group.position),
    target: target.clone().add(group.position),
    angle: 0.32,
  });
}

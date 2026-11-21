// Light installation: a repository's commit history as a rising spiral of
// lights you walk through, with its file tree hanging above as a chandelier.

import * as THREE from 'three';
import { buildForm, commitField } from '../shared/repoform.js';
import { loadRepoData } from './sculpture.js';
import { plaqueTexture } from './textures.js';
import { WALL_THICKNESS as T } from './plan.js';

const CYCLE_SECONDS = 16;

const vertexShader = /* glsl */`
  attribute vec3 aColor;
  attribute float aTime;
  attribute float aSize;
  uniform float uClock;
  uniform float uCursor;
  uniform float uScale;
  varying vec3 vColor;
  varying float vAlpha;
  void main() {
    vec3 p = position;
    float phase = aTime * 40.0 + p.x * 0.7 + p.z * 0.5;
    p.y += sin(uClock * 0.7 + phase) * 0.07;
    float d = aTime - uCursor;
    float pulse = exp(-d * d * 900.0);
    float past = step(aTime, uCursor);
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = aSize * uScale * (1.0 + 2.2 * pulse) / max(0.5, -mv.z);
    vColor = aColor * (0.6 + 0.45 * past + 3.2 * pulse);
    vAlpha = 0.55 + 0.45 * pulse;
  }
`;

const fragmentShader = /* glsl */`
  varying vec3 vColor;
  varying float vAlpha;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    float a = smoothstep(0.5, 0.0, d) * vAlpha;
    if (a < 0.01) discard;
    gl_FragColor = vec4(vColor * a, a);
  }
`;

function pointsMaterial(uniforms) {
  return new THREE.ShaderMaterial({
    uniforms, vertexShader, fragmentShader,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
}

function fieldPoints(field, uniforms) {
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(field.positions, 3));
  geometry.setAttribute('aColor', new THREE.Float32BufferAttribute(field.colours, 3));
  geometry.setAttribute('aTime', new THREE.Float32BufferAttribute(field.times, 1));
  geometry.setAttribute('aSize', new THREE.Float32BufferAttribute(field.sizes, 1));
  return new THREE.Points(geometry, pointsMaterial(uniforms));
}

function chandelier(data, plan, uniforms) {
  const form = buildForm(data, { height: Math.min(2.2, plan.height - 3.6), radius: 2.4 });
  const positions = [], colours = [], times = [], sizes = [];
  for (const star of form.stars) {
    const [x, y, z] = star.position;
    positions.push(x, plan.height - 0.25 - y, z);
    colours.push(...star.colour);
    times.push(star.born);
    sizes.push(Math.max(0.6, star.radius * 60));
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('aColor', new THREE.Float32BufferAttribute(colours, 3));
  geometry.setAttribute('aTime', new THREE.Float32BufferAttribute(times, 1));
  geometry.setAttribute('aSize', new THREE.Float32BufferAttribute(sizes, 1));
  const points = new THREE.Points(geometry, pointsMaterial(uniforms));

  const lines = [];
  for (const branch of form.branches) {
    lines.push(branch.from[0], plan.height - 0.25 - branch.from[1], branch.from[2]);
    lines.push(branch.to[0], plan.height - 0.25 - branch.to[1], branch.to[2]);
  }
  const lineGeometry = new THREE.BufferGeometry();
  lineGeometry.setAttribute('position', new THREE.Float32BufferAttribute(lines, 3));
  const lineMaterial = new THREE.LineBasicMaterial({
    color: 0x8a7550, transparent: true, opacity: 0.35, blending: THREE.AdditiveBlending, depthWrite: false,
  });
  return [points, new THREE.LineSegments(lineGeometry, lineMaterial)];
}

export function addInstallation(room, entry, track) {
  const { plan, group } = room;
  room.installation = [];
  if (!entry) return;
  const info = { ...entry, style: 'installation', stats: '' };
  addPlaque(room, info, ['Light installation', 'Loading...'], track);

  loadRepoData(entry.data).then((data) => {
    if (room.disposed) return;
    const uniforms = {
      uClock: { value: 0 }, uCursor: { value: 1.2 },
      uScale: { value: 42 * Math.min(window.devicePixelRatio, 1.75) },
    };
    const radius = Math.min(plan.width, plan.depth) / 2 - 2.6;
    const field = commitField(data, { radius, top: Math.min(3.6, plan.height - 1.6) });
    const parts = [fieldPoints(field, uniforms), ...chandelier(data, plan, uniforms)];
    for (const part of parts) {
      part.frustumCulled = false;
      group.add(part);
      room.installation.push(part);
    }
    const years = [data.first_commit, data.last_commit].map((t) => new Date(t * 1000).getUTCFullYear());
    info.stats = `${data.commits.toLocaleString('en-GB')} commits, ${years[0]} to ${years[1]}`;
    room.plaque?.replace(['Light installation', info.stats, 'Each light is a change; the pulse is time']);

    let clock = 0;
    room.updaters.push((dt) => {
      clock += dt;
      uniforms.uClock.value = clock;
      uniforms.uCursor.value = ((clock % CYCLE_SECONDS) / (CYCLE_SECONDS - 3)) * 1.05 - 0.02;
    });
    room.rest = () => { uniforms.uCursor.value = 1.2; };
  }).catch(() => {});

  room.releases.push(() => {
    for (const part of room.installation) {
      part.geometry.dispose();
      part.material.dispose();
    }
  });
}

function addPlaque(room, info, lines, track) {
  const { plan, group } = room;
  const material = track(new THREE.MeshBasicMaterial({ color: 0xb8b8b8 }));
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), material);
  mesh.userData.artwork = info;
  const x = -plan.width / 4;
  mesh.position.set(x, 1.45, -plan.depth / 2 + T / 2 + 0.01);
  group.add(mesh);
  room.artMeshes.push(mesh);
  let texture = null;
  room.plaque = {
    replace(newLines) {
      if (texture) texture.dispose();
      texture = plaqueTexture(info.title, ...newLines);
      material.map = texture;
      material.needsUpdate = true;
      mesh.scale.set(0.9, 0.9 / texture.userData.aspect, 1);
    },
  };
  room.plaque.replace(lines);
  room.releases.push(() => { texture?.dispose(); mesh.geometry.dispose(); });
}

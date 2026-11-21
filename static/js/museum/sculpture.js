// A repository as a sculpture: glowing file beads on bronze directory branches.
// History replays on the GPU: each element carries its birth time and a single
// uProgress uniform decides what exists.

import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';
import { buildForm } from '../shared/repoform.js';

const BEAD = new THREE.IcosahedronGeometry(1, 2);
const POP = 0.025;
const BEAD_SCALE = 1.5;
const GROW = 0.06;
const dataCache = new Map();

export function loadRepoData(url) {
  if (!dataCache.has(url)) {
    dataCache.set(url, fetch(url).then((r) => {
      if (!r.ok) throw new Error(`repo data ${r.status}`);
      return r.json();
    }));
  }
  return dataCache.get(url);
}

function revealOnProgress(material, uniforms, attribute, extraFragment = '') {
  material.onBeforeCompile = (shader) => {
    shader.uniforms.uProgress = uniforms.uProgress;
    shader.uniforms.uGlow = uniforms.uGlow;
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', `#include <common>\nattribute float ${attribute};\nuniform float uProgress;\nvarying float vAge;`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>\nvAge = uProgress - ${attribute};\ntransformed *= clamp(vAge / ${POP.toFixed(3)}, 0.0, 1.0);`);
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform float uGlow;\nvarying float vAge;')
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>\n${extraFragment}`);
  };
  material.customProgramCacheKey = () => `reveal:${attribute}:${extraFragment}`;
}

function buildBeads(form, uniforms) {
  const count = form.stars.length;
  const geometry = BEAD.clone();
  const born = new Float32Array(count);
  const material = new THREE.MeshPhysicalMaterial({
    roughness: 0.18, metalness: 0.0, clearcoat: 1.0, clearcoatRoughness: 0.1, emissive: 0x000000,
  });
  revealOnProgress(material, uniforms, 'aBorn',
    'float flash = 1.0 - clamp(vAge / 0.08, 0.0, 1.0);\ntotalEmissiveRadiance += diffuseColor.rgb * (uGlow + flash * 2.5);');
  const mesh = new THREE.InstancedMesh(geometry, material, count);
  const matrix = new THREE.Matrix4();
  const colour = new THREE.Color();
  form.stars.forEach((star, i) => {
    const [x, y, z] = star.position;
    const r = star.radius * BEAD_SCALE;
    matrix.makeScale(r, r, r).setPosition(x, y, z);
    mesh.setMatrixAt(i, matrix);
    colour.setRGB(...star.colour, THREE.SRGBColorSpace);
    mesh.setColorAt(i, colour);
    born[i] = star.born;
  });
  geometry.setAttribute('aBorn', new THREE.InstancedBufferAttribute(born, 1));
  mesh.computeBoundingSphere();
  return mesh;
}

function buildBranches(form, uniforms) {
  const tubes = form.branches.map((branch) => {
    const from = new THREE.Vector3(...branch.from);
    const to = new THREE.Vector3(...branch.to);
    const mid = from.clone().lerp(to, 0.5);
    const side = new THREE.Vector3().subVectors(to, from).cross(new THREE.Vector3(0, 1, 0));
    if (side.lengthSq() < 1e-8) side.set(1, 0, 0);
    mid.addScaledVector(side.normalize(), branch.bend * from.distanceTo(to) * 0.45);
    const curve = new THREE.QuadraticBezierCurve3(from, mid, to);
    const radius = Math.max(0.0025, branch.weight * 0.09);
    const tube = new THREE.TubeGeometry(curve, 10, radius, 6, false);
    const born = new Float32Array(tube.attributes.position.count).fill(branch.born);
    tube.setAttribute('aBorn', new THREE.BufferAttribute(born, 1));
    return tube;
  });
  if (tubes.length === 0) return null;
  const geometry = mergeGeometries(tubes, false);
  tubes.forEach((t) => t.dispose());
  const material = new THREE.MeshStandardMaterial({ color: 0x9a7a45, metalness: 1.0, roughness: 0.32 });
  revealOnProgress(material, uniforms, 'aBorn');
  return new THREE.Mesh(geometry, material);
}

function buildFilaments(form, uniforms) {
  const positions = [], colours = [], born = [];
  for (const star of form.stars) {
    const slash = star.path.lastIndexOf('/');
    const dir = form.dirs.get(slash < 0 ? '' : star.path.slice(0, slash));
    positions.push(...dir, ...star.position);
    colours.push(...star.colour, ...star.colour);
    born.push(star.born, star.born);
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colours, 3));
  geometry.setAttribute('aBorn', new THREE.Float32BufferAttribute(born, 1));
  const material = new THREE.ShaderMaterial({
    uniforms: { uProgress: uniforms.uProgress },
    vertexShader: /* glsl */`
      attribute float aBorn; uniform float uProgress; varying vec3 vColor; varying float vShow;
      void main() { vColor = color; vShow = clamp((uProgress - aBorn) / ${GROW.toFixed(3)}, 0.0, 1.0);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: /* glsl */`
      varying vec3 vColor; varying float vShow;
      void main() { if (vShow <= 0.0) discard; gl_FragColor = vec4(vColor * 0.55 * vShow, 0.5 * vShow); }`,
    vertexColors: true, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  });
  return new THREE.LineSegments(geometry, material);
}

// Returns a Group standing on y = 0 with update(dt, near) and dispose().
export function buildSculpture(data, { height = 1.7, radius = 0.72 } = {}) {
  const form = buildForm(data, { height, radius });
  const uniforms = { uProgress: { value: 1.0 }, uGlow: { value: 0.75 } };
  const group = new THREE.Group();
  const parts = [buildBeads(form, uniforms), buildBranches(form, uniforms), buildFilaments(form, uniforms)].filter(Boolean);
  for (const part of parts) group.add(part);

  let clock = 0;
  const cycle = 14;
  group.userData.update = (dt, active) => {
    group.rotation.y += dt * 0.12;
    if (!active) {
      uniforms.uProgress.value = 1.0;
      clock = 0;
      return;
    }
    clock = (clock + dt) % cycle;
    const growing = Math.min(1, clock / (cycle - 4));
    uniforms.uProgress.value = -0.02 + growing * 1.04;
  };
  group.userData.dispose = () => {
    for (const part of parts) {
      part.geometry.dispose();
      part.material.dispose();
    }
  };
  return group;
}

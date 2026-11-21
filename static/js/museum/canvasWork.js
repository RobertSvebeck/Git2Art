// Artworks as physical objects: a stretched canvas (painting wrapped around
// its edges) or a wooden panel, with linen weave, brushstroke relief,
// varnish, an optional frame moulding and a soft shadow on the wall.

import * as THREE from 'three';
import { hashUnit } from '../shared/repoform.js';
import { softShadow, weaveNormal } from './textures.js';

const CANVAS_DEPTH = 0.038;
const PANEL_DEPTH = 0.022;
const WALL_GAP = 0.006;
const EDGE_STRIP = 0.012;
const WEAVE_TILE = 0.03;

// Side faces sample a thin strip from the matching edge of the image, so the
// painting appears to continue around the stretcher (a gallery wrap).
function wrappedBox(width, height, depth) {
  const geometry = new THREE.BoxGeometry(width, height, depth);
  const uv = geometry.attributes.uv;
  const strip = (face, fn) => {
    for (let i = face * 4; i < face * 4 + 4; i++) {
      const [u, v] = fn(uv.getX(i), uv.getY(i));
      uv.setXY(i, u, v);
    }
  };
  strip(0, (u, v) => [1 - EDGE_STRIP * u, v]);
  strip(1, (u, v) => [EDGE_STRIP * u, v]);
  strip(2, (u, v) => [u, 1 - EDGE_STRIP * v]);
  strip(3, (u, v) => [u, EDGE_STRIP * v]);
  strip(5, () => [0.5, 0.5]);
  return geometry;
}

export function paintMaterial(width, height, placeholder, track) {
  const weave = track(weaveNormal().clone());
  weave.repeat.set(width / WEAVE_TILE, height / WEAVE_TILE);
  weave.needsUpdate = true;
  return track(new THREE.MeshPhysicalMaterial({
    color: placeholder,
    roughness: 0.58,
    clearcoat: 0.3,
    clearcoatRoughness: 0.32,
    normalMap: weave,
    normalScale: new THREE.Vector2(0.35, 0.35),
    emissive: 0x000000,
  }));
}

// Called once the image has loaded: show it, glow faintly in unlit rooms,
// and raise brushstrokes using the image itself as a bump map.
export function applyArt(material, texture) {
  material.map = texture;
  material.bumpMap = texture;
  material.bumpScale = 1.6;
  material.emissiveMap = texture;
  material.emissive.set(0xffffff);
  material.emissiveIntensity = 0.04;
  material.color.set(0xffffff);
  material.needsUpdate = true;
}

export function frameRing(piece, outerW, outerH, border, depth, material, track) {
  const parts = [
    [outerW, border, 0, (outerH - border) / 2],
    [outerW, border, 0, -(outerH - border) / 2],
    [border, outerH - 2 * border, -(outerW - border) / 2, 0],
    [border, outerH - 2 * border, (outerW - border) / 2, 0],
  ];
  for (const [w, h, x, y] of parts) {
    const mesh = new THREE.Mesh(track(new THREE.BoxGeometry(w, h, depth)), material);
    mesh.position.set(x, y, WALL_GAP + depth / 2);
    piece.add(mesh);
  }
}

// Builds the painted object inside `piece`; returns the mesh to raycast.
export function buildCanvas(piece, artwork, width, height, frameDepth, materials, track) {
  const panel = hashUnit(String(artwork.id), 'panel') < 0.25;
  const depth = panel ? PANEL_DEPTH : CANVAS_DEPTH;
  const geometry = track(wrappedBox(width, height, depth));
  const paint = materials.paint;
  const sides = panel ? materials.wood : paint;
  const mesh = new THREE.Mesh(geometry, [sides, sides, sides, sides, paint, materials.back]);
  const recess = frameDepth > 0 ? Math.max(0, frameDepth - depth - 0.008) : 0.03;
  mesh.position.z = WALL_GAP + recess + depth / 2;
  piece.add(mesh);
  return mesh;
}

export function wallShadow(piece, width, height, track) {
  const material = track(new THREE.MeshBasicMaterial({
    color: 0x000000, alphaMap: softShadow(), transparent: true, opacity: 0.68, depthWrite: false,
  }));
  const shadow = new THREE.Mesh(track(new THREE.PlaneGeometry(width * 1.16 + 0.1, height * 1.16 + 0.12)), material);
  shadow.position.set(0.02, -0.05, 0.002);
  shadow.renderOrder = 0;
  piece.add(shadow);
}

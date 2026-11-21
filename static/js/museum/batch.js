// Merge a room's static meshes that share a material into one draw call each.

import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

function mergeable(mesh) {
  const m = mesh.material;
  return mesh.isMesh && !mesh.isInstancedMesh && !Array.isArray(m) && !m.transparent
    && !m.isShaderMaterial && !mesh.userData.artwork && mesh.geometry.index;
}

// Returns the merged geometries so the caller can dispose them with the room.
export function mergeStatic(group) {
  group.updateMatrixWorld(true);
  const toLocal = new THREE.Matrix4().copy(group.matrixWorld).invert();
  const buckets = new Map();
  group.traverse((object) => {
    if (object.userData.dynamic) return;
    let parent = object.parent;
    while (parent && parent !== group) {
      if (parent.userData.dynamic) return;
      parent = parent.parent;
    }
    if (object !== group && mergeable(object)) {
      if (!buckets.has(object.material)) buckets.set(object.material, []);
      buckets.get(object.material).push(object);
    }
  });

  const merged = [];
  for (const [material, meshes] of buckets) {
    if (meshes.length < 2) continue;
    const geometries = meshes.map((mesh) => {
      const g = mesh.geometry.clone();
      g.applyMatrix4(new THREE.Matrix4().multiplyMatrices(toLocal, mesh.matrixWorld));
      for (const name of Object.keys(g.attributes)) {
        if (!['position', 'normal', 'uv'].includes(name)) g.deleteAttribute(name);
      }
      return g;
    });
    const geometry = mergeGeometries(geometries, false);
    geometries.forEach((g) => g.dispose());
    if (!geometry) continue;
    for (const mesh of meshes) mesh.removeFromParent();
    const batch = new THREE.Mesh(geometry, material);
    batch.matrixAutoUpdate = false;
    group.add(batch);
    merged.push(geometry);
  }
  return merged;
}

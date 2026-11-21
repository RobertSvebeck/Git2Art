// Cheap fake lighting that works in every loaded room: volumetric beams,
// wall halos and dust. Real lights are reserved for the room you stand in.

import * as THREE from 'three';
import { radialTexture } from './textures.js';

const DOWN = new THREE.Vector3(0, -1, 0);

const beamVertex = /* glsl */`
  uniform float uLength;
  varying float vAlong;
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    vAlong = clamp(-position.y / uLength, 0.0, 1.0);
    vNormal = normalize(normalMatrix * normal);
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    vView = normalize(-mv.xyz);
    gl_Position = projectionMatrix * mv;
  }
`;

const beamFragment = /* glsl */`
  uniform vec3 uColor;
  uniform float uIntensity;
  varying float vAlong;
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    float edge = pow(abs(dot(normalize(vNormal), normalize(vView))), 2.2);
    float fade = pow(1.0 - vAlong, 1.4) * smoothstep(0.0, 0.08, vAlong);
    float a = edge * fade * uIntensity;
    gl_FragColor = vec4(uColor * a, a);
  }
`;

export function makeBeam(from, to, spread, color, intensity) {
  const direction = new THREE.Vector3().subVectors(to, from);
  const length = direction.length() * 1.1;
  const geometry = new THREE.ConeGeometry(spread, length, 32, 1, true);
  geometry.translate(0, -length / 2, 0);
  geometry.rotateY(Math.PI);
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uColor: { value: new THREE.Color(color) },
      uIntensity: { value: intensity },
      uLength: { value: length },
    },
    vertexShader: beamVertex,
    fragmentShader: beamFragment,
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
    side: THREE.DoubleSide,
  });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.copy(from);
  mesh.quaternion.setFromUnitVectors(DOWN, direction.normalize());
  mesh.renderOrder = 2;
  return mesh;
}

export function makeHalo(width, height, color, intensity) {
  const material = new THREE.MeshBasicMaterial({
    map: radialTexture(),
    color: new THREE.Color(color).multiplyScalar(intensity),
    transparent: true,
    depthWrite: false,
    blending: THREE.AdditiveBlending,
  });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(width, height), material);
  mesh.renderOrder = 1;
  return mesh;
}

export function makeDust(width, height, depth, count, color) {
  const positions = new Float32Array(count * 3);
  const speeds = new Float32Array(count);
  for (let i = 0; i < count; i++) {
    positions[i * 3] = (Math.random() - 0.5) * width;
    positions[i * 3 + 1] = Math.random() * height;
    positions[i * 3 + 2] = (Math.random() - 0.5) * depth;
    speeds[i] = 0.02 + Math.random() * 0.06;
  }
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const material = new THREE.PointsMaterial({
    color, size: 0.025, transparent: true, opacity: 0.55,
    depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
  });
  const points = new THREE.Points(geometry, material);
  points.userData.update = (dt, time) => {
    const p = geometry.attributes.position.array;
    for (let i = 0; i < count; i++) {
      p[i * 3 + 1] += speeds[i] * dt * (Math.sin(time * 0.3 + i) > 0 ? 1 : -0.6);
      p[i * 3] += Math.sin(time * 0.2 + i * 1.7) * 0.004;
      if (p[i * 3 + 1] > height) p[i * 3 + 1] = 0;
      if (p[i * 3 + 1] < 0) p[i * 3 + 1] = height;
    }
    geometry.attributes.position.needsUpdate = true;
  };
  return points;
}

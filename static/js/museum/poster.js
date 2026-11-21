// Invitation lightboxes: "Your repository could hang here". Clicking one opens
// the submit form; when the artwork is ready it replaces the sign on the wall.

import * as THREE from 'three';
import { wallShadow } from './canvasWork.js';

let posterTexture = null;

function makeTexture() {
  if (posterTexture) return posterTexture;
  const c = document.createElement('canvas');
  c.width = 1024; c.height = 680;
  const ctx = c.getContext('2d');
  const g = ctx.createLinearGradient(0, 0, 0, c.height);
  g.addColorStop(0, '#171b30');
  g.addColorStop(1, '#0c0e1a');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, c.width, c.height);
  ctx.strokeStyle = '#ffd23f';
  ctx.setLineDash([22, 14]);
  ctx.lineWidth = 6;
  ctx.strokeRect(70, 70, c.width - 140, c.height - 140);
  ctx.setLineDash([]);
  ctx.textAlign = 'center';
  ctx.fillStyle = 'rgba(255,255,255,0.65)';
  ctx.font = '600 30px "Helvetica Neue", Arial, sans-serif';
  ctx.fillText('G I T 2 A R T   M U S E U M', c.width / 2, 170);
  ctx.fillStyle = '#ffffff';
  ctx.font = '300 74px "Helvetica Neue", Arial, sans-serif';
  ctx.fillText('Your repository', c.width / 2, 285);
  ctx.fillText('could hang here', c.width / 2, 370);
  ctx.fillStyle = 'rgba(255,255,255,0.75)';
  ctx.font = '400 32px "Helvetica Neue", Arial, sans-serif';
  ctx.fillText('Turn any public GitHub repository into art', c.width / 2, 450);
  ctx.fillStyle = '#ffd23f';
  const pill = { w: 470, h: 70 };
  const px = (c.width - pill.w) / 2, py = 500;
  ctx.beginPath();
  ctx.roundRect(px, py, pill.w, pill.h, 35);
  ctx.fill();
  ctx.fillStyle = '#14182b';
  ctx.font = '700 30px "Helvetica Neue", Arial, sans-serif';
  ctx.fillText('CLICK OR PRESS ENTER', c.width / 2, py + 46);
  posterTexture = new THREE.CanvasTexture(c);
  posterTexture.colorSpace = THREE.SRGBColorSpace;
  return posterTexture;
}

export const INVITATION = { kind: 'submit', title: 'Your repository could hang here', style: 'invitation' };

export function addPoster(room, slot, transform, track) {
  const height = Math.min(1.5, slot.maxHeight * 0.85);
  const width = Math.min(slot.maxWidth, height * 1024 / 680);
  const piece = new THREE.Group();
  piece.position.set(transform.x, slot.centreY, transform.z);
  piece.rotation.y = transform.rotationY;
  room.group.add(piece);

  const box = new THREE.Mesh(
    track(new THREE.BoxGeometry(width + 0.08, height + 0.08, 0.07)),
    track(new THREE.MeshStandardMaterial({ color: 0x111114, metalness: 0.4, roughness: 0.4 })),
  );
  box.position.z = 0.04;
  piece.add(box);
  const face = new THREE.Mesh(
    track(new THREE.PlaneGeometry(width, height)),
    track(new THREE.MeshBasicMaterial({ map: makeTexture(), color: new THREE.Color(1.15, 1.15, 1.15) })),
  );
  face.position.z = 0.0755;
  face.userData.artwork = INVITATION;
  face.userData.poster = { piece, slot };
  piece.add(face);
  wallShadow(piece, width + 0.08, height + 0.08, track);
  room.artMeshes.push(face);
  return face;
}

export function removePoster(room, face) {
  room.group.remove(face.userData.poster.piece);
  room.artMeshes = room.artMeshes.filter((m) => m !== face);
}

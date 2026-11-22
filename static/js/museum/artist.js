// An artist's room: their GitHub portrait in a gilded roundel above the north
// and south doors, with their name and star count beneath.

import * as THREE from 'three';
import { DOOR_HEIGHT, WALL_THICKNESS as T } from './plan.js';
import { signTexture } from './textures.js';

const PORTRAIT_RADIUS = 0.95;
const loader = new THREE.TextureLoader();
loader.setCrossOrigin('anonymous');

function starsText(stars) {
  if (!stars) return '';
  return stars >= 1000 ? `${(stars / 1000).toFixed(1).replace('.0', '')}k stars` : `${stars} ${stars === 1 ? 'star' : 'stars'}`;
}

export function addArtistWalls(plan, group, track) {
  const { artist } = plan;
  const lightWall = new THREE.Color(plan.mood.wall).getHSL({}).l > 0.5;
  const repos = `${artist.repos} ${artist.repos === 1 ? 'repository' : 'repositories'}`;
  const nameTexture = track(signTexture(artist.owner, lightWall));
  const metaTexture = track(signTexture([repos, starsText(artist.stars)].filter(Boolean).join('  /  '), lightWall));
  const portrait = track(new THREE.MeshBasicMaterial({ color: 0x4a4a4a }));
  if (artist.avatar) {
    loader.load(artist.avatar, (texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      track(texture);
      portrait.map = texture;
      portrait.color.set(0xffffff);
      portrait.needsUpdate = true;
    });
  }
  const gold = track(new THREE.MeshStandardMaterial({ color: 0xc29a45, metalness: 0.85, roughness: 0.32 }));
  const discGeometry = track(new THREE.CircleGeometry(PORTRAIT_RADIUS, 48));
  const ringGeometry = track(new THREE.TorusGeometry(PORTRAIT_RADIUS + 0.05, 0.07, 12, 64));
  const nameGeometry = track(new THREE.PlaneGeometry(5.2, 0.65));
  const metaGeometry = track(new THREE.PlaneGeometry(3.4, 0.425));
  const nameMaterial = track(new THREE.MeshBasicMaterial({ map: nameTexture, transparent: true }));
  const metaMaterial = track(new THREE.MeshBasicMaterial({ map: metaTexture, transparent: true, opacity: 0.95 }));

  for (const side of [-1, 1]) {
    const wall = new THREE.Group();
    wall.position.z = side * (plan.depth / 2 - T / 2 - 0.03);
    wall.rotation.y = side < 0 ? 0 : Math.PI;
    group.add(wall);
    const add = (geometry, material, y) => {
      const mesh = new THREE.Mesh(geometry, material);
      mesh.position.y = y;
      wall.add(mesh);
      return mesh;
    };
    add(nameGeometry, nameMaterial, DOOR_HEIGHT + 0.85);
    add(metaGeometry, metaMaterial, DOOR_HEIGHT + 0.36);
    const y = DOOR_HEIGHT + 1.3 + PORTRAIT_RADIUS;
    add(discGeometry, portrait, y).position.z = 0.02;
    add(ringGeometry, gold, y).position.z = 0.03;
  }
}

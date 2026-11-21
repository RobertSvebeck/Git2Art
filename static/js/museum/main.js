// Git2Art Museum: an endless, procedurally generated walkable gallery.

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { isWalkable } from './plan.js';
import { setMaxAnisotropy } from './textures.js';
import { World } from './world.js';
import { Lighting } from './lighting.js';
import { Walker } from './controls.js';
import { Ui } from './ui.js';

const INTERACT_DISTANCE = 7;
const touchDevice = window.matchMedia('(pointer: coarse)').matches;

function worldSeedFromUrl() {
  const fromUrl = Number.parseInt(new URLSearchParams(window.location.search).get('seed'), 10);
  return Number.isFinite(fromUrl) ? fromUrl >>> 0 : Math.floor(Math.random() * 2 ** 31);
}

function createRenderer(container) {
  const renderer = new THREE.WebGLRenderer({ antialias: !touchDevice, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, touchDevice ? 1.25 : 1.75));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);
  setMaxAnisotropy(renderer.capabilities.getMaxAnisotropy());
  return renderer;
}

function createComposer(renderer, scene, camera) {
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const scale = touchDevice ? 0.5 : 1;
  const bloom = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth * scale, window.innerHeight * scale), 0.4, 0.55, 0.92,
  );
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  return composer;
}

async function loadCatalogue() {
  const response = await fetch('/api/museum/artworks');
  if (!response.ok) throw new Error(`Catalogue request failed (${response.status})`);
  const data = await response.json();
  if (!data.artworks || data.artworks.length === 0) throw new Error('No artworks to hang yet');
  return data.artworks;
}

async function start() {
  const container = document.getElementById('museum');
  const ui = new Ui();
  const worldSeed = worldSeedFromUrl();

  const renderer = createRenderer(container);
  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x000000, 22, 64);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.35;
  const camera = new THREE.PerspectiveCamera(touchDevice ? 72 : 65, window.innerWidth / window.innerHeight, 0.05, 120);
  const composer = createComposer(renderer, scene, camera);

  let artworks;
  try {
    artworks = await loadCatalogue();
  } catch (error) {
    ui.showError(error.message);
    return;
  }

  const world = new World(scene, artworks, worldSeed);
  const lighting = new Lighting(scene, renderer, touchDevice ? 4 : 10);
  const walker = new Walker(camera, renderer.domElement, (x, z) => isWalkable(worldSeed, x, z));
  walker.position.set(0, 1.65, 4);

  const raycaster = new THREE.Raycaster();
  raycaster.far = INTERACT_DISTANCE;
  const pickAt = (ndcX, ndcY) => {
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);
    const hit = raycaster.intersectObjects(world.artMeshes(), false)[0];
    return hit ? hit.object.userData.artwork : null;
  };

  let hovered = null;
  ui.onEnter = () => {
    walker.enabled = true;
    if (!touchDevice) walker.lock();
  };
  ui.onClosePanel = () => {
    if (!touchDevice) walker.lock();
  };
  renderer.domElement.addEventListener('click', () => {
    if (touchDevice || ui.panelOpen) return;
    if (!walker.locked) {
      if (walker.enabled) walker.lock();
      return;
    }
    if (hovered) {
      document.exitPointerLock();
      ui.showArtwork(hovered);
    }
  });
  walker.onTap = (x, y) => {
    const artwork = pickAt((x / window.innerWidth) * 2 - 1, -(y / window.innerHeight) * 2 + 1);
    if (artwork) ui.showArtwork(artwork);
  };
  document.addEventListener('pointerlockchange', () => {
    if (!walker.locked && !ui.panelOpen && walker.enabled && !touchDevice) ui.showPaused();
    if (walker.locked) ui.hideOverlays();
  });

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer.setSize(window.innerWidth, window.innerHeight);
  });

  const entered = world.update(walker.position);
  if (entered) lighting.focus(entered);
  ui.ready(artworks.length, worldSeed, touchDevice);

  if (new URLSearchParams(window.location.search).has('debug')) {
    window.museumDebug = { walker, world, renderer, lighting, ui };
  }

  const timer = new THREE.Timer();
  timer.connect(document);
  let frame = 0;
  renderer.setAnimationLoop(() => {
    timer.update();
    const dt = Math.min(timer.getDelta(), 0.05);
    const time = timer.getElapsed();
    walker.update(dt);
    const room = world.update(walker.position);
    if (room) {
      lighting.focus(room);
      ui.enterRoom(room.plan, world.visited.size);
    }
    lighting.update(dt);
    world.tick(dt, time);
    if (!touchDevice && walker.locked && frame++ % 4 === 0) {
      hovered = pickAt(0, 0);
      ui.setHover(hovered);
    }
    composer.render();
  });
}

start();

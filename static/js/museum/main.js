// Git2Art Museum: an endless, procedurally generated walkable gallery.

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { SMAAPass } from 'three/addons/postprocessing/SMAAPass.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { isWalkable } from './plan.js';
import { setRenderer, warmSurfaces } from './textures.js';
import { World } from './world.js';
import { Lighting } from './lighting.js';
import { Walker } from './controls.js';
import { Ui } from './ui.js';
import { SubmitPanel } from './submit.js';

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
  setRenderer(renderer);
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
  // SMAA, not a multisampled target: a 4x MSAA half-float target rendered
  // all black on ANGLE/Metal (Chrome on Apple silicon) in testing.
  if (!touchDevice) composer.addPass(new SMAAPass());
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
  scene.environmentIntensity = 0.14;
  const camera = new THREE.PerspectiveCamera(touchDevice ? 72 : 65, window.innerWidth / window.innerHeight, 0.05, 120);
  const composer = createComposer(renderer, scene, camera);

  warmSurfaces();
  let artworks;
  try {
    artworks = await loadCatalogue();
  } catch (error) {
    ui.showError(error.message);
    return;
  }

  const world = new World(scene, artworks, worldSeed, renderer, camera);
  const lighting = new Lighting(scene, renderer, touchDevice ? 4 : 10);
  const walker = new Walker(camera, renderer.domElement, (x, z) => isWalkable(worldSeed, x, z));
  walker.position.set(0, 1.65, 4);

  const raycaster = new THREE.Raycaster();
  raycaster.far = INTERACT_DISTANCE;
  const pickAt = (ndcX, ndcY) => {
    raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);
    const hit = raycaster.intersectObjects(world.artMeshes(), false)[0];
    return hit ? hit.object : null;
  };
  const submit = new SubmitPanel({
    onOpen: () => { if (walker.locked) document.exitPointerLock(); ui.setHover(null); },
    onClose: () => { if (!touchDevice) walker.lock(); },
    onHang: (face, artwork) => {
      const room = world.roomContaining(face);
      if (room) {
        room.hangArtwork(face, artwork);
        if (world.current && room.plan.key === world.current.key) lighting.focus(room);
      }
      world.deck.cards.push(artwork);
    },
  });
  const inspect = (mesh) => {
    if (!mesh) return;
    if (mesh.userData.poster) submit.open(mesh);
    else ui.showArtwork(mesh.userData.artwork);
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
    if (touchDevice || ui.panelOpen || submit.isOpen) return;
    if (!walker.locked) {
      if (walker.enabled) walker.lock();
      return;
    }
    if (hovered) {
      document.exitPointerLock();
      inspect(hovered);
    }
  });
  document.addEventListener('keydown', (e) => {
    if (e.code !== 'Enter' || !walker.enabled || ui.panelOpen || submit.isOpen || !hovered) return;
    if (walker.locked) document.exitPointerLock();
    inspect(hovered);
  });
  walker.onTap = (x, y) => {
    inspect(pickAt((x / window.innerWidth) * 2 - 1, -(y / window.innerHeight) * 2 + 1));
  };
  document.addEventListener('pointerlockchange', () => {
    if (!walker.locked && !ui.panelOpen && !submit.isOpen && walker.enabled && !touchDevice) ui.showPaused();
    if (walker.locked) ui.hideOverlays();
  });

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    composer.setSize(window.innerWidth, window.innerHeight);
  });

  const teleport = (owner) => {
    const target = world.prepareArtistRoom(owner);
    walker.position.set(target.x, 1.65, target.z);
    walker.velocity.set(0, 0);
    walker.yaw = target.yaw;
    walker.pitch = 0.18;
    const flash = document.getElementById('teleport-flash');
    flash.classList.remove('active');
    void flash.offsetWidth;
    flash.classList.add('active');
    const params = new URLSearchParams(window.location.search);
    params.set('artist', owner);
    params.set('seed', worldSeed);
    history.replaceState(null, '', `${window.location.pathname}?${params}`);
  };
  ui.onTeleport = teleport;
  ui.canTeleport = (owner) => world.hasArtist(owner) && world.currentArtist() !== owner.toLowerCase();
  const startArtist = new URLSearchParams(window.location.search).get('artist');
  if (startArtist && world.hasArtist(startArtist)) teleport(startArtist);

  const entered = world.update(walker.position);
  if (entered) lighting.focus(entered);
  ui.ready(artworks.length, worldSeed, touchDevice);

  if (new URLSearchParams(window.location.search).has('debug')) {
    window.museumDebug = { walker, world, renderer, lighting, ui, submit };
  }

  let perfFrames = 0, perfTime = 0, perfChecked = false;
  const timer = new THREE.Timer();
  timer.connect(document);
  let frame = 0;
  renderer.setAnimationLoop(() => {
    timer.update();
    const dt = Math.min(timer.getDelta(), 0.05);
    const time = timer.getElapsed();
    if (!perfChecked && walker.enabled) {
      perfFrames += 1;
      perfTime += timer.getDelta();
      if (perfTime > 4) {
        perfChecked = true;
        if (perfFrames / perfTime < 32) ui.suggestLite();
      }
    }
    walker.update(dt);
    const room = world.update(walker.position);
    if (room) {
      lighting.focus(room);
      ui.enterRoom(room.plan, world.visited.size);
    }
    lighting.update(dt);
    world.tick(dt, time);
    if (!touchDevice && walker.enabled && !ui.panelOpen && !submit.isOpen && frame++ % 4 === 0) {
      hovered = pickAt(0, 0);
      ui.setHover(hovered ? hovered.userData.artwork : null);
    }
    composer.render();
  });
}

start();

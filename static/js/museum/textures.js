// Procedural surface textures (canvas) and a reference-counted artwork texture cache.

import * as THREE from 'three';
import { Rng } from './rng.js';

const SIZE = 1024;
const surfaceCache = new Map();
let maxAnisotropy = 8;
let uploader = null;

export function setRenderer(renderer) {
  maxAnisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  uploader = renderer;
}

// Draw and upload every shared surface texture up front, so the first room of
// each kind never pays for canvas drawing or GPU upload mid-walk.
export function warmSurfaces() {
  const textures = [...Object.keys(FLOORS).map((type) => floorTexture(type).texture), plasterTexture(), radialTexture()];
  if (uploader) textures.forEach((t) => uploader.initTexture(t));
}

function canvas(size = SIZE) {
  const c = document.createElement('canvas');
  c.width = c.height = size;
  return [c, c.getContext('2d')];
}

function css(hex, lighten = 0) {
  const c = new THREE.Color(hex);
  c.offsetHSL(0, 0, lighten);
  return `#${c.getHexString()}`;
}

function planks(ctx, rng, base, plankWidth, variance = 0.05) {
  const rows = Math.round(SIZE / plankWidth);
  for (let r = 0; r < rows; r++) {
    let x = -rng.range(0, 400);
    while (x < SIZE) {
      const length = rng.range(260, 520);
      ctx.fillStyle = css(base, rng.range(-variance, variance));
      ctx.fillRect(x, r * plankWidth, length, plankWidth);
      ctx.globalAlpha = 0.18;
      for (let g = 0; g < 14; g++) {
        const y = r * plankWidth + rng.range(2, plankWidth - 2);
        ctx.strokeStyle = css(base, rng.range(-0.14, 0.06));
        ctx.lineWidth = rng.range(0.6, 2.2);
        ctx.beginPath();
        ctx.moveTo(x, y);
        ctx.bezierCurveTo(x + length * 0.3, y + rng.range(-4, 4), x + length * 0.7, y + rng.range(-4, 4), x + length, y);
        ctx.stroke();
      }
      ctx.globalAlpha = 0.55;
      ctx.fillStyle = css(base, -0.22);
      ctx.fillRect(x, r * plankWidth, 2, plankWidth);
      ctx.globalAlpha = 1;
      x += length;
    }
    ctx.fillStyle = css(base, -0.25);
    ctx.fillRect(0, r * plankWidth, SIZE, 2);
  }
}

function speckle(ctx, rng, colours, count, minSize, maxSize, alpha = 1) {
  ctx.globalAlpha = alpha;
  for (let i = 0; i < count; i++) {
    ctx.fillStyle = rng.pick(colours);
    const x = rng.range(0, SIZE), y = rng.range(0, SIZE), s = rng.range(minSize, maxSize);
    ctx.beginPath();
    const corners = rng.int(3, 6);
    for (let k = 0; k < corners; k++) {
      const a = (k / corners) * Math.PI * 2 + rng.range(-0.4, 0.4);
      const d = s * rng.range(0.5, 1);
      ctx.lineTo(x + Math.cos(a) * d, y + Math.sin(a) * d);
    }
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

function veins(ctx, rng, colour, count, width, alpha) {
  ctx.strokeStyle = colour;
  for (let i = 0; i < count; i++) {
    ctx.globalAlpha = alpha * rng.range(0.4, 1);
    ctx.lineWidth = rng.range(width * 0.3, width);
    let x = rng.range(-200, SIZE), y = rng.range(0, SIZE), angle = rng.range(-0.6, 0.6);
    ctx.beginPath();
    ctx.moveTo(x, y);
    for (let s = 0; s < 40; s++) {
      angle += rng.range(-0.35, 0.35);
      x += Math.cos(angle) * 30;
      y += Math.sin(angle) * 30;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
}

const FLOORS = {
  oak: { metres: 4, roughness: 0.5, draw: (ctx, rng) => planks(ctx, rng, 0xb08a5a, 64) },
  walnut: { metres: 4, roughness: 0.48, draw: (ctx, rng) => planks(ctx, rng, 0x5e3b22, 56, 0.022) },
  'black-marble': {
    metres: 6, roughness: 0.12, draw: (ctx, rng) => {
      ctx.fillStyle = '#0d0d10'; ctx.fillRect(0, 0, SIZE, SIZE);
      veins(ctx, rng, '#6a6a78', 26, 3, 0.35);
      veins(ctx, rng, '#c8c8d8', 10, 1.5, 0.25);
    },
  },
  terrazzo: {
    metres: 3, roughness: 0.28, draw: (ctx, rng) => {
      ctx.fillStyle = '#d9d4ca'; ctx.fillRect(0, 0, SIZE, SIZE);
      speckle(ctx, rng, ['#2f5d55', '#b8584a', '#e8c27a', '#555', '#9aa'], 2600, 2, 9);
      speckle(ctx, rng, ['#fff'], 900, 1, 3, 0.6);
    },
  },
  travertine: {
    metres: 4, roughness: 0.45, draw: (ctx, rng) => {
      ctx.fillStyle = '#d8c7a8'; ctx.fillRect(0, 0, SIZE, SIZE);
      for (let y = 0; y < SIZE; y += 2) {
        ctx.fillStyle = css(0xd8c7a8, rng.range(-0.05, 0.03));
        ctx.globalAlpha = 0.35; ctx.fillRect(0, y, SIZE, rng.range(1, 3));
      }
      ctx.globalAlpha = 1;
      speckle(ctx, rng, ['#a8977a'], 700, 1, 4, 0.5);
      ctx.fillStyle = '#b8a688';
      for (let k = 0; k <= SIZE; k += SIZE / 2) { ctx.fillRect(k, 0, 3, SIZE); ctx.fillRect(0, k, SIZE, 3); }
    },
  },
  concrete: {
    metres: 5, roughness: 0.55, draw: (ctx, rng) => {
      ctx.fillStyle = '#58585c'; ctx.fillRect(0, 0, SIZE, SIZE);
      speckle(ctx, rng, ['#4a4a4e', '#66666b', '#505055'], 5000, 2, 14, 0.5);
      speckle(ctx, rng, ['#3a3a3e'], 300, 1, 2, 0.8);
    },
  },
};

function cachedCanvasTexture(key, draw, repeat = true) {
  if (surfaceCache.has(key)) return surfaceCache.get(key);
  const [c, ctx] = canvas();
  draw(ctx, new Rng(key.length * 7919 + key.charCodeAt(0)));
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = maxAnisotropy;
  if (repeat) texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  surfaceCache.set(key, texture);
  return texture;
}

export function floorTexture(type) {
  const spec = FLOORS[type];
  return { texture: cachedCanvasTexture(`floor:${type}`, spec.draw), metres: spec.metres, roughness: spec.roughness };
}

export function plasterTexture() {
  return cachedCanvasTexture('plaster', (ctx, rng) => {
    ctx.fillStyle = '#f2f2f2'; ctx.fillRect(0, 0, SIZE, SIZE);
    speckle(ctx, rng, ['#e2e2e2', '#fafafa', '#e9e9e9'], 4000, 3, 22, 0.35);
  });
}

export function radialTexture() {
  return cachedCanvasTexture('radial', (ctx) => {
    const g = ctx.createRadialGradient(SIZE / 2, SIZE / 2, 0, SIZE / 2, SIZE / 2, SIZE / 2);
    g.addColorStop(0, 'rgba(255,255,255,1)');
    g.addColorStop(0.35, 'rgba(255,255,255,0.45)');
    g.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.fillStyle = g; ctx.fillRect(0, 0, SIZE, SIZE);
  }, false);
}

export function plaqueTexture(title, ...lines) {
  const height = 160 + 46 * Math.max(0, lines.length - 1);
  const [c, ctx] = canvas(512);
  c.height = height;
  ctx.fillStyle = '#f6f4ef'; ctx.fillRect(0, 0, 512, height);
  ctx.fillStyle = '#1b1b1b';
  ctx.font = '600 44px "Helvetica Neue", Arial, sans-serif';
  ctx.fillText(fitText(ctx, title, 470), 22, 66);
  ctx.fillStyle = '#6a6a6a';
  ctx.font = '400 30px "Helvetica Neue", Arial, sans-serif';
  lines.forEach((line, i) => ctx.fillText(fitText(ctx, line, 470), 22, 118 + i * 46));
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = maxAnisotropy;
  texture.userData.aspect = 512 / height;
  return texture;
}

function fitText(ctx, text, maxWidth) {
  if (ctx.measureText(text).width <= maxWidth) return text;
  let cut = text;
  while (cut.length > 1 && ctx.measureText(`${cut}...`).width > maxWidth) cut = cut.slice(0, -1);
  return `${cut}...`;
}

// Artwork images: shared between rooms, disposed when no room uses them.
const loader = new THREE.TextureLoader();
const artCache = new Map();

export function acquireArt(url) {
  let entry = artCache.get(url);
  if (!entry) {
    entry = { refs: 0, texture: null, promise: null };
    entry.promise = loader.loadAsync(url).then((texture) => {
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.anisotropy = maxAnisotropy;
      if (uploader) uploader.initTexture(texture);
      entry.texture = texture;
      if (entry.refs <= 0) disposeArt(url);
      return texture;
    });
    artCache.set(url, entry);
  }
  entry.refs += 1;
  return entry.promise;
}

export function releaseArt(url) {
  const entry = artCache.get(url);
  if (!entry) return;
  entry.refs -= 1;
  if (entry.refs <= 0 && entry.texture) disposeArt(url);
}

function disposeArt(url) {
  const entry = artCache.get(url);
  if (entry && entry.texture) entry.texture.dispose();
  artCache.delete(url);
}

// Linen weave as a tangent-space normal map: threads over and under in a
// plain weave. One tile is about 3 cm of canvas; repeat it per artwork.
export function weaveNormal() {
  if (surfaceCache.has('weave')) return surfaceCache.get('weave');
  const size = 128, threads = 32, pitch = size / threads;
  const height = new Float32Array(size * size);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const cx = (x % pitch) / pitch - 0.5, cy = (y % pitch) / pitch - 0.5;
      const over = (Math.floor(x / pitch) + Math.floor(y / pitch)) % 2;
      const warp = Math.cos(cx * Math.PI) * (over ? 1 : 0.55);
      const weft = Math.cos(cy * Math.PI) * (over ? 0.55 : 1);
      height[y * size + x] = Math.max(warp, weft) + ((x * 7 + y * 13) % 5) * 0.02;
    }
  }
  const [c, ctx] = canvas(size);
  const image = ctx.createImageData(size, size);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const h = (dx, dy) => height[((y + dy + size) % size) * size + ((x + dx + size) % size)];
      const nx = (h(-1, 0) - h(1, 0)) * 1.4, ny = (h(0, -1) - h(0, 1)) * 1.4;
      const len = Math.hypot(nx, ny, 1);
      const i = (y * size + x) * 4;
      image.data[i] = (nx / len * 0.5 + 0.5) * 255;
      image.data[i + 1] = (ny / len * 0.5 + 0.5) * 255;
      image.data[i + 2] = (1 / len * 0.5 + 0.5) * 255;
      image.data[i + 3] = 255;
    }
  }
  ctx.putImageData(image, 0, 0);
  const texture = new THREE.CanvasTexture(c);
  texture.wrapS = texture.wrapT = THREE.RepeatWrapping;
  texture.anisotropy = maxAnisotropy;
  surfaceCache.set('weave', texture);
  return texture;
}

// Soft rectangular shadow (white = opaque) for use as an alphaMap.
export function softShadow() {
  return cachedCanvasTexture('soft-shadow', (ctx) => {
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, SIZE, SIZE);
    ctx.filter = `blur(${SIZE * 0.05}px)`;
    ctx.fillStyle = '#fff';
    ctx.fillRect(SIZE * 0.12, SIZE * 0.12, SIZE * 0.76, SIZE * 0.76);
    ctx.filter = 'none';
  }, false);
}

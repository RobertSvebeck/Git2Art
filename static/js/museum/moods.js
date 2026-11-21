// Curated room atmospheres. Each room picks one and varies it slightly.

export const MOODS = [
  {
    name: 'White Cube', wall: 0xeeebe4, trim: 0xd6d1c7, floor: 'oak', ceilings: ['skylight', 'beams'],
    light: 0xfff2e0, sky: 0xfffaf0, ground: 0x8a7f70, ambient: 0.9, spot: 1.0, exposure: 1.0,
    accent: null, frames: ['thin-black', 'float', 'white-mat'], fog: 0xbdb7ad,
  },
  {
    name: 'Salon', wall: 0x5c1d24, trim: 0x3a1015, floor: 'walnut', ceilings: ['coffered'],
    light: 0xffd6a0, sky: 0xffe2c0, ground: 0x2a0c0c, ambient: 0.45, spot: 1.4, exposure: 1.05,
    accent: null, frames: ['gold', 'gold', 'walnut'], fog: 0x1f0d0c,
  },
  {
    name: 'Nocturne', wall: 0x1a2240, trim: 0x10162c, floor: 'black-marble', ceilings: ['dark'],
    light: 0xd6e4ff, sky: 0x5d6fa8, ground: 0x05060c, ambient: 0.28, spot: 1.8, exposure: 1.1,
    accent: 0x4fc3ff, frames: ['float', 'thin-black'], fog: 0x05070f,
  },
  {
    name: 'Verdigris', wall: 0x2e5c54, trim: 0x1f413b, floor: 'terrazzo', ceilings: ['skylight', 'coffered'],
    light: 0xf2fff4, sky: 0xe6fff4, ground: 0x13241f, ambient: 0.6, spot: 1.2, exposure: 1.0,
    accent: null, frames: ['brass', 'thin-black'], fog: 0x14231f,
  },
  {
    name: 'Sandstone', wall: 0xd6c09c, trim: 0xb59d77, floor: 'travertine', ceilings: ['coffered', 'skylight'],
    light: 0xffe6c0, sky: 0xfff0d8, ground: 0x6b5a42, ambient: 0.75, spot: 1.0, exposure: 0.95,
    accent: null, frames: ['walnut', 'white-mat', 'brass'], fog: 0x7d6e58,
  },
  {
    name: 'Graphite', wall: 0x2a2a2e, trim: 0x18181b, floor: 'concrete', ceilings: ['dark', 'beams'],
    light: 0xffffff, sky: 0x9a9aa4, ground: 0x0a0a0b, ambient: 0.3, spot: 2.0, exposure: 1.05,
    accent: 0xff9a3c, frames: ['float', 'thin-black'], fog: 0x09090a,
  },
  {
    name: 'Blush', wall: 0xe5c4bf, trim: 0xcaa39d, floor: 'oak', ceilings: ['skylight'],
    light: 0xfff0ea, sky: 0xfff4f0, ground: 0x7a5c58, ambient: 0.8, spot: 1.0, exposure: 1.0,
    accent: null, frames: ['white-mat', 'thin-black', 'brass'], fog: 0xa88c88,
  },
  {
    name: 'Ultraviolet', wall: 0x261540, trim: 0x170c28, floor: 'black-marble', ceilings: ['dark'],
    light: 0xe8dcff, sky: 0x5b3c8f, ground: 0x07030d, ambient: 0.3, spot: 1.8, exposure: 1.1,
    accent: 0xc86bff, frames: ['float', 'thin-black'], fog: 0x0a0512,
  },
];

// Only used by the light installation wing: darkness so the light can speak.
export const VOID_MOOD = {
  name: 'Void', wall: 0x060608, trim: 0x0c0c10, floor: 'black-marble', ceilings: ['dark'],
  light: 0xbfcfff, sky: 0x1a2036, ground: 0x000000, ambient: 0.12, spot: 0, exposure: 1.0,
  accent: null, frames: ['float'], fog: 0x000000, fill: 0, environment: 0.02,
};

export const FRAME_STYLES = {
  'thin-black': { border: 0.05, depth: 0.05, color: 0x121212, metalness: 0.0, roughness: 0.5, mat: 0 },
  'float': { border: 0.0, depth: 0.05, color: 0x1c1c1c, metalness: 0.0, roughness: 0.7, mat: 0 },
  'white-mat': { border: 0.04, depth: 0.05, color: 0xf3f1ec, metalness: 0.0, roughness: 0.6, mat: 0.16 },
  'gold': { border: 0.13, depth: 0.09, color: 0xc29a45, metalness: 1.0, roughness: 0.32, mat: 0 },
  'walnut': { border: 0.09, depth: 0.07, color: 0x4a2c1a, metalness: 0.0, roughness: 0.55, mat: 0.08 },
  'brass': { border: 0.06, depth: 0.06, color: 0xb08d4c, metalness: 0.9, roughness: 0.3, mat: 0 },
};

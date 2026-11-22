// Draws a repository sculpture on a 2D canvas (no WebGL needed).

import { buildForm } from '../shared/repoform.js';
import { throttled } from '../shared/throttle.js';

const CAMERA_DISTANCE = 4.2;
const GROW_SECONDS = 7;
const HOLD_SECONDS = 3;

const dataCache = new Map();

export function loadData(url) {
  if (!dataCache.has(url)) dataCache.set(url, throttled(() => fetch(url)).then((r) => (r.ok ? r.json() : Promise.reject(r.status))));
  return dataCache.get(url);
}

function rgba(colour, alpha, lift = 0) {
  const [r, g, b] = colour.map((c) => Math.round(Math.min(1, c + lift) * 255));
  return `rgba(${r},${g},${b},${alpha})`;
}

export class SculptureCanvas {
  constructor(canvas, data) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.form = buildForm(data, { height: 1.8, radius: 0.8 });
    this.angle = 0.6;
    this.progress = 1;
    this.clock = GROW_SECONDS + HOLD_SECONDS;
    this.active = false;
    this.draw();
  }

  setActive(active) {
    if (active && !this.active) this.clock = 0;
    this.active = active;
    if (!active) {
      this.progress = 1;
      this.draw();
    }
  }

  tick(dt) {
    if (!this.active) return;
    this.angle += dt * 0.35;
    this.clock = (this.clock + dt) % (GROW_SECONDS + HOLD_SECONDS);
    this.progress = Math.min(1, this.clock / GROW_SECONDS) * 1.02 - 0.01;
    this.draw();
  }

  project([x, y, z]) {
    const cos = Math.cos(this.angle), sin = Math.sin(this.angle);
    const rx = x * cos + z * sin;
    const rz = -x * sin + z * cos;
    const f = CAMERA_DISTANCE / (CAMERA_DISTANCE + rz);
    const { width, height } = this.canvas;
    const scale = height * 0.5;
    return [width / 2 + rx * scale * f, height * 0.96 - (y - 0.1) * scale * f, rz, f * scale];
  }

  draw() {
    const { ctx, canvas, form, progress } = this;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.lineCap = 'round';
    for (const branch of form.branches) {
      if (branch.born > progress) continue;
      const [x0, y0, , s0] = this.project(branch.from);
      const [x1, y1] = this.project(branch.to);
      const mx = (x0 + x1) / 2 - (y1 - y0) * branch.bend * 0.45;
      const my = (y0 + y1) / 2 + (x1 - x0) * branch.bend * 0.45;
      ctx.strokeStyle = 'rgba(176, 141, 76, 0.85)';
      ctx.lineWidth = Math.max(0.8, branch.weight * 0.18 * s0);
      ctx.beginPath();
      ctx.moveTo(x0, y0);
      ctx.quadraticCurveTo(mx, my, x1, y1);
      ctx.stroke();
    }

    const visible = form.stars.filter((s) => s.born <= progress)
      .map((s) => ({ star: s, p: this.project(s.position) }))
      .sort((a, b) => b.p[2] - a.p[2]);

    ctx.globalCompositeOperation = 'lighter';
    ctx.lineWidth = 0.6;
    for (const { star, p } of visible) {
      const dir = form.dirs.get(star.path.includes('/') ? star.path.slice(0, star.path.lastIndexOf('/')) : '');
      const [dx, dy] = this.project(dir);
      ctx.strokeStyle = rgba(star.colour, 0.18);
      ctx.beginPath();
      ctx.moveTo(dx, dy);
      ctx.lineTo(p[0], p[1]);
      ctx.stroke();
    }
    for (const { star, p } of visible) {
      const r = Math.max(1.2, star.radius * p[3]);
      const age = progress - star.born;
      const flash = progress < 1 ? Math.max(0, 1 - age / 0.06) : 0;
      const glow = ctx.createRadialGradient(p[0], p[1], 0, p[0], p[1], r * 3.2);
      glow.addColorStop(0, rgba(star.colour, 0.35 + flash * 0.5, flash * 0.4));
      glow.addColorStop(1, rgba(star.colour, 0));
      ctx.fillStyle = glow;
      ctx.beginPath();
      ctx.arc(p[0], p[1], r * 3.2, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalCompositeOperation = 'source-over';
    for (const { star, p } of visible) {
      const r = Math.max(1.2, star.radius * p[3]);
      const body = ctx.createRadialGradient(p[0] - r * 0.35, p[1] - r * 0.35, r * 0.1, p[0], p[1], r);
      body.addColorStop(0, rgba(star.colour, 1, 0.45));
      body.addColorStop(1, rgba(star.colour, 0.95, -0.12));
      ctx.fillStyle = body;
      ctx.beginPath();
      ctx.arc(p[0], p[1], r, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

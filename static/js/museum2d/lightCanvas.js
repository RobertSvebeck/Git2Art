// Draws a light installation (commit spiral) on a 2D canvas.

import { commitField } from '../shared/repoform.js';

const CYCLE_SECONDS = 14;
const CAMERA_DISTANCE = 12;
const TILT = 0.32;

export class LightCanvas {
  constructor(canvas, data) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.field = commitField(data, { radius: 4.5, bottom: 0, top: 3.6, maxPoints: 2600 });
    this.angle = 0.4;
    this.clock = 0;
    this.cursor = 1.5;
    this.active = false;
    this.draw();
  }

  setActive(active) {
    if (active && !this.active) this.clock = 0;
    this.active = active;
    if (!active) {
      this.cursor = 1.5;
      this.draw();
    }
  }

  tick(dt) {
    if (!this.active) return;
    this.angle += dt * 0.18;
    this.clock = (this.clock + dt) % CYCLE_SECONDS;
    this.cursor = (this.clock / (CYCLE_SECONDS - 2)) * 1.05 - 0.02;
    this.draw();
  }

  draw() {
    const { ctx, canvas, field } = this;
    const { width, height } = canvas;
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = '#030305';
    ctx.fillRect(0, 0, width, height);
    ctx.globalCompositeOperation = 'lighter';

    const cos = Math.cos(this.angle), sin = Math.sin(this.angle);
    const tc = Math.cos(TILT), ts = Math.sin(TILT);
    const scale = height * 1.05;
    const { positions, colours, times, sizes } = field;
    for (let i = 0; i < field.count; i++) {
      const x = positions[i * 3], y = positions[i * 3 + 1] - 1.8, z = positions[i * 3 + 2];
      const rx = x * cos + z * sin;
      const rz = -x * sin + z * cos;
      const ry = y * tc - rz * ts;
      const dz = y * ts + rz * tc;
      const f = scale / (CAMERA_DISTANCE + dz);
      const px = width / 2 + rx * f;
      const py = height * 0.56 - ry * f;
      const d = times[i] - this.cursor;
      const pulse = Math.exp(-d * d * 900);
      const past = times[i] <= this.cursor ? 1 : 0;
      const k = 0.45 + 0.3 * past + 1.5 * pulse;
      const r = Math.max(0.8, sizes[i] * f * 0.03 * (1 + 0.9 * pulse));
      const red = Math.min(255, colours[i * 3] * 255 * k);
      const green = Math.min(255, colours[i * 3 + 1] * 255 * k);
      const blue = Math.min(255, colours[i * 3 + 2] * 255 * k);
      ctx.fillStyle = `rgba(${red | 0},${green | 0},${blue | 0},${0.55 + 0.45 * pulse})`;
      ctx.beginPath();
      ctx.arc(px, py, r, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

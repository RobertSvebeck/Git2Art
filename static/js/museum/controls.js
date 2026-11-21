// First-person walking: pointer lock + keys on desktop, joystick + drag on touch.

import * as THREE from 'three';

const EYE_HEIGHT = 1.65;
const WALK_SPEED = 2.6;
const RUN_SPEED = 5.5;
const ACCELERATION = 10;
const LOOK_SENSITIVITY = 0.0022;
const TOUCH_LOOK = 0.005;
const JOYSTICK_RADIUS = 55;
const PITCH_LIMIT = Math.PI / 2 - 0.05;
const TURN_SPEED = 1.9;

export class Walker {
  constructor(camera, element, isWalkable) {
    this.camera = camera;
    this.element = element;
    this.isWalkable = isWalkable;
    this.position = new THREE.Vector3(0, EYE_HEIGHT, 0);
    this.velocity = new THREE.Vector2();
    this.yaw = 0;
    this.pitch = 0;
    this.keys = new Set();
    this.joystick = null;
    this.lookTouch = null;
    this.bobPhase = 0;
    this.enabled = false;
    this.onTap = null;
    this.bindDesktop();
    this.bindTouch();
  }

  get locked() {
    return document.pointerLockElement === this.element;
  }

  lock() {
    this.element.requestPointerLock?.();
  }

  bindDesktop() {
    document.addEventListener('keydown', (e) => {
      if (['KeyW', 'KeyA', 'KeyS', 'KeyD', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ShiftLeft', 'ShiftRight'].includes(e.code)) {
        this.keys.add(e.code);
        if (e.code.startsWith('Arrow')) e.preventDefault();
      }
    });
    document.addEventListener('keyup', (e) => this.keys.delete(e.code));
    window.addEventListener('blur', () => this.keys.clear());
    document.addEventListener('mousemove', (e) => {
      if (!this.locked || !this.enabled) return;
      this.turn(e.movementX * LOOK_SENSITIVITY, e.movementY * LOOK_SENSITIVITY);
    });
  }

  bindTouch() {
    const el = this.element;
    el.addEventListener('touchstart', (e) => {
      if (!this.enabled) return;
      for (const t of e.changedTouches) {
        if (t.clientX < window.innerWidth * 0.45 && !this.joystick) {
          this.joystick = { id: t.identifier, x0: t.clientX, y0: t.clientY, dx: 0, dy: 0 };
          this.showJoystick(t.clientX, t.clientY);
        } else if (!this.lookTouch) {
          this.lookTouch = { id: t.identifier, x: t.clientX, y: t.clientY, moved: 0, start: performance.now() };
        }
      }
      e.preventDefault();
    }, { passive: false });
    el.addEventListener('touchmove', (e) => {
      for (const t of e.changedTouches) {
        if (this.joystick && t.identifier === this.joystick.id) {
          let dx = t.clientX - this.joystick.x0, dy = t.clientY - this.joystick.y0;
          const len = Math.hypot(dx, dy);
          if (len > JOYSTICK_RADIUS) { dx *= JOYSTICK_RADIUS / len; dy *= JOYSTICK_RADIUS / len; }
          this.joystick.dx = dx / JOYSTICK_RADIUS;
          this.joystick.dy = dy / JOYSTICK_RADIUS;
          this.moveKnob(dx, dy);
        } else if (this.lookTouch && t.identifier === this.lookTouch.id) {
          const dx = t.clientX - this.lookTouch.x, dy = t.clientY - this.lookTouch.y;
          this.lookTouch.moved += Math.abs(dx) + Math.abs(dy);
          this.lookTouch.x = t.clientX;
          this.lookTouch.y = t.clientY;
          this.turn(dx * TOUCH_LOOK, dy * TOUCH_LOOK);
        }
      }
      e.preventDefault();
    }, { passive: false });
    const end = (e) => {
      for (const t of e.changedTouches) {
        if (this.joystick && t.identifier === this.joystick.id) {
          this.joystick = null;
          this.hideJoystick();
        } else if (this.lookTouch && t.identifier === this.lookTouch.id) {
          const tap = this.lookTouch.moved < 12 && performance.now() - this.lookTouch.start < 350;
          this.lookTouch = null;
          if (tap && this.onTap) this.onTap(t.clientX, t.clientY);
        }
      }
    };
    el.addEventListener('touchend', end);
    el.addEventListener('touchcancel', end);
  }

  showJoystick(x, y) {
    const pad = document.getElementById('joystick');
    if (!pad) return;
    pad.style.left = `${x}px`;
    pad.style.top = `${y}px`;
    pad.classList.add('visible');
    this.moveKnob(0, 0);
  }

  moveKnob(dx, dy) {
    const knob = document.getElementById('joystick-knob');
    if (knob) knob.style.transform = `translate(calc(-50% + ${dx}px), calc(-50% + ${dy}px))`;
  }

  hideJoystick() {
    document.getElementById('joystick')?.classList.remove('visible');
  }

  turn(dx, dy) {
    this.yaw -= dx;
    this.pitch = Math.max(-PITCH_LIMIT, Math.min(PITCH_LIMIT, this.pitch - dy));
  }

  inputVector() {
    let forward = 0, strafe = 0;
    if (this.keys.has('KeyW') || this.keys.has('ArrowUp')) forward += 1;
    if (this.keys.has('KeyS') || this.keys.has('ArrowDown')) forward -= 1;
    if (this.keys.has('KeyD')) strafe += 1;
    if (this.keys.has('KeyA')) strafe -= 1;
    if (this.joystick) {
      forward -= this.joystick.dy;
      strafe += this.joystick.dx;
    }
    const length = Math.hypot(forward, strafe);
    if (length > 1) { forward /= length; strafe /= length; }
    return [forward, strafe];
  }

  update(dt) {
    const [forward, strafe] = this.enabled ? this.inputVector() : [0, 0];
    if (this.enabled) {
      const turn = (this.keys.has('ArrowLeft') ? 1 : 0) - (this.keys.has('ArrowRight') ? 1 : 0);
      this.yaw += turn * TURN_SPEED * dt;
    }
    const running = this.keys.has('ShiftLeft') || this.keys.has('ShiftRight');
    const speed = running ? RUN_SPEED : WALK_SPEED;
    const sin = Math.sin(this.yaw), cos = Math.cos(this.yaw);
    const targetX = (-sin * forward + cos * strafe) * speed;
    const targetZ = (-cos * forward - sin * strafe) * speed;
    const k = 1 - Math.exp(-ACCELERATION * dt);
    this.velocity.x += (targetX - this.velocity.x) * k;
    this.velocity.y += (targetZ - this.velocity.y) * k;

    const nx = this.position.x + this.velocity.x * dt;
    if (this.isWalkable(nx, this.position.z)) this.position.x = nx;
    else this.velocity.x = 0;
    const nz = this.position.z + this.velocity.y * dt;
    if (this.isWalkable(this.position.x, nz)) this.position.z = nz;
    else this.velocity.y = 0;

    const moving = this.velocity.length();
    this.bobPhase += dt * moving * 2.4;
    const bob = Math.sin(this.bobPhase) * 0.025 * Math.min(1, moving / WALK_SPEED);

    this.camera.position.set(this.position.x, EYE_HEIGHT + bob, this.position.z);
    this.camera.rotation.set(this.pitch, this.yaw, 0, 'YXZ');
  }
}

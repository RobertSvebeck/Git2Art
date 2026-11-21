// Real lights follow the visitor: a pool of spotlights is re-aimed at the
// artworks of the current room, and fog, sky and exposure blend between moods.

import * as THREE from 'three';
import { CELL } from './plan.js';

const SPOT_INTENSITY = 32;
const FILL_INTENSITY = 40;
const BLEND_TAU = 0.6;
const ENVIRONMENT = 0.14;

export class Lighting {
  constructor(scene, renderer, spotCount) {
    this.scene = scene;
    this.renderer = renderer;
    this.hemisphere = new THREE.HemisphereLight(0xffffff, 0x444444, 0.8);
    scene.add(this.hemisphere);
    this.fill = new THREE.PointLight(0xffffff, 0, 0, 2);
    scene.add(this.fill);
    this.spots = [];
    for (let i = 0; i < spotCount; i++) {
      const spot = new THREE.SpotLight(0xffffff, 0, 0, 0.4, 0.65, 2);
      spot.userData.goal = 0;
      scene.add(spot);
      scene.add(spot.target);
      this.spots.push(spot);
    }
    this.goal = null;
    this.fogColour = new THREE.Color(0x000000);
    this.exposure = 1;
  }

  focus(room) {
    const { mood, height } = room.plan;
    this.goal = {
      sky: new THREE.Color(mood.sky),
      ground: new THREE.Color(mood.ground),
      ambient: mood.ambient,
      fog: new THREE.Color(mood.fog),
      exposure: mood.exposure,
      environment: mood.environment ?? ENVIRONMENT,
      fill: mood.fill ?? FILL_INTENSITY * mood.ambient * (height / 6) ** 2,
    };
    this.fill.color.set(mood.light);
    this.fill.position.set(room.plan.cx * CELL, height - 1.2, room.plan.cz * CELL);
    this.spots.forEach((spot, i) => {
      const fixture = room.fixtures[i];
      if (!fixture) {
        spot.userData.goal = 0;
        return;
      }
      spot.intensity = 0;
      spot.position.copy(fixture.position);
      spot.target.position.copy(fixture.target);
      spot.angle = fixture.angle;
      spot.color.set(mood.light);
      spot.userData.goal = SPOT_INTENSITY * mood.spot;
    });
  }

  update(dt) {
    if (!this.goal) return;
    const k = 1 - Math.exp(-dt / BLEND_TAU);
    const g = this.goal;
    this.hemisphere.color.lerp(g.sky, k);
    this.hemisphere.groundColor.lerp(g.ground, k);
    this.hemisphere.intensity += (g.ambient - this.hemisphere.intensity) * k;
    this.fill.intensity += (g.fill - this.fill.intensity) * k;
    this.fogColour.lerp(g.fog, k);
    this.scene.fog.color.copy(this.fogColour);
    this.scene.background = this.fogColour;
    this.exposure += (g.exposure - this.exposure) * k;
    this.renderer.toneMappingExposure = this.exposure;
    this.scene.environmentIntensity += (g.environment - this.scene.environmentIntensity) * k;
    for (const spot of this.spots) spot.intensity += (spot.userData.goal - spot.intensity) * k;
  }
}

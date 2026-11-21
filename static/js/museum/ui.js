// HTML overlays: intro, pause, room titles, hover caption and artwork panel.

import { styleLabel } from './roomArt.js';

const $ = (id) => document.getElementById(id);

export class Ui {
  constructor() {
    this.panelOpen = false;
    this.onEnter = null;
    this.onClosePanel = null;
    this.roomTimer = null;
    $('enter-button').addEventListener('click', () => this.enter());
    $('resume-button').addEventListener('click', () => this.enter());
    $('panel-close').addEventListener('click', () => this.closePanel());
    document.addEventListener('keydown', (e) => {
      if (e.code === 'Escape' && this.panelOpen) this.closePanel();
    });
  }

  ready(count, seed, touch) {
    $('intro-status').textContent = `${count} artworks in the collection`;
    $('enter-button').disabled = false;
    $('enter-button').textContent = 'Enter the museum';
    $('controls-desktop').hidden = touch;
    $('controls-touch').hidden = !touch;
    $('share-link').href = `${window.location.pathname}?seed=${seed}`;
  }

  showError(message) {
    $('intro-status').textContent = `The museum is closed: ${message}`;
    $('enter-button').hidden = true;
  }

  enter() {
    this.hideOverlays();
    $('hud').hidden = false;
    if (this.onEnter) this.onEnter();
  }

  hideOverlays() {
    $('intro').hidden = true;
    $('paused').hidden = true;
  }

  showPaused() {
    $('paused').hidden = false;
  }

  enterRoom(plan, visited) {
    $('hud-room').textContent = `Room ${plan.cx}, ${plan.cz}`;
    $('hud-visited').textContent = `${visited} visited`;
    const title = $('room-title');
    $('room-title-name').textContent = plan.mood.name;
    $('room-title-meta').textContent = `${plan.slots.length} works`;
    title.classList.remove('visible');
    void title.offsetWidth;
    title.classList.add('visible');
    clearTimeout(this.roomTimer);
    this.roomTimer = setTimeout(() => title.classList.remove('visible'), 2600);
  }

  setHover(artwork) {
    const hover = $('hover');
    $('crosshair').classList.toggle('active', Boolean(artwork));
    if (!artwork) {
      hover.classList.remove('visible');
      return;
    }
    $('hover-title').textContent = artwork.title;
    $('hover-meta').textContent = `${styleLabel(artwork.style)}  |  click for details`;
    hover.classList.add('visible');
  }

  showArtwork(artwork) {
    this.panelOpen = true;
    $('panel-image').src = artwork.image;
    $('panel-image').alt = `${artwork.title}, ${styleLabel(artwork.style)} style`;
    $('panel-title').textContent = artwork.title;
    $('panel-style').textContent = `${styleLabel(artwork.style)} style`;
    $('panel-likes').textContent = `${artwork.likes} ${artwork.likes === 1 ? 'like' : 'likes'}`;
    $('panel-view').href = `/artwork/${artwork.id}`;
    $('panel-repo').href = artwork.repo_url;
    $('panel').hidden = false;
    this.setHover(null);
  }

  closePanel() {
    this.panelOpen = false;
    $('panel').hidden = true;
    if (this.onClosePanel) this.onClosePanel();
  }
}

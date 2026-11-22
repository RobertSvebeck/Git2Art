// HTML overlays: intro, pause, room titles, hover caption and artwork panel.

import { styleLabel } from './roomArt.js';

const $ = (id) => document.getElementById(id);

function formatStars(stars) {
  return stars >= 1000 ? `${(stars / 1000).toFixed(1).replace('.0', '')}k` : String(stars);
}

export class Ui {
  constructor() {
    this.panelOpen = false;
    this.onEnter = null;
    this.onClosePanel = null;
    this.roomTimer = null;
    $('enter-button').addEventListener('click', () => this.enter());
    $('resume-button').addEventListener('click', () => this.enter());
    $('panel-close').addEventListener('click', () => this.closePanel());
    $('panel-teleport').addEventListener('click', () => {
      const owner = this.panelOwner;
      if (owner && this.onTeleport) this.onTeleport(owner);
      this.closePanel();
    });
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
    $('hud-room').textContent = plan.artist ? `The room of ${plan.artist.owner}` : `Room ${plan.cx}, ${plan.cz}`;
    $('hud-visited').textContent = `${visited} visited`;
    const title = $('room-title');
    const works = plan.wing === 'light' ? 1 : plan.slots.length + plan.furniture.filter((f) => f.type === 'plinth').length;
    $('room-title-name').textContent = plan.artist ? `The room of ${plan.artist.owner}`
      : plan.wing === 'light' ? 'Light Installation' : plan.mood.name;
    $('room-title-meta').textContent = plan.artist
      ? `${works} ${works === 1 ? 'work' : 'works'}  |  any door leads back to the galleries`
      : `${works} ${works === 1 ? 'work' : 'works'}`;
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
    $('hover-meta').textContent = artwork.kind === 'submit'
      ? 'Place your repository in this museum  |  click or Enter'
      : `${artwork.owner ? `by ${artwork.owner}  |  ` : ''}${styleLabel(artwork.style)}  |  click or Enter for details`;
    hover.classList.add('visible');
  }

  showArtwork(artwork) {
    this.panelOpen = true;
    $('panel-image').src = artwork.image;
    $('panel-image').alt = `${artwork.title}, ${styleLabel(artwork.style)} style`;
    $('panel-title').textContent = artwork.title;
    const special = artwork.style === 'sculpture' || artwork.style === 'installation';
    $('panel-style').textContent = special ? styleLabel(artwork.style) : `${styleLabel(artwork.style)} style`;
    $('panel-stats').textContent = artwork.stats || '';
    $('panel-stats').hidden = !artwork.stats;
    $('panel-view').textContent = special ? 'View painting' : 'View artwork';
    $('panel-likes').textContent = `${artwork.likes} ${artwork.likes === 1 ? 'like' : 'likes'}`;
    $('panel-view').href = `/artwork/${artwork.id}`;
    $('panel-repo').href = artwork.repo_url;
    $('panel-repo').innerHTML = `&#9733; Star on GitHub${artwork.stars ? ` &middot; ${formatStars(artwork.stars)}` : ''}`;
    $('panel-artist').hidden = !artwork.owner;
    if (artwork.owner) {
      $('panel-artist').href = artwork.profile;
      $('panel-avatar').src = artwork.avatar;
      $('panel-owner').textContent = artwork.owner;
      $('panel-crew').textContent = artwork.contributors > 1 ? `${artwork.contributors} contributors  |  GitHub profile` : 'GitHub profile';
    }
    const canTeleport = Boolean(this.onTeleport && artwork.owner && this.canTeleport?.(artwork.owner));
    $('panel-teleport').hidden = !canTeleport;
    this.panelOwner = artwork.owner;
    $('panel').hidden = false;
    this.setHover(null);
  }

  suggestLite() {
    $('lite-hint').hidden = false;
    setTimeout(() => { $('lite-hint').hidden = true; }, 12000);
  }

  closePanel() {
    this.panelOpen = false;
    $('panel').hidden = true;
    if (this.onClosePanel) this.onClosePanel();
  }
}

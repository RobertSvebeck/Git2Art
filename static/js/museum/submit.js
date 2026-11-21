// In-museum submission: generate art for a GitHub repository and hang it
// in place of the invitation the visitor clicked.

const $ = (id) => document.getElementById(id);

export class SubmitPanel {
  constructor({ onOpen, onClose, onHang }) {
    this.onOpen = onOpen;
    this.onClose = onClose;
    this.onHang = onHang;
    this.poster = null;
    this.busy = false;
    $('submit-form').addEventListener('submit', (e) => {
      e.preventDefault();
      this.generate();
    });
    $('submit-close').addEventListener('click', () => this.close());
    $('submit-walk').addEventListener('click', () => this.close());
    document.addEventListener('keydown', (e) => {
      if (e.code === 'Escape' && this.isOpen && !this.busy) this.close();
    });
  }

  get isOpen() {
    return !$('submit-panel').hidden;
  }

  open(poster) {
    this.poster = poster;
    $('submit-panel').hidden = false;
    $('submit-form').hidden = false;
    $('submit-done').hidden = true;
    $('submit-status').textContent = '';
    if (this.onOpen) this.onOpen();
    setTimeout(() => $('submit-url').focus(), 50);
  }

  close() {
    $('submit-panel').hidden = true;
    if (this.onClose) this.onClose();
  }

  async generate() {
    if (this.busy) return;
    const url = $('submit-url').value.trim();
    const style = $('submit-style').value;
    if (!/^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/.test(url)) {
      $('submit-status').textContent = 'Please enter a public GitHub repository URL, like https://github.com/owner/repo';
      return;
    }
    this.busy = true;
    $('submit-button').disabled = true;
    const messages = ['Cloning the repository...', 'Reading its history...', 'Painting...', 'Varnishing...'];
    let step = 0;
    $('submit-status').textContent = messages[0];
    const ticker = setInterval(() => {
      step = Math.min(messages.length - 1, step + 1);
      $('submit-status').textContent = messages[step];
    }, 4000);
    try {
      const response = await fetch('/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ github_url: url, art_style: style }),
      });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error(data.error || 'Generation failed');
      const aspect = await imageAspect(data.image_url);
      const artwork = {
        id: data.artwork_id, title: data.repo_name, repo_url: url, style: data.art_style,
        likes: 0, image: data.image_url, aspect,
      };
      if (this.onHang) this.onHang(this.poster, artwork);
      $('submit-form').hidden = true;
      $('submit-done').hidden = false;
      $('submit-preview').src = data.image_url;
      $('submit-view').href = `/artwork/${data.artwork_id}`;
      $('submit-done-title').textContent = `${data.repo_name} now hangs in the museum`;
    } catch (error) {
      $('submit-status').textContent = error.message;
    } finally {
      clearInterval(ticker);
      this.busy = false;
      $('submit-button').disabled = false;
    }
  }
}

function imageAspect(url) {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(img.naturalWidth / img.naturalHeight || 1);
    img.onerror = () => resolve(1);
    img.src = url;
  });
}

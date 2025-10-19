# Git2Art - Quick Start Guide

## Phase 1: Web Application ✅ COMPLETED

The Flask web application is ready to use!

## Setup Instructions

### 1. Install All Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- GitPython (git operations)
- Pillow (image processing)
- NumPy (numerical operations)
- Matplotlib (plotting/visualization)

### 2. Verify Installation

```bash
# Check if all packages are installed
pip list | grep -E "Flask|GitPython|Pillow|numpy|matplotlib"
```

You should see all five packages listed.

### 3. Run the Web Application

```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`

**Note**: If port 5000 is in use (common on macOS with AirPlay Receiver), either:
- Disable AirPlay Receiver in System Settings → General → AirDrop & Handoff
- Or modify `app.py` to use a different port

### 4. Use the Web Interface

1. Open your browser to `http://localhost:5000`
2. Enter a GitHub repository URL (e.g., `https://github.com/flask/flask`)
3. Click "Generate Art"
4. Wait for the artwork to be generated (30 seconds - 2 minutes)
5. Download your artwork!

## Features

### Smart Caching ⚡
The app automatically caches generated artwork based on the repository's commit hash. If you request art for the same repository again and nothing has changed, it will instantly serve the cached version.

Cache files are stored in:
- `static/generated/` - Generated PNG images
- `static/generated/.{repo_name}_cache.json` - Cache metadata

### Automatic Watermarking 🏷️
All generated images include a subtle watermark in the bottom-right corner showing:
- "git2art" branding
- The GitHub repository URL

### Repository Management 📁
Cloned repositories are stored in `temp_repos/` and are automatically:
- Cloned on first request
- Updated (git fetch + reset) on subsequent requests
- Reused to save time and bandwidth

## Command-Line Usage

You can still use the original CLI tool:

```bash
# Generate art from current repository
python git2art.py

# Generate from specific repository
python git2art.py --repo /path/to/repo

# With custom settings
python git2art.py --aspect 16:9 --size 1920 --contrast high
```

## Troubleshooting

### "ModuleNotFoundError"
Run `pip install -r requirements.txt` to install all dependencies.

### "Port 5000 is in use"
Either:
1. Disable AirPlay Receiver on macOS
2. Kill the process: `lsof -ti:5000 | xargs kill -9`
3. Change the port in `app.py`

### "Failed to clone repository"
- Verify the GitHub URL is correct and the repository is public
- Check your internet connection
- Ensure git is installed: `git --version`

### Generation Takes Too Long
- Large repositories (1000+ files) can take 2-5 minutes
- The first generation is always slower (cloning + generation)
- Subsequent generations of the same repo are instant (cached)

## File Structure

```
Git2Art/
├── app.py                    # Flask application entry point
├── routes/                   # Web endpoints
├── services/                 # Business logic
│   ├── art_service.py       # Art generation + caching
│   └── git_service.py       # Git operations
├── utils/                    # Utilities
│   └── watermark.py         # Image watermarking
├── templates/               # HTML templates
├── static/
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript
│   └── generated/           # Generated images (gitignored)
└── temp_repos/              # Cloned repos (gitignored)
```

## Next Steps (Phase 2)

Coming soon:
- Gallery page to browse all generated art
- Repository comparison
- Like/favorite functionality
- Share links to generated art

## Support

For issues or questions:
- GitHub: https://github.com/RobertSvebeck/Git2Art
- Check existing documentation: README.md, FLASK_SETUP.md, ART_THEORY.md

---

**Enjoy turning code into art!** 🎨

# Git2Art Flask Web Application

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python app.py
   ```

3. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## Features

- ✅ GitHub URL input form with validation
- ✅ Automatic artwork generation from any public GitHub repository
- ✅ Smart caching based on commit hash (avoids regeneration)
- ✅ Watermark with repository URL
- ✅ Download button for generated artwork
- ✅ Beautiful, responsive UI

## How It Works

1. Enter a GitHub repository URL (e.g., `https://github.com/owner/repo`)
2. Click "Generate Art"
3. The app will:
   - Clone the repository to a temporary location
   - Check if artwork already exists for this commit
   - Generate new artwork if needed (or use cached version)
   - Add a subtle watermark
   - Display the artwork with download option

## File Structure

```
Git2Art/
├── app.py                 # Flask application factory
├── routes/
│   └── main_routes.py    # Web endpoints
├── services/
│   ├── art_service.py    # Art generation logic
│   └── git_service.py    # Git operations
├── utils/
│   └── watermark.py      # Watermark utility
├── templates/
│   └── index.html        # Main page
├── static/
│   ├── css/style.css     # Stylesheets
│   ├── js/app.js         # JavaScript
│   └── generated/        # Generated artwork (gitignored)
└── temp_repos/            # Cloned repos (gitignored)
```

## Caching System

The app uses a filesystem-based caching system:
- Each generated artwork is stored with a JSON cache file
- Cache includes: commit hash, filename, repo name
- If the repository hasn't changed (same commit hash), cached art is served
- This prevents unnecessary regeneration and speeds up repeated requests

## Next Steps (Phase 2)

- Gallery page to browse all generated art
- Repository metadata display
- Sort and filter options

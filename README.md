# Git2Art

Turn your git repository into a beautiful piece of abstract art!

[![GitHub](https://img.shields.io/badge/github-RobertSvebeck%2FGit2Art-blue)](https://github.com/RobertSvebeck/Git2Art)

## Concept

Git2Art creates deterministic abstract art from your codebase:
- **Small changes** in code = **small changes** in the artwork
- **Big changes** in many files = **big changes** in the artwork
- Same code always generates the same art (byte-for-byte identical)

## Art Styles

Every style is drawn from the repository's actual structure (folders, file sizes, languages and history), so each repository looks different and you can see why. Layouts are seeded by file paths, so a small change to the code is a small change to the picture.

- **Expressionist** (default) - Gestural bristle-brush painting: a sweep for every folder, black calligraphy along the folder tree, splatter and drips from the most-edited files
- **Impressionist** - Broken brushstrokes swirling around each folder like eddies in a pond; the busiest files catch the light
- **Watercolour** (`watercolor`) - Layered transparent glazes on cold-press paper: folders as washes, files as glazes, an ink sketch of the folder tree
- **Psychedelic** - An op-art poster: every folder is the eye of a spiral, the spirals interfere into neon bands, the largest folders bloom into mandalas
- **Pixel City** (`pixel_city`) - An isometric 8-bit city: folders are districts, files are buildings, documentation is parkland, the time of day shows how recently the project was active
- **De Stijl** (`de_stijl`) - A Mondrian-style composition that maps the code exactly: folders divide the canvas by size, primary colours mark the heaviest and busiest code
- **Garden** - A botanical plate: folders grow as plants, files are leaves, the busiest files flower, contributors are butterflies
- **Tapestry** - The history woven as cloth: a warp band per folder, weft rows from first commit to today, colour where the code grew
- **Constellation** - The directory tree as a star map; also used for the history animation (`--animate`)

## Features

- **Nine Art Styles**: Each drawn from the repository's folders, files, languages and history
- **Language Colours**: Every file is coloured by its language
- **100% Deterministic**: Same repository state always generates identical artwork
- **Smart Aspect Ratios**: Auto-detects canvas shape based on project type (mobile/web/backend)
- **Flexible Canvas Sizes**: From 800px to 2400px+ with multiple aspect ratios
- **Smart Filenames**: Auto-generated with repo name, dimensions, style, timestamp, and commit hash
- **CLI and Web Interface**: Use standalone Python script or full-featured Flask web application

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Python CLI (Simple & Fast)

Just want to generate art directly? Use the Python script!

#### Basic Usage

Generate art from current repository with auto-generated filename:
```bash
python git2art.py
```

#### Art Style Selection

```bash
# List all available art styles
python git2art.py --list-styles

# Generate with specific style
python git2art.py --style expressionist  # Gestural painting (default)
python git2art.py --style impressionist  # Swirling brushstrokes
python git2art.py --style watercolor     # Layered glazes
python git2art.py --style psychedelic    # Op-art spirals
python git2art.py --style pixel_city     # Isometric 8-bit city
python git2art.py --style de_stijl       # Mondrian-style map of the code
python git2art.py --style garden         # Botanical plate
python git2art.py --style tapestry       # History woven as cloth
python git2art.py --style constellation  # Star map of the folder tree
```

#### History Animation

Render the whole history of a repository as a video in the constellation style.
Files are born, grow, glide when renamed, flare when touched and fade when
deleted; a caption shows the date, commit, file, line and author counts.

```bash
python git2art.py --animate                          # this repo, 1920x1080 MP4
python git2art.py --animate --repo /path/to/repo --size 1280
python git2art.py --animate --duration 20 --fps 30   # length excludes a 3 s final hold
python git2art.py --animate --pace time              # follow calendar time, not commit count
python git2art.py --animate --output history.gif     # GIF instead of MP4 (much larger files)
python git2art.py --animate --no-caption
```

MP4 output needs `ffmpeg` on the PATH. The default length scales with the
number of commits (12 to 40 seconds). Only first-parent history is replayed,
so merged branches appear as the merge commit. Rendering takes about 50 ms per
frame at 1280x720.

#### Common Options

```bash
# Specific aspect ratio (auto-detects by default)
python git2art.py --aspect 16:9 --size 1920

# Portrait for mobile apps
python git2art.py --aspect portrait_3:4

# Landscape for web projects
python git2art.py --aspect 16:9

# Square for backend/libraries (default when auto-detect can't determine)
python git2art.py --aspect square
```

Available aspect ratios: `auto` (recommended), `square`, `4:3`, `16:10`, `16:9`, `3:2`, `5:4`, `portrait_3:4`, `portrait_2:3`

**Aspect Ratio Auto-Detection:**
- **Portrait (3:4)**: Mobile apps - Swift/Kotlin/Dart files >15% of codebase
- **Landscape (16:9)**: Web frontends - HTML/CSS/JS files >25% OR documentation >40%
- **Square (1:1)**: Backend, libraries, general purpose (default fallback)

#### Size

```bash
# Higher resolution (default: 1600px)
python git2art.py --size 2400
```

#### Generate from Specific Repository

```bash
python git2art.py --repo /path/to/any/git/repo
```

#### Combine Options

```bash
python git2art.py --repo /path/to/repo --style garden --aspect 16:9 --size 1920 --output my_art.png
```

#### Smart Filenames

When you don't specify `--output`, Git2Art automatically generates descriptive filenames:
```
Git2Art_1600x1600_expressionist_20251107_143022_aa7f55a.png
         ↓            ↓              ↓          ↓
    dimensions    art style      timestamp  commit hash
```

### Option 2: Flask Web Application (Full Featured)

Want a complete web interface with gallery and sharing? Use Flask!

#### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (copy and customize)
cp .env.example .env

# Run the web app
python app.py
```

Then open http://localhost:5001 in your browser.

#### Web Features

**Generate Artwork**
- GitHub URL input with validation (HTTPS and git@ formats supported)
- Automatic repository cloning and analysis
- Smart caching (avoids regeneration for unchanged repos)
- Download button for generated artwork

**Gallery & Discovery**
- Browse all generated artworks in a beautiful grid layout
- View artwork details and repository information
- Like/unlike artworks (persistent with database)
- Sort by creation date or popularity
- Responsive design for mobile and desktop

**Museum** (`/museum`, works on any device)
- The collection hung room by room: Entrance Hall (new acquisitions), Painting Galleries (one room per style), Sculpture Court, Light Installations, Most Loved
- Walk along each wall with the arrow keys, Enter to look closer, M for the floor plan; swipe on phones
- Server-rendered HTML, so it works without JavaScript and is indexable
- Repository sculptures are drawn on a 2D canvas and replay their history when focused

**3D Museum** (`/gallery3d`)
- An endless, walkable museum: every room has 5 to 10 works and a door in each wall; new rooms are generated as you walk
- Eight room moods (White Cube, Salon, Nocturne, Verdigris, Sandstone, Graphite, Blush, Ultraviolet) with different sizes, ceilings, floors, frames, benches and sculptures; adjacent rooms never share a mood
- Track spotlights with volumetric beams, wall halos, neon accents, bloom and drifting dust
- Light Installations (east of the entrance): dark rooms where a repository's commit history rises as a walk-through spiral of light, with a time pulse travelling through it and the file tree hanging above as a chandelier
- Sculpture Court (south of the entrance): each repository as a 3D sculpture of glowing file beads on bronze folder branches, replaying its history while you are in the room
- Desktop: arrow keys walk and turn, A/D step sideways, mouse look optional, Enter or click for details. Touch: left thumb walks, right thumb looks, tap a work
- Suggests the 2D museum if the device renders below about 30 fps
- `?seed=N` reproduces a museum layout; the intro screen links to the current one
- Uses web-sized WebP copies in `static/generated/museum/`; create them for existing artworks with `python scripts/make_museum_images.py` (new artworks get one automatically)
- Sculptures need per-repository data in `static/generated/repodata/`: create it for existing repositories with `python scripts/make_repo_data.py` (clones each repository, reads the database only); new artworks get it automatically
- The Artists: every work names its repository owner (portrait from GitHub), the number of contributors and the star count, with a star button. Each owner has a room in both museums; in 3D, "Teleport to the artist's room" from any painting, or open `/gallery3d?artist=<owner>`
- Star counts are cached in `static/generated/repodata/github.json`: new artworks fetch their own; refresh the rest with `python scripts/refresh_github_info.py` (40 per run without a token; set `GITHUB_TOKEN` in `.env` for more)

**Database Integration**
- MariaDB backend for persistent storage
- Like count tracking and user sessions
- Artwork metadata management
- Graceful fallback if database unavailable

**User Experience**
- Beautiful, modern responsive UI
- Real-time generation status updates
- Error handling and user feedback
- Mobile-friendly design

## How It Works

1. **Reads the repository**: every tracked file at HEAD with its size, the commit in which it first appeared and how often it has changed, plus languages and a commit timeline (`scene/repodata.py`). A blobless clone is enough.
2. **Groups the code**: folders become districts, plants, washes, warp bands or spiral centres depending on the style.
3. **Places things stably**: positions and angles come from hashes of file paths, so adding or editing a file changes only its own part of the picture.
4. **Colours by language**: each language has its own colour (Python blue, JavaScript yellow, TypeScript light blue and so on).
5. **Chooses the canvas shape**: mobile projects portrait, web and documentation-heavy projects landscape, others square (override with `--aspect`).

Artworks on the site are stored as WebP (lossless for flat-colour styles such as Pixel City); downloads are converted to PNG. `scripts/cleanup_artworks.py` removes orphaned files and, on request, superseded or retired artworks.

Styles live in `styles/` and render from the repository data alone, so the whole collection can be re-rendered without cloning (`scripts/render_data_style.py`). Use `scripts/style_lab.py <style>` to see a style on eight contrasting repositories.

## Project Documentation

See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for complete documentation including:
- Development journey and design decisions
- Flask web application architecture
- Database schema and API documentation
- Deployment guides

Research and development docs are in the [/research](research/) folder.

## Future Possibilities

- More art style variations (minimalist, geometric, etc.)
- SVG and vector export options
- VR/AR gallery experiences
- User accounts and authentication
- Social sharing and community features
- Comparison visualizations for multiple repositories

## Contributing

Contributions welcome! Please check the issues page or submit pull requests.

## License

MIT License - see LICENSE file for details

---

Generated with Claude Code - Transform your code into art

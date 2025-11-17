# Git2Art

Turn your git repository into a beautiful piece of abstract art!

[![GitHub](https://img.shields.io/badge/github-RobertSvebeck%2FGit2Art-blue)](https://github.com/RobertSvebeck/Git2Art)

## Concept

Git2Art creates deterministic abstract art from your codebase:
- **Small changes** in code = **small changes** in the artwork
- **Big changes** in many files = **big changes** in the artwork
- Same code always generates the same art (byte-for-byte identical)

## Art Styles

Git2Art offers seven distinct art styles to visualize your code:

- **Expressionist** - Bold strokes, vibrant colors, organic shapes inspired by abstract expressionism (default)
- **Impressionist** - Soft brush dabs, pastel colors, luminous atmosphere inspired by Monet and Renoir
- **Watercolor** - Transparent washes, flowing blends, soft edges with watercolor painting techniques
- **Pixel** - Retro 8-bit aesthetic with blocky shapes and limited color palette
- **Face** - Cubist face art inspired by Picasso and Matisse with playful abstract features
- **Nature** - Organic textures inspired by natural forms with earth-toned backgrounds
- **Psychedelic** - Hypnotic trippy flows with NO straight lines, vibrant neon colors, spirals and mandala patterns

## Features

- **Multiple Art Styles**: Seven unique styles, each with distinct visual characteristics
- **Repository-Driven Palettes**: Colors automatically selected based on primary programming language
- **100% Deterministic**: Same repository state always generates identical artwork
- **Smart Aspect Ratios**: Auto-detects canvas shape based on project type (mobile/web/backend)
- **Flexible Canvas Sizes**: From 800px to 2400px+ with multiple aspect ratios
- **Professional Composition**: Uses golden ratio, rule of thirds, and visual hierarchy principles
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
python git2art.py --style expressionist  # Bold abstract (default)
python git2art.py --style impressionist  # Soft pastel brushwork
python git2art.py --style watercolor     # Flowing transparent washes
python git2art.py --style pixel          # Retro 8-bit aesthetic
python git2art.py --style face           # Cubist face art
python git2art.py --style nature         # Organic natural textures
python git2art.py --style psychedelic    # Hypnotic trippy flows
```

**Face Style Details:**
The face style creates abstract cubist faces inspired by Picasso and Matisse. Features are positioned and styled using deterministic randomness based on repository metrics:
- **Eye size**: Based on file count (more files = larger eyes)
- **Eye shapes**: Randomly selected from 5 styles (circular, almond, organic blob, square, crescent)
- **Nose size**: Based on commit count (more commits = larger nose)
- **Nose shapes**: Randomly selected from 5 styles (triangle, rectangle, L-shaped, blob, hook)
- **Mouth width**: Based on author count (more authors = wider mouth)
- **Mouth expression**: Happiness increases with collaboration (more authors = bigger smile)
- **Hair style**: Randomly selected from 5 styles (circular tufts, spiky triangles, organic blobs, wavy lines, rectangular blocks)
- **Face planes**: Bold color blocks in cubist style with asymmetric positioning
- **Background**: Organic flowing shapes with palette-based colors

**Psychedelic Style Details:**
The psychedelic style creates hypnotic, trippy artwork with zero straight lines and vibrant neon colors:
- **NO straight lines**: Every element uses curves - wavy lines, spirals, and organic flows
- **Vibrant colors**: Neon magentas, electric blues, acid yellows, vivid purples with high saturation
- **Flowing background**: Multi-layered wavy lines with sine wave amplitude modulation
- **Spiral vortices**: Hypnotic rotating spirals that draw the eye inward
- **Concentric waves**: Circular patterns with wavy distortion creating ripple effects
- **Flowing blobs**: Organic shapes with smooth, wavy edges
- **Mandala patterns**: Radiating geometric curves with petal-like structures
- **Undulating waves**: Complex layered sine waves for infinite visual movement
- **Dark background**: Deep purple/black base to make colors pop with psychedelic intensity

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

#### Adjust Contrast & Size

```bash
# Low contrast (subtle, muted tones)
python git2art.py --contrast low

# Medium contrast (balanced)
python git2art.py --contrast medium

# High contrast (dramatic, default)
python git2art.py --contrast high

# Higher resolution (default: 1600px)
python git2art.py --size 2400
```

#### Generate from Specific Repository

```bash
python git2art.py --repo /path/to/any/git/repo
```

#### Combine Options

```bash
python git2art.py --repo /path/to/repo --style face --aspect 16:9 --size 1920 --contrast medium --output my_art.png
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

**3D Gallery Experience**
- Immersive THREE.js-based 3D gallery
- Nature-themed environments (forest, desert, ocean, arctic, sunset, midnight)
- Artworks displayed on floating panels with realistic lighting
- Interactive navigation with mouse/touch controls
- Animated camera tours and environment transitions
- Realistic materials with bump maps and reflections

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

1. **Analyzes Your Repository**:
   - Scans all tracked files in git
   - Counts lines of code per file
   - Hashes file content for deterministic seeding
   - Maps file types and relationships
   - Extracts commit count and author list

2. **Selects Color Palette**:
   - Detects primary programming language from file extensions
   - Selects harmonious color scheme (Python=blues, JavaScript=yellows, etc.)
   - Creates expanded palette with tints, shades, and tones

3. **Determines Canvas Shape**:
   - Analyzes file type distribution
   - Auto-detects aspect ratio (mobile=portrait, web=landscape, backend=square)
   - Can be manually overridden with `--aspect` flag

4. **Generates Artwork** (style-specific):
   - **Expressionist**: Bold strokes, thick lines, filled color areas, organic shapes
   - **Impressionist**: Small brush dabs, soft edges, layered transparency
   - **Watercolor**: Transparent washes, color bleeding, soft gradients
   - **Pixel**: Blocky shapes, limited palette, retro 8-bit aesthetic
   - **Face**: Cubist face with planes, varied eye/nose/mouth shapes, asymmetric features
   - **Nature**: Earth-toned background with organic elements, natural textures
   - **Psychedelic**: Hypnotic curves, zero straight lines, vibrant neon colors, spirals and mandalas

5. **Ensures Determinism**:
   - All randomness seeded from repository metrics
   - Same repository state = identical artwork (byte-for-byte)
   - Small code changes = small visual changes
   - Large code changes = large visual changes

## Technical Details

### Color System
- **Language-Based Palettes**: 7 curated palettes (Python, JavaScript, Java, Ruby, Go, Rust, default)
- **Auto-Detection**: Analyzes file extension distribution to select palette
- **Expansion**: Each palette expanded with tints, shades, and complementary colors

### Aspect Ratio Detection
- **Mobile Detection**: Swift, Kotlin, Dart, Objective-C files
- **Web Detection**: HTML, CSS, JS, JSX, TS, TSX, Vue, Svelte files
- **Documentation Detection**: Markdown, RST, text files
- **Thresholds**: Mobile >15%, Web >25%, Docs >40%

### Deterministic System
- All "random" values derived from MD5 hashes of repository data
- `total_lines` → main seed for global decisions
- File content hashes → element-specific seeds
- Deterministic random class ensures reproducibility across runs

### Art Theory Principles
- **Golden Ratio (φ)**: Element positioning at natural focal points
- **Rule of Thirds**: Dynamic composition with key elements at intersections
- **Visual Hierarchy**: File importance mapped to size, opacity, and placement
- **Color Harmony**: Complementary, analogous, and triadic color schemes

## Project Documentation

See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for complete documentation including:
- Development journey and design decisions
- Flask web application architecture
- Database schema and API documentation
- Deployment guides

Research and development docs are in the [/research](research/) folder.

## Examples

Generate different styles from the same repository:

```bash
# Bold expressionist (default)
python git2art.py --style expressionist

# Soft impressionist
python git2art.py --style impressionist

# Flowing watercolor
python git2art.py --style watercolor

# Retro pixel art
python git2art.py --style pixel

# Abstract cubist face
python git2art.py --style face

# Natural organic textures
python git2art.py --style nature

# Hypnotic psychedelic (trippy!)
python git2art.py --style psychedelic
```

Each style will produce completely different artwork from the same codebase while maintaining determinism.

## Future Possibilities

- Animation showing repository evolution over time
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

# Git2Art

Turn your git repository into a beautiful piece of abstract art!

[![GitHub](https://img.shields.io/badge/github-RobertSvebeck%2FGit2Art-blue)](https://github.com/RobertSvebeck/Git2Art)

## Concept

Git2Art creates deterministic abstract art from your codebase:
- **Small changes** in code = **small changes** in the artwork
- **Big changes** in many files = **big changes** in the artwork
- Same code always generates the same art

## Art Styles

Git2Art offers multiple art styles to visualize your code:

- **🎨 Expressionist** - Bold strokes, vibrant colors, organic shapes (default)
- **🌸 Impressionist** - Soft brush dabs, pastel colors, luminous atmosphere
- **💧 Watercolor** - Transparent washes, flowing blends, soft edges
- **🎮 Pixel** - Retro 8-bit aesthetic, blocky shapes, limited palette
- **👤 Face** - Human face where features are built from code metrics

## Features

- 🎨 **Advanced Color Theory**: Complementary, triadic, split-complementary, and tetradic color schemes
- 🎭 **Adjustable Contrast**: Choose low, medium, or high contrast levels for different aesthetics
- 🌈 **Sophisticated Color Mixing**: Elements blend 2-4 colors with deterministic ratios
- 🔀 **Analogous & Complementary Variations**: Each element uses subtle color shifts or bold complementary accents
- 📐 **Professional Composition**: Golden ratio, rule of thirds, Fibonacci spirals
- 📊 **Visual Hierarchy**: File importance mapped to size and opacity
- 🌊 **Organic Flow**: IDEO-inspired Cornu curves and bold strokes (up to 30% canvas width)
- 🔄 **100% Deterministic**: Same code always generates identical art (byte-for-byte)
- 🖼️ **Flexible Canvas**: Multiple aspect ratios (4:3, 16:10, 16:9, 3:2, portrait modes)
- 📝 **Smart Naming**: Auto-generated filenames with repo name, dimensions, and commit hash

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Python CLI (Simple & Fast) ⚡

Just want to generate art directly? Use the Python script!

#### Basic Usage

Generate art from current repository (auto-named file):
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
python git2art.py --style face           # Human face from code metrics
```

**Face Style Details:**
The face style creates a unique human face where each feature is determined by repository metrics:
- **Face shape**: Repository size (round → oval → angular)
- **Eyes**: File count and type distribution
- **Nose**: Commit count
- **Mouth**: Author count (more authors = bigger smile!)
- **Hair**: Primary language (curly for Python/Ruby, spiky for JS/TS, etc.)

#### Common Options

```bash
# Specific aspect ratio (auto-detects by default)
python git2art.py --aspect 16:9 --size 1920

# Portrait for mobile apps
python git2art.py --aspect portrait_3:4

# Landscape for web projects
python git2art.py --aspect 16:9

# Square for backend/libraries (default)
python git2art.py --aspect square
```

Available aspect ratios: `auto` (recommended), `square`, `4:3`, `16:10`, `16:9`, `3:2`, `5:4`, `portrait_3:4`, `portrait_2:3`

#### Adjust Contrast & Size

```bash
# Low contrast (subtle, muted tones)
python git2art.py --contrast low

# High contrast (dramatic, default)
python git2art.py --contrast high

# Higher resolution (default: 1200px)
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
Git2Art_1600x1200_20251019_143022_aa7f55a.png
         ↓        ↓          ↓          ↓
    repo name  size    timestamp  commit hash
```

### Option 2: Flask Web Application (Full Featured) 🌐

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

Then open http://localhost:5000 in your browser.

#### Web Features

✅ **Generate Artwork**
- GitHub URL input with validation
- Automatic repository analysis and artwork generation
- Smart caching (avoids regeneration for unchanged repos)
- Watermark with repository URL
- Download button for generated artwork

✅ **Gallery & Discovery**
- Browse all generated artworks in a beautiful grid
- View artwork details and repository information
- Like/unlike artworks (persistent with database)
- Sort by creation date or popularity
- Responsive design for mobile and desktop

✅ **Database Integration**
- MariaDB backend for persistent storage
- Like count tracking and user sessions
- Artwork metadata management
- Graceful fallback if database unavailable

✅ **User Experience**
- Beautiful, modern responsive UI
- Real-time generation status updates
- Error handling and user feedback
- Mobile-friendly design

## How It Works

1. **Analyzes** your repository:
   - Scans all tracked files
   - Counts lines of code
   - Hashes file content for determinism
   - Maps file types and relationships

2. **Applies Art Theory**:
   - **Advanced Color Theory**: Complementary, triadic, split-complementary, and tetradic schemes
   - **Adjustable Contrast**: Low (1.15x/0.7x), Medium (1.25x/0.55x), or High (1.4x/0.4x) brightness ratios
   - **Sophisticated Mixing**: Each element blends 2-4 colors with deterministic weighted ratios
   - **Color Variations**: Analogous shifts (subtle) or complementary accents (bold) per element
   - **Composition**: Places elements using golden ratio and rule of thirds
   - **Visual Hierarchy**: Sizes elements by code importance
   - **Bold Strokes**: IDEO-inspired thick strokes up to 30% of canvas width
   - **Flow**: Connects elements with Cornu curves and organic Bézier paths

3. **Generates Beautiful Art**:
   - Multi-center gradient background
   - Shape variation by file type (circles, hexagons, triangles)
   - Depth and texture with subtle blur
   - High-quality PNG output

See [CLAUDE.md](CLAUDE.md) for detailed development journey and technical architecture.

## For Developers

See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for complete documentation.

Research and development docs are in the [/research](research/) folder.

## Future Possibilities

- Animation showing repository evolution over time
- More art style variations and presets
- SVG and high-resolution export options
- Interactive parameter tweaking
- User accounts and authentication

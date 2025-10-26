# Git2Art

Turn your git repository into a beautiful piece of abstract art!

[![GitHub](https://img.shields.io/badge/github-RobertSvebeck%2FGit2Art-blue)](https://github.com/RobertSvebeck/Git2Art)

## Concept

Git2Art creates deterministic abstract art from your codebase:
- **Small changes** in code = **small changes** in the artwork
- **Big changes** in many files = **big changes** in the artwork
- Same code always generates the same art

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

### Basic Usage

Generate art from current repository (auto-named file with 4:3 aspect ratio):
```bash
python git2art.py
```

### Advanced Options

Generate art with specific aspect ratio:
```bash
# Landscape 16:10 (great for wallpapers)
python git2art.py --aspect 16:10 --size 1920

# Portrait 2:3
python git2art.py --aspect portrait_2:3 --size 1200

# Wide 16:9 (HD format)
python git2art.py --aspect 16:9 --size 1920
```

Available aspect ratios: `square`, `4:3`, `16:10`, `16:9`, `3:2`, `5:4`, `portrait_3:4`, `portrait_2:3`

Adjust contrast level:
```bash
# Low contrast (subtle, muted tones)
python git2art.py --contrast low

# Medium contrast (balanced)
python git2art.py --contrast medium

# High contrast (dramatic, default)
python git2art.py --contrast high
```

Generate art with custom filename:
```bash
python git2art.py --output my_artwork.png
```

Generate from a specific repository:
```bash
python git2art.py --repo /path/to/repo --size 2400
```

Combine multiple options:
```bash
python git2art.py --repo /path/to/repo --aspect 16:10 --size 1920 --contrast medium --output my_art.png
```

### Smart Filenames

When you don't specify `--output`, Git2Art automatically generates descriptive filenames:
```
Git2Art_1600x1200_20251019_143022_aa7f55a.png
         ↓        ↓          ↓          ↓
    repo name  size    timestamp  commit hash
```

The timestamp ensures uniqueness even when generating multiple artworks from repos with the same name.

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

## Web Application 🌐

Git2Art includes a full-featured Flask web application for generating and sharing artwork!

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment (copy and customize)
cp .env.example .env

# Run the web app
python app.py
```

Then open http://localhost:5000 in your browser.

### Web Features

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

## For Developers

See [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for complete documentation.

Research and development docs are in the [/research](research/) folder.

## Future Possibilities

- Animation showing repository evolution over time
- More art style variations and presets
- SVG and high-resolution export options
- Interactive parameter tweaking
- User accounts and authentication

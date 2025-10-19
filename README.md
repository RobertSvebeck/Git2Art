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
- 📐 **Professional Composition**: Golden ratio, rule of thirds, Fibonacci spirals
- 🎭 **High Contrast**: Rich darks and bright lights for visual impact
- 📊 **Visual Hierarchy**: File importance mapped to size and opacity
- 🌊 **Organic Flow**: IDEO-inspired Cornu curves and bold strokes (up to 30% canvas width)
- 🔄 **100% Deterministic**: Same code always generates identical art
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

Generate art with custom filename:
```bash
python git2art.py --output my_artwork.png
```

Generate from a specific repository:
```bash
python git2art.py --repo /path/to/repo --size 2400
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
   - **High Contrast**: Very light tints (1.4x brightness) and very dark shades (0.4x brightness)
   - **Composition**: Places elements using golden ratio and rule of thirds
   - **Visual Hierarchy**: Sizes elements by code importance
   - **Bold Strokes**: IDEO-inspired thick strokes up to 30% of canvas width
   - **Flow**: Connects elements with Cornu curves and organic Bézier paths

3. **Generates Beautiful Art**:
   - Multi-center gradient background
   - Shape variation by file type (circles, hexagons, triangles)
   - Depth and texture with subtle blur
   - High-quality PNG output

See [ART_THEORY.md](ART_THEORY.md) for detailed explanation of principles used.

## Coming Soon

- Flask web app for easy visualization
- More art styles and algorithms
- Animation showing repository evolution over time
- Gallery of repository artworks

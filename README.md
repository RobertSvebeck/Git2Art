# Git2Art

Turn your git repository into a beautiful piece of abstract art!

[![GitHub](https://img.shields.io/badge/github-RobertSvebeck%2FGit2Art-blue)](https://github.com/RobertSvebeck/Git2Art)

## Concept

Git2Art creates deterministic abstract art from your codebase:
- **Small changes** in code = **small changes** in the artwork
- **Big changes** in many files = **big changes** in the artwork
- Same code always generates the same art

## Features

- 🎨 **Art Theory-Based**: Uses color harmony (complementary, triadic, analogous)
- 📐 **Professional Composition**: Golden ratio, rule of thirds, Fibonacci spirals
- 📊 **Visual Hierarchy**: File importance mapped to size and opacity
- 🎭 **Semantic Shapes**: Different shapes for different file types
- 🌊 **Flow & Unity**: Connecting curves and harmonious gradients
- 🔄 **100% Deterministic**: Same code always generates identical art
- 🖼️ **High Resolution**: Default 1200x1200, customizable size

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Generate art from current repository:
```bash
python git2art.py
```

Generate art from a specific repository:
```bash
python git2art.py --repo /path/to/repo --output my_art.png --size 2400
```

## How It Works

1. **Analyzes** your repository:
   - Scans all tracked files
   - Counts lines of code
   - Hashes file content for determinism
   - Maps file types and relationships

2. **Applies Art Theory**:
   - **Color Harmony**: Selects complementary, triadic, or analogous palette
   - **Composition**: Places elements using golden ratio and rule of thirds
   - **Visual Hierarchy**: Sizes elements by code importance
   - **Flow**: Connects elements with subtle Bézier curves

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

# Git2Art

Turn your git repository into a beautiful piece of abstract art!

## Concept

Git2Art creates deterministic abstract art from your codebase:
- **Small changes** in code = **small changes** in the artwork
- **Big changes** in many files = **big changes** in the artwork
- Same code always generates the same art

## Features

- Analyzes file types, line counts, and code structure
- Visualizes commit history as spiraling patterns
- Maps code complexity to colors and shapes
- Generates high-resolution abstract art (default 1200x1200)

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

1. **Fingerprints** the repository by analyzing all tracked files
2. **Maps** code metrics to visual parameters:
   - File content → Colors (via hash)
   - Line count → Size of elements
   - File type → Shape (circle, square, triangle)
   - Commit history → Spiral pattern
3. **Generates** deterministic abstract art based on the fingerprint

## Coming Soon

- Flask web app for easy visualization
- More art styles and algorithms
- Animation showing repository evolution over time

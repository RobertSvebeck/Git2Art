# Developing New Art Styles for Git2Art

This guide explains how to create new art styles for the Git2Art modular generator system.

## Architecture Overview

Git2Art uses a modular architecture where each art style is a separate generator class:

```
generators/
├── __init__.py          # Public API exports
├── base.py              # BaseArtGenerator (common functionality)
├── default_style.py     # Default style (bold expressionist)
├── your_new_style.py    # Your new style goes here
└── registry.py          # Style factory and registry
```

## Quick Start: Creating a New Style

### 1. Create Your Style File

Create a new file in `generators/` directory, e.g., `minimalist_style.py`:

```python
"""Minimalist art style - clean lines and simple shapes."""

from .base import BaseArtGenerator
from PIL import Image, ImageDraw
import random


class MinimalistStyleGenerator(BaseArtGenerator):
    """Minimalist style with clean geometric shapes."""

    # Required class attributes
    STYLE_NAME = "minimalist"
    STYLE_DESCRIPTION = "Clean, minimal design with simple geometric shapes and limited colors"

    def __init__(self, repo_path='.', width=1600, height=1200, aspect_ratio='auto', **kwargs):
        """Initialize minimalist generator.

        Args:
            repo_path: Path to git repository
            width: Canvas width
            height: Canvas height
            aspect_ratio: Aspect ratio ('auto', 'square', '16:9', etc.)
            **kwargs: Additional style-specific parameters
        """
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)

        # Add any style-specific initialization here
        self.max_shapes = kwargs.get('max_shapes', 10)

    def generate_art(self, output_path='repo_art.png'):
        """Generate minimalist artwork.

        This is the main method you must implement.
        """
        # Get repository data
        fingerprint = self.get_repo_fingerprint()

        # Create canvas
        img = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(img, 'RGBA')

        # Your art generation logic here
        self._draw_minimalist_shapes(draw, fingerprint)

        # Save image
        img.save(output_path, quality=95)

        # Print generation info
        print(f"Art generated: {output_path}")
        print(f"Style: {self.STYLE_NAME}")
        print(f"Aspect ratio: {self.aspect_ratio} ({self.width}x{self.height})")
        print(f"{len(fingerprint['files'])} files processed")

        return output_path

    def _draw_minimalist_shapes(self, draw, fingerprint):
        """Draw simple geometric shapes based on repository data."""
        # Example: Draw rectangles for each file
        files = sorted(fingerprint['files'].items(),
                      key=lambda x: x[1]['lines'],
                      reverse=True)

        for idx, (file_path, file_data) in enumerate(files[:self.max_shapes]):
            # Use file hash for deterministic positioning
            file_hash = int(file_data['hash'][:8], 16)
            random.seed(file_hash)

            # Simple rectangle
            x = random.randint(0, self.width - 200)
            y = random.randint(0, self.height - 200)
            size = 50 + (file_data['lines'] % 150)

            draw.rectangle(
                [x, y, x + size, y + size],
                fill=(100, 100, 100),
                outline=(0, 0, 0),
                width=2
            )
```

### 2. Register Your Style

Edit `generators/registry.py` and add your style to the registry:

```python
from .default_style import DefaultStyleGenerator
from .minimalist_style import MinimalistStyleGenerator  # Import your style

STYLE_REGISTRY = {
    'default': DefaultStyleGenerator,
    'minimalist': MinimalistStyleGenerator,  # Register your style
}
```

### 3. Test Your Style

```bash
# Test from command line
python git2art.py --style minimalist --repo /path/to/repo

# List all available styles
python git2art.py --list-styles
```

## BaseArtGenerator Reference

Your style inherits from `BaseArtGenerator` which provides:

### Available Methods

```python
# Repository data
fingerprint = self.get_repo_fingerprint()
# Returns: {
#     'files': {path: {'lines': int, 'hash': str, 'extension': str}},
#     'total_lines': int,
#     'file_types': {'.py': line_count, ...},
#     'commit_count': int,
#     'authors': set()
# }

# Aspect ratio detection
aspect = self.detect_aspect_ratio(fingerprint)
# Returns: 'square', '16:9', 'portrait_3:4', etc.

# File filtering (already applied)
should_skip = self._should_skip_file(file_path)
```

### Available Properties

```python
self.repo           # GitPython Repo object
self.repo_path      # Path to repository
self.width          # Canvas width (pixels)
self.height         # Canvas height (pixels)
self.aspect_ratio   # Current aspect ratio name
self.ASPECT_RATIOS  # Dict of available ratios
```

### Class Attributes (Required)

```python
STYLE_NAME = "your_style"  # Short identifier
STYLE_DESCRIPTION = "Description shown in --list-styles"
```

## Deterministic Art Generation

**Important**: Git2Art generates deterministic art - same repository = same image.

### Best Practices for Determinism

1. **Use repository data for randomness:**
   ```python
   # Good - deterministic
   seed = fingerprint['total_lines']
   random.seed(seed)

   # Good - per-file determinism
   file_hash = int(file_data['hash'][:8], 16)
   random.seed(file_hash)
   ```

2. **Avoid time-based randomness:**
   ```python
   # Bad - not deterministic
   random.seed()  # Uses system time
   import time
   x = int(time.time())
   ```

3. **Use DeterministicRandom helper** (see default_style.py):
   ```python
   from generators.default_style import DeterministicRandom

   value = DeterministicRandom.uniform(hash_string, index, min_val, max_val)
   ```

## Style Design Guidelines

### 1. Use Repository Metrics Meaningfully

Map repository characteristics to visual elements:

```python
# File count → number of shapes
num_shapes = min(len(fingerprint['files']), 50)

# Lines of code → size
size = int(file_data['lines'] / 10)

# File type → color or shape
if file_data['extension'] == '.py':
    color = (52, 152, 219)  # Blue
elif file_data['extension'] == '.js':
    color = (241, 196, 15)  # Yellow

# Commit count → complexity
layers = fingerprint['commit_count'] % 10
```

### 2. Respect Aspect Ratio

The base class handles aspect ratio, but consider it in your layout:

```python
# Center-based layout adapts automatically
center_x = self.width / 2
center_y = self.height / 2

# Grid layouts need adjustment
if self.aspect_ratio == 'portrait_3:4':
    cols = 3
    rows = 4
elif self.aspect_ratio == '16:9':
    cols = 4
    rows = 2
```

### 3. Performance Considerations

```python
# Good - O(n) where n is file count
for file_path, file_data in fingerprint['files'].items():
    draw_shape(file_data)

# Bad - O(width * height) can be slow
for x in range(self.width):
    for y in range(self.height):
        draw_pixel(x, y)

# Solution - use PIL efficiently
img = Image.new('RGB', (self.width, self.height))
# Batch operations are faster than pixel-by-pixel
```

## Advanced Examples

### Example 1: Color Palette from Repository

```python
from generators.default_style import RepositoryPalette

def generate_art(self, output_path='repo_art.png'):
    fingerprint = self.get_repo_fingerprint()

    # Use built-in palette selector
    palette_name, palette_dict = RepositoryPalette.select_palette_by_repo(fingerprint)
    colors = palette_dict['base']  # List of RGB tuples

    # Now use these harmonious colors in your art
    for idx, color in enumerate(colors):
        # Draw something with this color
        pass
```

### Example 2: File Importance Hierarchy

```python
def generate_art(self, output_path='repo_art.png'):
    fingerprint = self.get_repo_fingerprint()

    # Sort files by importance (line count)
    files = sorted(
        fingerprint['files'].items(),
        key=lambda x: x[1]['lines'],
        reverse=True
    )

    # Draw larger/more prominent for important files
    for idx, (file_path, file_data) in enumerate(files):
        importance = 1.0 - (idx / len(files))  # 1.0 to 0.0
        size = int(100 * importance)
        opacity = int(255 * importance)

        # Draw with size and opacity reflecting importance
        draw.ellipse([x, y, x+size, y+size], fill=(255, 0, 0, opacity))
```

### Example 3: Style-Specific Parameters

```python
class WatercolorStyleGenerator(BaseArtGenerator):
    STYLE_NAME = "watercolor"
    STYLE_DESCRIPTION = "Soft, flowing watercolor effect"

    def __init__(self, repo_path='.', width=1600, height=1200,
                 aspect_ratio='auto', transparency=0.5, blur_radius=5, **kwargs):
        super().__init__(repo_path, width, height, aspect_ratio, **kwargs)

        # Style-specific parameters
        self.transparency = transparency
        self.blur_radius = blur_radius

    def generate_art(self, output_path='repo_art.png'):
        # Use self.transparency and self.blur_radius
        pass
```

## Testing Your Style

### Manual Testing

```bash
# Test on current repository
python git2art.py --style your_style

# Test on specific repository
python git2art.py --style your_style --repo /path/to/repo

# Test different sizes
python git2art.py --style your_style --size 800
python git2art.py --style your_style --size 2400

# Test different aspect ratios
python git2art.py --style your_style --aspect square
python git2art.py --style your_style --aspect 16:9
python git2art.py --style your_style --aspect portrait_3:4
```

### Verify Determinism

```bash
# Generate twice with same repo
python git2art.py --style your_style --repo /path/to/repo --output test1.png
python git2art.py --style your_style --repo /path/to/repo --output test2.png

# Files should be identical
diff test1.png test2.png
# No output = identical ✓
```

### Test on Different Repository Types

```bash
# Small repo
python git2art.py --style your_style --repo small-project

# Large repo
python git2art.py --style your_style --repo large-project

# Different languages
python git2art.py --style your_style --repo python-project
python git2art.py --style your_style --repo javascript-project
```

## Integration with Web Application

Once your style is registered, it's automatically available in:

1. **CLI**: `python git2art.py --style your_style`
2. **Web API**: Pass `art_style='your_style'` to `generate_art_from_github()`
3. **Database**: Stored with `art_style` field

### Adding to Web UI (Future)

When you add style selection to the web interface:

```python
from generators import list_available_styles

# In your Flask route
@app.route('/generate', methods=['POST'])
def generate():
    style = request.form.get('style', 'default')

    # Generate with selected style
    result = generate_art_from_github(
        github_url=repo_url,
        temp_dir=temp_dir,
        images_dir=images_dir,
        art_style=style
    )
```

## Style Ideas

Here are some style concepts to inspire you:

### Minimalist
- Clean geometric shapes
- Limited color palette (2-3 colors)
- Lots of whitespace
- Sharp edges and straight lines

### Geometric
- Tessellations and patterns
- Voronoi diagrams
- Triangulation
- Sacred geometry

### Watercolor
- Soft edges with blur
- Transparent overlapping shapes
- Color bleeding effects
- Organic, flowing forms

### Pixel Art
- Blocky, retro aesthetic
- Limited color palette
- Grid-based layout
- 8-bit/16-bit style

### Abstract Expressionist (Default)
- Bold, thick strokes
- Organic shapes
- Multiple layers
- Rich textures

### Tech/Circuit
- Circuit board patterns
- Connected nodes
- Technical diagrams
- Futuristic aesthetic

### Nature/Organic
- Tree-like branching
- Fractal patterns
- Growth algorithms
- Natural color palettes

### Data Visualization
- Charts and graphs
- Network diagrams
- Statistical representations
- Information design

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you're running from the project root
cd /path/to/Git2Art
python git2art.py --style your_style
```

### Style not appearing in `--list-styles`
- Check that you registered it in `generators/registry.py`
- Verify the import statement is correct
- Make sure the class name matches the import

### Art looks different each time
- Review your randomness sources
- Ensure you're using repository data for seeding
- Check for time-based or system randomness

### Performance issues
- Reduce number of elements
- Use batch operations instead of loops
- Profile with `python -m cProfile git2art.py --style your_style`

## Resources

### Color Theory
- Adobe Color Wheel: https://color.adobe.com/
- Coolors Palette Generator: https://coolors.co/
- Material Design Colors: https://materialui.co/colors/

### PIL/Pillow Documentation
- ImageDraw: https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
- Image Filters: https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html

### Inspiration
- "Painting with Code" - IDEO: https://vimeo.com/57060656
- Processing Examples: https://processing.org/examples/
- Generative Art Subreddit: https://reddit.com/r/generative

## Example Styles in the Wild

Study the default style (`generators/default_style.py`) to see:
- Repository-driven color palettes
- Deterministic randomness patterns
- Layered composition techniques
- IDEO-inspired organic shapes
- Performance optimizations

## Questions?

Refer back to:
- `generators/base.py` - Base class implementation
- `generators/default_style.py` - Complete working example
- `generators/registry.py` - Registration system
- `CLAUDE.md` - Project development history

---

**Happy creating! 🎨**

*Remember: The best generative art tells a story about the code it represents.*

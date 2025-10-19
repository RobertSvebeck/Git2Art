# Git2Art - Recent Visual Improvements

## Overview
This document details the latest enhancements to Git2Art, focusing on advanced color theory, sophisticated mixing, and user-customizable contrast levels - all while maintaining 100% determinism.

## New Features

### 1. Adjustable Contrast Parameter (`--contrast`)

Users can now choose from three contrast levels to match different aesthetic preferences:

#### Low Contrast (Subtle)
- Tint multiplier: 1.15x brightness
- Shade multiplier: 0.7x brightness
- Saturation: Tints at 0.6x, Shades at 1.1x
- **Use case**: Muted, subtle artwork with gentle color transitions
- **Command**: `python git2art.py --contrast low`

#### Medium Contrast (Balanced)
- Tint multiplier: 1.25x brightness
- Shade multiplier: 0.55x brightness
- Saturation: Tints at 0.5x, Shades at 1.2x
- **Use case**: Balanced composition with moderate visual impact
- **Command**: `python git2art.py --contrast medium`

#### High Contrast (Dramatic) - Default
- Tint multiplier: 1.4x brightness
- Shade multiplier: 0.4x brightness
- Saturation: Tints at 0.3x, Shades at 1.3x
- **Use case**: Bold, dramatic artwork with maximum visual impact
- **Command**: `python git2art.py --contrast high`

### 2. Sophisticated Color Mixing (ColorMixer Class)

#### Deterministic Multi-Color Blending
New `ColorMixer.blend_colors()` method that:
- Blends 2-4 colors from the palette
- Uses deterministic weighted ratios based on file hash
- Ratios always sum to 1.0 for accurate color representation
- Applied to:
  - Filled color areas (3-7 huge organic shapes)
  - Bold color blocks (4-10 large rectangles)

**Example**: A shape might blend 3 colors with ratios [0.5, 0.3, 0.2]
- 50% of Color A (e.g., blue)
- 30% of Color B (e.g., teal)
- 20% of Color C (e.g., light blue)
- Result: Custom blended color unique to that element

#### Analogous Color Variations
New `ColorMixer.get_analogous_variation()` method that:
- Generates nearby colors on the color wheel (±18 degrees)
- Maintains visual cohesion
- Used for shadows and outer glows
- Creates harmonious color relationships

### 3. Analogous + Complementary Per-Element Variations

Each layered shape now uses advanced color theory:

#### Complementary Inner Layers (30% chance)
- Inner layers use the complementary color (opposite on color wheel)
- Creates visual "pop" and energy in the center
- Deterministically chosen based on file hash
- Example: Blue outer layers → Orange inner layers

#### Analogous Outer Variations (70% chance)
- Subtle hue shifts (±8 degrees) per layer
- Creates smooth, cohesive gradients
- More common for gentle, flowing aesthetics

#### Analogous Shadows
- Shadows use nearby colors on the color wheel
- Creates depth without harsh contrast
- More sophisticated than simple darkening

## Technical Implementation

### 100% Determinism Maintained
All new features use the `DeterministicRandom` class:
- `from_hash()`: Generate 0-1 value from hash + index
- `uniform()`: Deterministic floating point in range
- `randint()`: Deterministic integer in range
- `choice()`: Deterministic selection from list

**Verification**: Generated same repo twice, MD5 hashes matched perfectly:
```
MD5 (test_determinism_1.png) = 2f1fd7109033f3c60db47f43f5c0068d
MD5 (test_determinism_2.png) = 2f1fd7109033f3c60db47f43f5c0068d
```

### Color Mixing Ratios Algorithm

```python
def blend_colors(colors, seed_hash, count=2):
    # Select colors deterministically
    selected_colors = [colors[hash_based_index] for i in range(count)]

    # Generate deterministic ratios
    ratios = [random_from_hash(0.1, 1.0) for i in range(count)]

    # Normalize to sum to 1.0
    total = sum(ratios)
    ratios = [r / total for r in ratios]

    # Blend RGB values
    r = sum(color[0] * ratio for color, ratio in zip(selected_colors, ratios))
    # ... same for g, b
```

### Analogous Variation Algorithm

```python
def get_analogous_variation(color, seed_hash, shift_range=0.05):
    h, s, v = rgb_to_hsv(color)

    # Deterministic hue shift (±18 degrees)
    shift = random_from_hash(-shift_range, shift_range)
    new_h = (h + shift) % 1.0

    # Slight saturation/value variations
    new_s = s * random_from_hash(0.9, 1.1)
    new_v = v * random_from_hash(0.9, 1.1)

    return hsv_to_rgb(new_h, new_s, new_v)
```

## Usage Examples

### Basic Contrast Adjustment
```bash
# Generate with low contrast for subtle aesthetics
python git2art.py --contrast low --size 1600

# Generate with medium contrast for balance
python git2art.py --contrast medium --size 1600

# Generate with high contrast for drama (default)
python git2art.py --contrast high --size 1600
```

### Combined with Other Features
```bash
# Wide wallpaper with medium contrast
python git2art.py --aspect 16:10 --size 1920 --contrast medium

# Portrait mode with low contrast
python git2art.py --aspect portrait_2:3 --size 1200 --contrast low

# Custom output with all features
python git2art.py --repo /path/to/repo --aspect 4:3 --size 1600 --contrast high --output masterpiece.png
```

## Benefits

### For Users
- **Customization**: Choose contrast level to match personal taste
- **Consistency**: Same settings always produce identical output
- **Quality**: More sophisticated color relationships
- **Flexibility**: Three aesthetic options without randomness

### For Artists
- **Low Contrast**: Gentle, meditative pieces
- **Medium Contrast**: Balanced, versatile compositions
- **High Contrast**: Bold, gallery-worthy statements

### For Developers
- **Determinism**: Reproducible artwork for version control
- **Modularity**: ColorMixer class is reusable
- **Extensibility**: Easy to add new mixing strategies
- **Clean Code**: Separated concerns (mixing, theory, generation)

## Visual Impact

### Color Mixing Examples
1. **Filled Areas**: 3-7 large organic blobs, each blending 2-4 colors
2. **Bold Blocks**: 4-10 rectangles, each mixing 3-4 colors
3. **Result**: Rich, complex color palette in every composition

### Complementary Accents
- **Before**: All layers used analogous colors only
- **After**: 30% of shapes have complementary centers for visual excitement

### Analogous Shadows
- **Before**: Simple RGB darkening (darker = color - 50)
- **After**: Analogous variation + darkening for cohesive depth

## Performance

No significant performance impact:
- Color mixing: O(n) where n = blend count (2-4)
- Analogous variation: O(1) - single HSV conversion
- Total generation time: Still 2-15 seconds depending on repo size

## Future Enhancements

Potential additions based on this foundation:
- **Custom contrast values**: Allow precise tint/shade ratios
- **Color palette presets**: Save favorite contrast settings
- **Mix strategy selection**: Choose complementary vs. triadic blending
- **Interactive mode**: Adjust contrast and see real-time preview

## Conclusion

These improvements elevate Git2Art from "good color theory" to "sophisticated color mastery":
- ✅ User-customizable aesthetics (contrast parameter)
- ✅ Professional color relationships (mixing, analogous, complementary)
- ✅ Maintained 100% determinism (critical for git-based art)
- ✅ Enhanced visual quality without sacrificing performance

The art generated is now more nuanced, more customizable, and more professional - while remaining deterministic and reproducible.

---

**Generated**: 2025-10-19
**Version**: git2art.py v2.0 (with advanced color improvements)

# Art Styles Database System

This document explains how the art styles database system works and how to use it in the UX.

## Overview

The art styles system consists of:
1. **`art_styles` table** - Database table storing available art styles
2. **ArtStyle model** - Python model for database operations
3. **Registry integration** - Automatic sync with generator registry
4. **Management tools** - CLI utilities for managing styles

## Database Schema

### `art_styles` Table

```sql
CREATE TABLE art_styles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    style_id VARCHAR(50) NOT NULL UNIQUE,      -- e.g., 'default', 'impressionist'
    display_name VARCHAR(100) NOT NULL,        -- e.g., 'Default', 'Impressionist'
    description TEXT,                          -- User-friendly description
    class_name VARCHAR(100) NOT NULL,          -- Generator class name
    is_active BOOLEAN DEFAULT TRUE,            -- Enable/disable in UX
    sort_order INT DEFAULT 0,                  -- Display order in UX
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Relationship with `artworks` Table

The `artworks` table has an `art_style` field (VARCHAR) that stores the `style_id`:

```sql
CREATE TABLE artworks (
    ...
    art_style VARCHAR(50) NOT NULL DEFAULT 'default',
    ...
);
```

This approach allows:
- Backward compatibility (no breaking changes)
- Flexible style management
- No strict foreign key constraints (styles can be added/removed dynamically)

## Setup

### 1. Run Migration

Create the `art_styles` table:

```bash
python migrations/create_art_styles_table.py
```

### 2. Seed from Registry

Populate the table with styles from the generator registry:

```bash
python seed_art_styles.py
```

This automatically reads all available styles from `generators/registry.py` and adds them to the database.

## Using the ArtStyle Model

### Import

```python
from models import ArtStyle
```

### Get All Active Styles (for UX)

```python
# Get only active styles for display in the UI
active_styles = ArtStyle.get_active_styles()

for style in active_styles:
    print(f"{style['style_id']}: {style['display_name']}")
    print(f"  Description: {style['description']}")
```

### Get All Styles

```python
# Get all styles (including inactive)
all_styles = ArtStyle.get_all()

# Get only active styles
active_only = ArtStyle.get_all(active_only=True)

# Custom ordering
by_name = ArtStyle.get_all(order_by='display_name')
```

### Get Specific Style

```python
style = ArtStyle.get_by_id('impressionist')
if style:
    print(style['display_name'])  # "Impressionist"
    print(style['description'])   # "Soft, luminous style..."
```

### Check if Style Exists/Active

```python
if ArtStyle.exists('impressionist'):
    print("Style exists")

if ArtStyle.is_active('impressionist'):
    print("Style is active and can be used")
```

### Enable/Disable Styles

```python
# Disable a style (hide from UX)
ArtStyle.update_status('impressionist', False)

# Enable a style
ArtStyle.update_status('impressionist', True)
```

### Usage Statistics

```python
stats = ArtStyle.get_usage_stats()
for s in stats:
    print(f"{s['style_id']}: {s['artwork_count']} artworks, {s['total_likes']} likes")
```

## Management CLI

The `manage_styles.py` script provides CLI tools for managing styles.

### List All Styles

```bash
# List all styles
python manage_styles.py list

# List only active styles
python manage_styles.py list --active
```

### Show Style Details

```bash
python manage_styles.py show impressionist
```

### Enable/Disable Styles

```bash
# Disable a style (hide from UX)
python manage_styles.py disable impressionist

# Enable a style
python manage_styles.py enable impressionist
```

### View Usage Statistics

```bash
python manage_styles.py stats
```

## UX Integration Examples

### Flask Route for Style Selection

```python
from flask import render_template
from models import ArtStyle

@app.route('/generate')
def generate_form():
    # Get active styles for dropdown/selection
    styles = ArtStyle.get_active_styles()
    return render_template('generate.html', styles=styles)
```

### HTML Template

```html
<form action="/generate" method="POST">
    <label for="style">Art Style:</label>
    <select name="art_style" id="style">
        {% for style in styles %}
        <option value="{{ style.style_id }}">
            {{ style.display_name }} - {{ style.description }}
        </option>
        {% endfor %}
    </select>
    <button type="submit">Generate Art</button>
</form>
```

### Processing Form Submission

```python
from flask import request
from models import ArtStyle
from services.art_service import generate_art_from_github

@app.route('/generate', methods=['POST'])
def generate():
    repo_url = request.form.get('repo_url')
    art_style = request.form.get('art_style', 'default')

    # Validate style is active
    if not ArtStyle.is_active(art_style):
        return jsonify({'error': 'Invalid or inactive art style'}), 400

    # Generate art with selected style
    result = generate_art_from_github(
        github_url=repo_url,
        temp_dir='temp',
        images_dir='static/images',
        art_style=art_style  # Pass style to generator
    )

    return jsonify(result)
```

## Adding New Styles

### 1. Create Style Generator

Create new style in `generators/` following the pattern in `DEVELOPING_NEW_STYLES.md`:

```python
# generators/watercolor_style.py
class WatercolorStyleGenerator(BaseArtGenerator):
    STYLE_NAME = "watercolor"
    STYLE_DESCRIPTION = "Soft, flowing watercolor effect"
    # ... implementation
```

### 2. Register in Registry

Add to `generators/registry.py`:

```python
from .watercolor_style import WatercolorStyleGenerator

STYLE_REGISTRY = {
    'default': DefaultStyleGenerator,
    'impressionist': ImpressionistStyleGenerator,
    'watercolor': WatercolorStyleGenerator,  # Add new style
}
```

### 3. Sync to Database

Run the seed script to add the new style to the database:

```bash
python seed_art_styles.py
```

The script automatically detects new styles and adds them, or updates existing ones.

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│  1. Developer creates new style generator                   │
│     └─ generators/my_style.py                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. Register in generators/registry.py                      │
│     └─ STYLE_REGISTRY['my_style'] = MyStyleGenerator        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. Sync to database                                        │
│     └─ python seed_art_styles.py                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. Style appears in UX automatically                       │
│     └─ ArtStyle.get_active_styles()                         │
└─────────────────────────────────────────────────────────────┘
```

## Benefits

1. **Separation of Concerns**: Database-driven style management separate from code
2. **Dynamic Control**: Enable/disable styles without code changes
3. **UX Ready**: Easy integration with forms and UI components
4. **Statistics**: Track which styles are most popular
5. **Versioning**: Can store different versions of same repository in different styles
6. **Admin Control**: Manage styles via CLI or (future) admin panel

## Future Enhancements

Potential additions to the system:

- **Preview images**: Add `preview_image_url` column for style thumbnails
- **Parameters**: Store style-specific parameters as JSON
- **Categories**: Group styles by category (painterly, geometric, abstract, etc.)
- **Admin UI**: Web-based admin panel for managing styles
- **Style comparison**: Gallery view comparing same repo in different styles
- **User preferences**: Remember user's favorite style

## Files Reference

- `models/art_style.py` - ArtStyle model
- `migrations/create_art_styles_table.py` - Database migration
- `seed_art_styles.py` - Sync registry to database
- `manage_styles.py` - CLI management tool
- `schema.sql` - Database schema (includes art_styles table)
- `generators/registry.py` - Style registry

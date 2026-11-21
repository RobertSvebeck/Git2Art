# Git2Art Development Log

## Project Overview
Git2Art transforms git repositories into beautiful, unique abstract art. Each repository generates deterministic artwork where small code changes create small visual changes, and large changes create dramatic visual shifts.

## Development Journey

### Initial Concept (Session 1)
**Goal**: Explore if it's possible to turn git repos into art

**Key Ideas**:
- Map code metrics to visual parameters
- File types → shapes and colors
- Line counts → size
- Commit history → visual patterns
- Deterministic: same code = same art

**Initial Implementation**:
- Simple grid layout
- Basic shapes (circles, squares, triangles)
- Random RGB colors from hash
- Commit spiral visualization

### Art Theory Integration (Session 2)
**Challenge**: Colors were clashing, composition felt random

**Solution**: Applied professional art theory principles
- **Color Harmony**: Complementary, triadic, and analogous palettes
- **Golden Ratio**: Element positioning at φ focal points
- **Rule of Thirds**: Important files at intersection points
- **Fibonacci Spiral**: Natural element distribution
- **Visual Hierarchy**: Size based on importance

**Result**: Professional, balanced compositions with harmonious colors

### Organic Enhancement (Session 3)
**Challenge**: Art felt too sparse and static, colors too muted

**Improvements**:
1. **Vibrant Colors**: High saturation (0.75-0.95) for energy
2. **Organic Shapes**: Flowing Bézier curves, wave patterns
3. **Particle Effects**: Bursts around key elements
4. **Energy Lines**: Connecting elements with curves
5. **Wave Patterns**: Rhythmic movement across canvas
6. **Full Canvas**: No empty space, action everywhere

### Repository-Driven Palettes (Session 4)
**Challenge**: Need harmonious colors, not random vibrancy

**Solution**: Created 8 curated palettes based on project type
- `python` - Cool blues and teals
- `javascript` - Warm yellows and oranges
- `data` - Natural greens
- `creative` - Purples and pinks
- `sunset`, `ocean`, `forest`, `mono` - Various moods

**Implementation**:
- Auto-detect project type from file extensions
- Select appropriate palette
- Expand with tints, shades, and tones
- Multi-center gradient backgrounds

### Dynamic Enhancements (Session 5)
**Challenge**: Background too boring, elements too small, lines too thin

**Improvements**:
1. **Multi-Center Backgrounds**: 3-6 gradient centers with lightened palette colors
2. **Larger Objects**: 60-240px (was 35-135px)
3. **Thicker Lines**: 3-7px background, 2-6px connections, 4px waves
4. **More Particles**: 1.5x bigger, more numerous, larger burst radius
5. **Higher Opacity**: Better visibility across all elements

### Advanced Visual Effects (Session 6)
**Challenge**: Add more visual interest, depth, and sophistication

**Additions**:
1. **Gradient Shading**: 8-layer radial gradients on objects
2. **Hue Variations**: Subtle shifts across layers
3. **Spiral Patterns**: 2-5 spirals with fading opacity
4. **Concentric Loops**: 2-4 centers with 3-6 rings each
5. **Rotating Elements**: Orbital patterns around main objects
6. **Directional Fading**: Waves fade left-to-right with hue shifts

### IDEO-Inspired Techniques (Session 7)
**Research**: Studied "Painting with Code" article from IDEO

**Key Learnings**:
- **Cornu Curves** (Euler spirals) - smooth flowing curves
- **Hundreds of layers** with varying opacity
- **Thousands of lines** with individual properties
- **Delightful randomness** within constraints
- **Algorithm as art** - mathematical beauty

**Implementation**:
1. **Cornu Curves**: 50-70 curves with smooth curvature changes
2. **Rich Texture**: 500-3000 micro-lines around elements
3. **Extreme Variations**: Stroke widths from 0.5px to 20px
4. **Layered Complexity**: Multiple rendering passes

### Bold & Expressive Style (Session 8)
**Challenge**: Make it BOLD with thick, paint-like strokes and filled areas

**Final Enhancements**:
1. **MASSIVE Strokes**: Lines up to 30% of canvas width (480px!)
2. **Filled Color Areas**: 3-7 huge organic shapes (200-800px)
3. **Bold Color Blocks**: 4-10 large rectangles at angles
4. **Color Mixing**: Blend 2-3 palette colors per element
5. **Abstract Expressionist**: De Kooning/Kandinsky style

### Automatic Aspect Ratio Detection (Session 9)
**Goal**: Make canvas shape meaningful - let repository type determine aspect ratio

**Motivation**:
- Visual form should match content
- Mobile apps look different from web apps
- Aspect ratio becomes part of the repository's evolving "fingerprint"

**Implementation**:
1. **Detection Logic**:
   - Analyzes file type distribution in repository
   - Calculates percentages of mobile, web, and documentation files
   - Automatically selects appropriate aspect ratio

2. **Aspect Ratio Rules**:
   - **Portrait (3:4)**: Mobile apps → Swift, Kotlin, Java+Android files >30%
   - **Landscape (16:9)**: Web frontends → HTML/CSS/JS files >40% OR docs >50%
   - **Square (1:1)**: Backend, libraries, general purpose (default)

3. **Features**:
   - Default behavior: `--aspect auto` (automatic detection)
   - Manual override still available: `--aspect portrait_3:4`, `--aspect 16:9`, etc.
   - Output displays detected aspect ratio: `📐 Aspect ratio: 16:9 (1920x1080)`
   - Deterministic: same repo state = same aspect ratio

4. **Evolution Over Time**:
   - Repo starts as Python library → Square
   - Add React frontend → Shifts to Landscape
   - Add mobile app → Shifts to Portrait
   - Visual form evolves with the codebase

**Example Results**:
- Git2Art (Python backend) → square (1200x1200)
- React (JavaScript frontend) → 16:9 landscape (1200x675)
- Rails (Ruby backend) → square (1200x1200)

### Face Art Style (Session 10)
**Goal**: Create a human face where facial features are built from repository code metrics

**Motivation**:
- Unique visual representation: each repo gets a literal "face"
- Intuitive mapping: code characteristics → facial characteristics
- Personal connection: code becomes a portrait
- Evolution over time: face changes as codebase grows

**Implementation**:
1. **Feature Mapping Logic**:
   - **Face shape**: Total line count (small=round, medium=oval, large=angular)
   - **Eyes**: Size from file count, shape from file type distribution (round for frontend, almond for backend)
   - **Nose**: Size based on commit count
   - **Mouth**: Expression based on author count (more authors = bigger smile)
   - **Hair**: Style from primary language (curly for Python/Ruby, spiky for JS/TS, straight for Java/C++, wavy for others)
   - **Skin tone**: Derived from repository palette (lightened and desaturated)
   - **Colors**: All features use harmonious palette based on primary language

2. **Technical Features**:
   - Fully deterministic (same repo = same face, byte-for-byte)
   - Scales to any canvas size (800px to 2400px+)
   - All aspect ratios supported (portrait, landscape, square)
   - Integrated into style registry system

3. **Drawing Techniques**:
   - Round eyes: White sclera, colored iris, black pupil
   - Almond eyes: Polygon-based with gradient iris
   - Triangular nose with subtle shading
   - Bezier curve smiles with happiness based on collaboration
   - Hair styles: curly (overlapping circles), spiky (triangles), wavy (sine curves)
   - Rounded rectangle face for large repositories

4. **Evolution Examples**:
   - Solo project → Small smile, single-developer features
   - Add collaborators → Smile grows wider
   - Add more files → Eyes get larger
   - More commits → Nose becomes more prominent
   - Change primary language → Hair style changes

**Example Results**:
- Git2Art (15k lines, Python, solo) → Angular face, curly blue hair, small smile
- React (large, JavaScript, many authors) → Big smile, spiky orange hair
- Small hobby project → Round face, simple features

### Scene Model and History Animation (Session 12, 2026-11-21)
**Problem**: Every older style reseeds `random` from `total_lines`, so a one-line change reshuffled 15-83% of the pixels. Deterministic, but not stable, and impossible to animate.

**Solution** (`scene/` package, see SCENE_AND_ANIMATION_PLAN.md):
- `history.py`: one `git log --first-parent --reverse -M --numstat --summary` pass; replay matches HEAD exactly
- `state.py`: file entities with ids that survive renames
- `layout.py`: positions are pure functions of the path (directories at hashed angles from their parent), size `sqrt(lines)` normalised by total lines, colour by language
- `render.py` / `builder.py`: constellation renderer (2x supersampling, blurred glow layer, tapered polygon branches)
- `animate.py`: per-frame simulation easing sprites towards the target state, piped to ffmpeg
- New `constellation` style and `git2art.py --animate`
- Result: one-line edit changes 0.53% of pixels; ~50 ms per 720p frame

**Web fixes**: blobless clone (commit and author counts were always 1 with `--depth 1`), unique temp folder per request, 120 s clone timeout.

### Endless 3D Museum (Session 13, 2026-11-21)
Rewrite of `/gallery3d` as a walkable, procedurally generated museum (three.js 0.187, ES modules in `static/js/museum/`):
- `plan.js`: room = pure function of (world seed, cell) on a 26 m grid; door + half-corridor on every side so neighbours always connect; lattice mood colouring `(cx + 3*cz) mod 8` guarantees adjacent rooms differ; `isWalkable` is the collision model
- `room.js` / `roomArt.js`: architecture, frames, plaques, fixtures, benches, sculptures
- `lighting.js`: a pool of real spotlights moves to the current room; other rooms use fake light (`lightfx.js`: additive beam shader, halos, dust)
- `world.js`: streams a 3x3 window (unload beyond 2), one room built per frame, art dealt from a shuffled deck and remembered per room
- `controls.js`: pointer lock + WASD, touch joystick + drag look; `ui.js`: overlays
- Server: `/api/museum/artworks` (read-only) and WebP copies via `services/museum_service.py`
- `?debug=1` exposes `window.museumDebug` for scripted testing


### Sculptures and the 2D Museum (Session 14, 2026-11-21)
- `scene/repodata.py`: compact per-repo JSON (files with bytes, birth commit and touch count; languages; commit timeline) from a blobless clone; stored in `static/generated/repodata/` (files, not DB, so backfills never write to production)
- `static/js/shared/repoform.js`: repo data to a 3D form (path-stable, branches grow upwards); shared by both museums
- 3D: `sculpture.js` (instanced beads, merged bronze tubes, filaments; history replay via a `uProgress` uniform and per-element birth attributes), `court.js` (plinths, plaques, fixtures); wing = `cz > 0` is the Sculpture Court with dark moods (mod-4 lattice); wing signs over doors
- 2D: `/museum` route, `services/museum_layout.py` curates wings and rooms, `templates/museum.html` is server-rendered, `static/js/museum2d/` adds one-room-at-a-time walking and canvas sculptures
- Controls: arrows walk and turn, A/D strafe, Enter for details (no pointer lock needed)
- Lesson: low-roughness floors reflecting RoomEnvironment cause white grazing-angle glare; keep `scene.environmentIntensity` low (0.14)

### Light Installations and Render Upgrades (Session 15, 2026-11-21)
- Wing layout in `plan.js` `wingOf`: south (`cz > 0`) Sculpture Court, east (`cx > 0`) Light Installations, rest Painting Galleries
- `installation.js`: commit spiral (`commitField` in shared `repoform.js`) as additive point sprites with a time pulse shader, plus the file tree hung from the ceiling; Void mood with no fill light and near-zero environment reflection
- 2D: light wing rooms (repos with the longest histories) drawn by `museum2d/lightCanvas.js`
- Render: `batch.js` merges static meshes per material, rooms compile with `compileAsync` while hidden, shared surface textures pre-warmed, artwork textures uploaded on load, SMAA instead of MSAA
- Lesson: a 4x MSAA HalfFloat composer target rendered the whole frame black on ANGLE/Metal; always screenshot after render pipeline changes, metrics alone did not show it
- Lesson: environment strength is per mood (`environment` in moods.js); glossy floors reflect the RoomEnvironment as white glare otherwise

### Art Styles from Repository Data (Session 16, 2026-11-21)
- Old styles seed everything from `total_lines`, so they encode nothing and all repos look alike within a style; new styles live in `styles/` and render from the repodata JSON (no clone needed)
- `styles/pixel_city.py`: low-res canvas with a fixed 32-colour palette, nearest-neighbour upscale; districts from the folder tree via a binary treemap, hash-assigned plots, docs as parks, data files as warehouses, sky from days idle
- `scripts/style_lab.py`: contact sheet of 8 contrasting repos; `scripts/render_data_style.py`: render a style for the whole collection (DB rows unless `--dry-run`)
- `generators/data_style.py` adapts data styles to the CLI/web generator interface; Face removed; museum shows only active styles
- `styles/de_stijl.py`: binary treemap of the folder tree (depth 3, min share 1.8%), line weight by depth, primaries by language rank for the heaviest and most-edited fields, black for small config files
- `scripts/remove_repo.py`: preview, then `--yes` deletes artworks (likes cascade), images, WebP copies and repo data
- Clones run with `GIT_TERMINAL_PROMPT=0`: a private repo used to stop and prompt for credentials
- Lesson: OneDrive's file provider can "bounce" folders to `name 2` during sync conflicts, which git sees as deletions; compare with `git show HEAD:path | cmp` before renaming back

## Technical Architecture

### Color System
```python
RepositoryPalette.select_palette_by_repo(fingerprint)
→ Analyzes file types and metrics
→ Returns harmonious color scheme
→ Expands with tints/shades/tones
```

### Organic Shapes Module
- `flowing_line()` - Bézier curves
- `spiral_pattern()` - Expanding spirals
- `circle_loop()` - Concentric circles
- `rotating_pattern()` - Orbital elements
- `cornu_inspired_curve()` - Euler spirals
- `generate_texture_lines()` - Micro-line texture

### Layering Order
1. Multi-center gradient background
2. Large filled color areas
3. Bold background flows (thick)
4. Cornu curves (hundreds)
5. Bold color blocks
6. Spirals and loops
7. Main file elements (gradient blobs)
8. Rich texture (thousands of lines)
9. Rotating orbital elements
10. Connection lines
11. Particle effects
12. Fading wave patterns

### Deterministic System
- All randomness seeded from repository metrics
- `total_lines` → main seed
- File content hashes → element-specific seeds
- Same repo state = identical artwork (byte-for-byte)

## Art Theory Principles Applied

### Color Theory
- **Analogous**: Adjacent hues (peaceful, cohesive)
- **Complementary**: Opposite hues (high contrast)
- **Triadic**: Evenly spaced hues (balanced, vibrant)

### Composition
- **Golden Ratio (φ ≈ 1.618)**: Natural balance
- **Rule of Thirds**: Dynamic focal points
- **Fibonacci Spiral**: Natural flow
- **Visual Hierarchy**: Size = importance

### Advanced Techniques
- **Radial Gradients**: Multi-layer depth
- **Hue Shifting**: Subtle color variations
- **Directional Fading**: Progressive opacity/color changes
- **Layered Transparency**: Depth through overlapping
- **Color Mixing**: Blending multiple palette colors

## Performance Considerations

### Optimization Decisions
- Micro-lines: Thousands (not millions) for speed
- Cornu curves: 50-70 (not hundreds) for generation time
- Main blobs: 8 gradient layers (not more) for balance
- Canvas size: Default 1200x1200, optional up to 2400x2400

### Rendering Time
- Small repos (5 files): ~2-3 seconds
- Medium repos (20 files): ~5-8 seconds
- Large repos (50+ files): ~10-15 seconds

## Repository URL
https://github.com/RobertSvebeck/Git2Art

## Key Features

✅ **Repository-driven palettes** (10 curated schemes based on language)
✅ **Automatic aspect ratio** (canvas shape matches repo type: mobile=portrait, web=landscape, backend=square)
✅ **Multiple art styles** (expressionist, impressionist, watercolor, pixel, face)
✅ **Deterministic** (same code = same art)
✅ **Incremental changes** (small changes = small differences)
✅ **Art theory-based** (golden ratio, color harmony)
✅ **IDEO-inspired** (Cornu curves, layered complexity)
✅ **Bold & expressive** (thick strokes, filled areas)
✅ **Professional quality** (gallery-worthy output)
✅ **Web application** (Flask-based UI with smart caching)

### Flask Web Application (Session 11)
**Goal**: Create web interface for public access to Git2Art

**Phase 1 Implementation** (✅ COMPLETED Oct 19, 2025):
1. **Modular Backend Structure**:
   - Application factory pattern with `create_app()`
   - Separated routes, services, and utilities
   - `art_service.py` - Generation logic with caching
   - `git_service.py` - Git operations and validation
   - `watermark.py` - Automatic watermarking utility

2. **Smart Caching System**:
   - Filesystem-based with JSON metadata
   - Commit hash comparison for cache validation
   - Instant response for unchanged repositories
   - Auto-directory creation on startup

3. **Beautiful UI**:
   - Gradient header with modern design
   - Responsive form with client-side validation
   - Real-time status updates (loading/success/error)
   - Smooth animations and transitions

4. **Features Delivered**:
   - GitHub URL input with validation (HTTPS + git@ formats)
   - Automatic repository cloning and updating
   - Art generation integration with `git2art.py`
   - Watermarking with repository URL
   - Download functionality for generated artwork
   - Error handling and user feedback

5. **Documentation Created**:
   - FLASK_SETUP.md - Technical architecture
   - QUICKSTART.md - User guide
   - PHASE1_SUMMARY.md - Implementation details

**Phase 2 Implementation** (✅ COMPLETED Oct 19, 2025):
1. **Gallery System**:
   - `get_all_gallery_artworks()` service function
   - Reads all cache files from filesystem
   - Extracts metadata (repo_name, commit_hash, created_at)
   - Automatic sorting by creation date (newest first)

2. **Gallery UI**:
   - Responsive grid layout with card design
   - Each card displays: artwork thumbnail, repo name, commit hash, timestamp
   - "View Full Size" link for each artwork
   - Empty state when no artworks exist
   - Consistent design with main app (gradient header, modern styling)

3. **Navigation**:
   - Bidirectional navigation between home and gallery
   - Header navigation links on both pages
   - Clean URL structure (/gallery route)

4. **Features Delivered**:
   - Browse all generated artworks in grid layout
   - Automatic sorting (newest first)
   - Display repository metadata for each artwork
   - Direct links to view full-size images
   - Mobile-responsive design
   - No database required (filesystem-based)

**Phase 3 Implementation** (✅ COMPLETED Oct 19, 2025):
1. **Database Infrastructure**:
   - MariaDB integration with PyMySQL
   - Environment-based configuration (.env file)
   - Connection pooling and context managers
   - Automatic schema initialization (init_db.py)

2. **Database Schema**:
   - `artworks` table: stores artwork metadata (repo_url, commit_hash, image_path, like_count)
   - `artwork_likes` table: tracks user likes with foreign key relationships
   - Proper indexes on frequently queried fields
   - Unique constraints to prevent duplicates

3. **Data Models**:
   - `Artwork` model: CRUD operations for artwork records
   - `ArtworkLike` model: like/unlike operations with atomic transactions
   - Database-backed gallery with filesystem fallback
   - Automatic like count synchronization

4. **Like Functionality**:
   - Session-based user identification (anonymous users)
   - Toggle like/unlike with single click
   - Real-time like count updates
   - Visual feedback (heart icon changes color)
   - Server-side validation and atomic transactions

5. **Features Delivered**:
   - Persistent artwork storage in MariaDB
   - Like/unlike functionality for each artwork
   - Popularity tracking via like counts
   - Gallery sorting by creation date or popularity
   - Graceful degradation (filesystem fallback if DB unavailable)
   - Secure database operations with prepared statements

## Future Possibilities

### Near Term
- ✅ Flask web application Phase 1 (COMPLETED)
- ✅ Gallery page for browsing all generated art (Phase 2 - COMPLETED)
- ✅ Database integration with MariaDB (Phase 3 - COMPLETED)
- Deployment to production web hosting (Phase 4)
- Animation showing repository evolution over time
- More art style presets (minimalist, maximalist, etc.)
- Export formats (SVG, high-res print)

### Long Term
- 3D visualization options
- Interactive parameter tweaking
- Social sharing features
- Repository comparison visualizations
- User accounts and authentication

## Lessons Learned

1. **Start simple, iterate**: Initial grid → golden ratio → bold expressionism
2. **Art theory matters**: Random colors → harmonious palettes = huge improvement
3. **Study masters**: IDEO article provided excellent techniques
4. **Balance determinism with variation**: Controlled randomness within constraints
5. **Bold is better**: Thick strokes and filled areas = more impact
6. **Layering creates depth**: Multiple passes build sophistication
7. **Performance vs. beauty**: Balance micro-details with generation time
8. **No emojis in code**: Emojis cause Unicode encoding errors in Flask/web environments - use plain ASCII text only

## Code Quality

- Modular design (separate color, shape, generation classes)
- Clear method names describing purpose
- Extensive comments explaining art theory principles
- Deterministic seeding throughout
- Repository-agnostic (works with any git repo)

## Development Guidelines

### File Organization
- **Keep files small**: Split large files into smaller, focused modules
- **Backend structure**: Separate concerns (routes, models, services, utils)
- **Frontend structure**: Separate HTML templates, CSS stylesheets, and JavaScript files
- **No mixing**: Templates should reference external CSS/JS, not inline them

### Code Style
- **Minimal comments**: Only comment when logic is complex or non-obvious
- **Self-documenting**: Use clear variable and function names instead of comments
- **DRY principle**: Always reuse existing functions/subs instead of creating duplicates
- **Delete dead code**: Remove unused code immediately, don't comment it out
- **NO EMOJIS**: Never use emojis in code (print statements, comments, strings). They cause Unicode encoding errors in Flask and other environments. Use plain ASCII text only.

### Project Maintenance
- **Update TODO.md**: Mark tasks as completed immediately after finishing
- **Clean as you go**: Remove deprecated code during refactoring
- **One purpose per file**: Each module should have a single, clear responsibility

### Flask Application Standards
- **Modular backend**:
  - `app.py` - Application factory and configuration
  - `routes/` - Endpoint handlers
  - `services/` - Business logic (art generation, git operations)
  - `utils/` - Helper functions
  - `models/` - Data structures (if needed)

- **Separated frontend**:
  - `templates/` - HTML files only
  - `static/css/` - Stylesheets
  - `static/js/` - JavaScript files
  - `static/images/` - Static assets

- **Keep it simple**: Don't over-engineer, start minimal and add complexity only when needed

---

*Generated with Claude Code - A journey from concept to bold abstract expressionism*

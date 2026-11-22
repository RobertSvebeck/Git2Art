# Git2Art - TODO List

## High Priority

### Visual Improvements
- ✅ **Increase contrast** in compositions (darker darks, lighter lights)
- ✅ **Add complementary color accents** - Use opposite colors on color wheel for pop
- ✅ **Implement color wheel theory** - Triadic, split-complementary, tetradic schemes
- ✅ Complementary colors automatically added to palette
- ✅ Tints at 1.4x brightness, shades at 0.4x brightness for high contrast
- ✅ Advanced expand_palette_with_theory() implements all color schemes
- ✅ Add contrast adjustment parameter (low/medium/high)
- ✅ Experiment with different palette mixing ratios
- ✅ Use analogous + complementary variations per element
- ✅ ColorMixer class with blend_colors() and get_analogous_variation()
- ✅ Elements blend 2-4 colors with deterministic weighted ratios
- ✅ Layered shapes use complementary colors for inner layers (30% chance)
- ✅ Shadows use analogous variations for cohesive look
- ✅ All new features maintain 100% determinism (verified with MD5 hashing)

### Flask Web Application

#### Phase 1: Basic Setup (No Database) ✅ COMPLETED
- ✅ Create basic Flask app structure
- ✅ Add GitHub URL input form
- ✅ Generate artwork from GitHub URL
- ✅ Store generated images in folder (filesystem-based)
- ✅ Skip regeneration if repo exists and hasn't changed (check commit hash)
- ✅ Add watermark on image
- ✅ Add download button for artwork

#### Phase 2: Gallery Feature (Filesystem-based) ✅ COMPLETED
- ✅ Create gallery page to browse all generated art
- ✅ Display artwork with:
  - ✅ Repository name
  - ✅ Commit hash
  - ✅ Creation timestamp
  - ✅ View full size link
- ✅ Gallery grid/card layout
- ✅ Sort gallery (newest first)

#### Phase 3: Database Integration (MariaDB) ✅ COMPLETED
- ✅ Set up .env configuration for MariaDB credentials
- ✅ Create database schema for:
  - ✅ Generated artworks (repo_url, commit_hash, image_path, created_at)
  - ✅ User likes (user_id, artwork_id, liked_at)
- ✅ Implement "like" functionality for artworks
- ✅ Track popularity metrics
- ✅ Migrate from filesystem-only to database-backed gallery

#### Phase 4: Deployment
- [ ] Deploy to Oderland Webhotel (more details needed) Cpanel based passenger_WSGI.py
- [ ] Set up production database connection
- [ ] Configure static file serving for images

### Documentation
- ✅ README updated with Option 1 (CLI) and Option 2 (Flask) usage patterns
- ✅ CLAUDE.md documents full development journey and architecture
- ✅ DOCUMENTATION_INDEX.md provides complete reference
- ✅ Research folder organized with development notes
- [ ] Add example artworks/gallery to README
- [ ] Create visual comparison guides
- [ ] Create contributing guidelines

### Web Fixes (found 2026-11-21)
- ✅ Clone was `--depth 1`, so commit and author counts were always 1 on the web: now a blobless clone
- ✅ Temp clone folders keyed by repo name collided between owners and concurrent requests: now unique per request
- ✅ No clone timeout: now 120 s
- ✅ `extract_repo_name` stripped `.git` anywhere in the URL
- [ ] SECRET_KEY falls back to a hard-coded dev key when the environment variable is missing
- [ ] No repository size cap before cloning

### Testing
- [ ] Test on large repositories (100+ files)
- [ ] Test on different language ecosystems (Rust, Go, Java)
- [ ] Verify determinism across multiple runs
- [ ] Performance profiling and optimization
- [ ] Test edge cases (empty repos, binary-only repos)

## Medium Priority

### Art Enhancements
- ✅ **Default to canvas aspect ratios** instead of square (e.g., 16:10, 3:2, 4:3)
- ✅ Common canvas sizes: 1920x1200, 1800x1200, 1600x1200
- ✅ Portrait and landscape orientation options
- ✅ 8 aspect ratio presets including portrait modes
- ✅ --aspect CLI parameter with all options
- ✅ Default changed from square (1200x1200) to 4:3 (1600x1200)
- [ ] Preset canvas sizes (social media, print standards, display)
- [ ] Add art style presets (minimalist, maximalist, classic)
- [ ] Create "dark mode" palette variants
- [ ] Add seasonal/themed color schemes
- [ ] Add texture overlay options (canvas, paper, watercolor)

### Features
- ✅ **Smart filename generation** - Name images after git repo name (e.g., `Git2Art_1600x1200_20251019_143022_aa7f55a.png`)
- ✅ Include repo name, size, timestamp in filename
- ✅ Option to include commit hash in filename for versioning
- ✅ Sanitize special characters in repo names for filenames
- ✅ Timestamp ensures uniqueness for repos with same name
- [ ] Auto-create output directory if it doesn't exist
- ✅ Animation: Show repository evolution over time (CLI `--animate`, constellation style; web version planned, see SCENE_AND_ANIMATION_PLAN.md)
- [ ] Compare mode: Visual diff between two commits
- [ ] Gallery mode: Generate art for all branches
- [ ] Export to SVG for infinite scaling
- [ ] High-res export for printing (300 DPI, large formats)
- [ ] Batch processing for multiple repositories

### Code Quality
- [ ] Add unit tests for color theory functions
- [ ] Add integration tests for art generation
- [ ] Add type hints throughout
- [ ] Create detailed API documentation
- [ ] Refactor into smaller, focused modules
- [ ] Add logging for debugging

## Low Priority

### Advanced Features
- ✅ 3D museum: endless walkable gallery (`/gallery3d`, static/js/museum/)
- [ ] Museum: run `scripts/make_museum_images.py` and `scripts/make_repo_data.py` on the server after deploying
- ✅ Sculpture Court (3D) and 2D museum at /museum
- ✅ Museum: light installation wing (3D and 2D)
- [ ] Museum: living shader canvases, cinema room
- ✅ Museum: SMAA, compileAsync per room, merged static geometry, pre-warmed textures (draw calls 437 -> 138 in the entrance)
- [ ] Museum: 4x MSAA half-float composer target renders black on ANGLE/Metal; revisit if SMAA is not enough
- [ ] Museum: bright neighbouring rooms bloom through doorways; tune per-room exposure
- [ ] Museum: decide whether /museum replaces the /gallery grid

### Art Styles Rework (2026-11-21)
- ✅ Style lab (`scripts/style_lab.py`) and data styles rendered from repodata (`styles/`)
- ✅ New: Pixel City, De Stijl, Garden, Tapestry. Rebuilt: Expressionist, Impressionist, Watercolour, Psychedelic. Removed: Face, Pixel, Nature
- [ ] On the server: `python scripts/remove_repo.py https://github.com/torvalds/linux https://github.com/yeongpin/cursor-free-vip --yes`
- [ ] On the server: `python scripts/apply_style_rework.py --yes --render` (registers styles, disables retired ones, re-renders all repositories)
- [ ] Consider a blocklist so oversized or private repos cannot be resubmitted
- ✅ Gallery hides retired (inactive) styles; their artwork pages stay reachable by direct link
- ✅ Artworks stored as WebP (lossless for flat-colour art), downloads converted to PNG; about 165 MB for the full collection instead of about 1.5 GB as PNG
- ✅ `scripts/cleanup_artworks.py`: orphan files always; `--superseded` (unliked older versions) and `--retired` on request; preview without `--yes`
- ✅ 3D museum: canvases with depth (gallery wrap or wooden panel), linen weave, brushstroke relief, varnish, wall shadows
- ✅ 3D museum invitations ("Your repository could hang here") in the entrance and ~30% of painting rooms; in-museum submit form hangs the result in place
- ✅ About page rewritten for the museums and new styles
- ✅ Celebrating the artists: owner, avatar, contributors and star count on every work; star buttons; an artist room per owner in both museums (teleport in 3D, `?artist=owner`); artist card on the artwork page; "Code is a shared art" copy on home and about
- [ ] Artists: run `scripts/refresh_github_info.py` from cron (or set GITHUB_TOKEN) so star counts stay fresh
- [ ] Artists: show the owner on /gallery cards too
- [ ] On the server after pulling: `python scripts/render_data_style.py <style>` for each style (or `apply_style_rework.py --yes --render`), then `python scripts/cleanup_artworks.py --superseded --retired --yes`

## Completed ✅

### Core Functionality
- ✅ Basic git repository analysis
- ✅ **100% Deterministic art generation** (identical repos → identical artwork)
- ✅ Deterministic random number generation from file hashes
- ✅ File-based fingerprinting with MD5 hashing
- ✅ Commit history visualization
- ✅ Tested: Multiple generations produce byte-identical PNG files

### Art Theory
- ✅ Color harmony (complementary, triadic, analogous)
- ✅ Golden ratio composition
- ✅ Rule of thirds
- ✅ Fibonacci spiral distribution
- ✅ Visual hierarchy

### Visual Effects
- ✅ Gradient shading on objects
- ✅ Hue variations within elements
- ✅ Spiral patterns
- ✅ Concentric circular loops
- ✅ Rotating orbital elements
- ✅ Directional color fading
- ✅ Wave patterns with motion

### IDEO-Inspired
- ✅ Cornu/Euler spiral curves
- ✅ Hundreds of layered curves
- ✅ Thousands of micro-texture lines
- ✅ Delightful randomness within constraints
- ✅ Extreme stroke width variations

### Bold Style
- ✅ Massive stroke widths (up to 30% of canvas)
- ✅ Large filled color areas
- ✅ Bold rotated color blocks
- ✅ Color mixing (2-3 colors per element)
- ✅ Abstract expressionist aesthetic

### Repository-Driven
- ✅ 8 curated color palettes
- ✅ Auto-detection of project type
- ✅ Palette expansion with tints/shades
- ✅ Multi-center dynamic backgrounds

### Documentation
- ✅ Comprehensive README
- ✅ Art theory documentation (ART_THEORY.md)
- ✅ Version comparison (COMPARISON.md)
- ✅ Development log (CLAUDE.md)

## Ideas for Consideration

### Experimental
- [ ] Audio-reactive art (repository metrics → sound)
- [ ] AR visualization (view art in physical space)
- [ ] Collaborative art (multiple repos → single piece)
- [ ] AI-enhanced: Use ML to suggest compositions
- [ ] Generative variations: Create series from one repo
- [ ] Print-on-demand integration (posters, canvas prints)

### Technical Exploration
- [ ] WebAssembly version for browser-based generation
- [ ] GPU acceleration for faster rendering
- [ ] Procedural generation with Perlin noise
- [ ] Physics simulation for element placement
- [ ] L-system generation for organic patterns

### Business Ideas
- [ ] Freemium web service (free low-res, paid high-res)
- [ ] Licensing for corporate use
- [ ] Custom palette creation service
- [ ] Art commissioning for specific repositories
- [ ] Workshop/tutorial series

## Performance Optimizations
- [ ] Consider caching generated textures
- [ ] Parallelize texture line generation
- [ ] Optimize gradient rendering
- [ ] Profile and optimize hot paths
- [ ] Consider C extension for critical loops

## Questions to Resolve
- [ ] Should we limit file count for texture generation?
- [ ] What's the optimal balance between detail and speed?
- [ ] Should we add watermark/signature option?
- [ ] How to handle monorepos with multiple languages?
- [ ] Should generated art be reproducible across different systems?

## Repository Status

✅ **Public Release Ready**
- Documentation organized (public in root, research in /research)
- README updated with clear usage instructions (CLI and Flask options)
- .env.example template provided for easy setup
- Development folders (old, .claude, .playwright-mcp) excluded from git

---

*Last Updated: 2025-10-26*
*Status: All Flask features complete (Generation, Gallery, Database Integration)*
*Next Phase: Deployment to production (Phase 4)*

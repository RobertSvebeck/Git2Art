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

#### Phase 2: Gallery Feature (Filesystem-based)
- [ ] Create gallery page to browse all generated art
- [ ] Display artwork with:
  - [ ] Repository name
  - [ ] Repository owner/user
  - [ ] Link to GitHub repository
- [ ] Gallery grid/card layout
- [ ] Sort gallery (newest first, most popular, etc.)

#### Phase 3: Database Integration (MariaDB)
- [ ] Set up .env configuration for MariaDB credentials
- [ ] Create database schema for:
  - [ ] Generated artworks (repo_url, commit_hash, image_path, created_at)
  - [ ] User likes (user_id, artwork_id, liked_at)
- [ ] Implement "like" functionality for artworks
- [ ] Track popularity metrics
- [ ] Migrate from filesystem-only to database-backed gallery

#### Phase 4: Deployment
- [ ] Deploy to Heroku/Render/Railway
- [ ] Set up production database connection
- [ ] Configure static file serving for images

### Documentation
- [ ] Add example artworks to README
- [ ] Create visual comparison (before/after changes)
- [ ] Add usage examples with different repo types
- [ ] Document each palette style with examples
- [ ] Create contributing guidelines

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
- [ ] Animation: Show repository evolution over time
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
- [ ] 3D visualization option (using Three.js or similar)
- [ ] Interactive mode: Adjust parameters in real-time
- [ ] Social features: Share artwork gallery
- [ ] Repository insights: Visual analytics from art
- [ ] NFT export option
- [ ] Video generation: Repository timeline animation

### Integration
- [ ] GitHub Action for auto-generating art on commit
- [ ] VS Code extension
- [ ] CLI improvements (progress bar, verbose mode)
- [ ] Docker container for easy deployment
- [ ] API endpoint for programmatic access

### Community
- [ ] Create showcase gallery on website
- [ ] Add community-contributed palettes
- [ ] Art competition/challenges
- [ ] Blog posts about art generation techniques
- [ ] Tutorial videos

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

## Bug Fixes Needed
- [ ] None currently identified

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

---

*Last Updated: 2025-10-18*
*Priority: Focus on Flask web app for public accessibility*

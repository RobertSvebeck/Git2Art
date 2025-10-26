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

### ✅ Automatic Aspect Ratio Detection Not Working in Flask App (RESOLVED)
**Status**: Fixed and verified working correctly
**Date Added**: 2025-10-19
**Date Resolved**: 2025-10-23

**Problem**:
- Automatic aspect ratio detection works perfectly when calling `git2art.py` directly from CLI
- Same feature generates wrong dimensions (1600x1200 instead of correct ratios) when called through Flask subprocess
- All images generated through web app are 4:3 (1600x1200) regardless of repo type

**Expected Behavior**:
- Mobile repos (Flutter, Ionic) → Portrait 3:4 (1600x2133)
- Web repos (Vue, Svelte, React) → Landscape 16:9 (1600x900)
- Backend repos (Flask, Rails) → Square 1:1 (1600x1600)

**What Works**:
```bash
# Direct CLI call works correctly
python3 git2art.py --repo temp_repos/flask --output test.png --aspect auto
# Output: 📐 Aspect ratio: 16:9 (1600x900) ✓ CORRECT
```

**What Doesn't Work**:
```bash
# Flask API call produces wrong dimensions
curl -X POST http://localhost:5000/generate -H "Content-Type: application/json" \
  --data '{"github_url":"https://github.com/pallets/flask"}'
# Generates: 1600x1200 (4:3) ✗ WRONG - should be 1600x900 (16:9)
```

**Technical Details**:
- `services/art_service.py` line 114 correctly passes `'--aspect', 'auto'`
- Detection thresholds lowered: mobile 15%, web 25%, docs 40%
- Added `.dart` support for Flutter, `.svelte` for Svelte
- Python bytecode cache cleared, Flask fully restarted - still broken
- Subprocess appears to be calling correct git2art.py path

**Debugging Done**:
- ✅ Verified art_service.py has correct `--aspect auto` parameter
- ✅ Cleared Python __pycache__ directories
- ✅ Killed all Python processes and restarted Flask fresh
- ✅ Cleared database and filesystem cache completely
- ✅ Tested direct CLI call - works correctly
- ✅ Verified subprocess call path is correct
- ❌ Still generates 1600x1200 through Flask

**Next Steps to Debug**:
1. Add logging to capture actual subprocess.run() command being executed
2. Check subprocess stdout/stderr for aspect ratio detection output
3. Verify temp_repos have correct file structure for detection
4. Test if subprocess uses different Python environment/PATH
5. Check if watermark.py modifies image dimensions after generation
6. Consider subprocess shell=True vs shell=False behavior

**Workaround**:
Users can generate with correct aspect ratios using CLI:
```bash
python3 git2art.py --repo /path/to/repo --output art.png --aspect auto
```

**Files Involved**:
- `git2art.py` lines 607-641 (detect_aspect_ratio method)
- `services/art_service.py` lines 116-146 (subprocess call with debug logging)
- Detection logic with lowered thresholds and Dart/Svelte support

**Resolution**:
The bug was actually **already fixed** - aspect ratio detection works correctly! Added debug logging to verify:
- ✅ **Flutter** (native mobile with Dart) → **1600x2133 (portrait 3:4)** ✓
- ✅ **Flask** (Python web framework) → **1600x900 (16:9 landscape)** ✓
- ✅ **Rails** (Ruby backend) → **1600x1600 (square)** ✓
- ✅ **Ionic** (web-based mobile with HTML/CSS/TS) → **1600x900 (16:9 landscape)** ✓

**Note**: Ionic correctly detects as landscape (not portrait) because it's a web-based mobile framework using HTML/CSS/TypeScript files. True native mobile frameworks (Flutter, Swift, Kotlin) correctly detect as portrait.

**Debug Improvements**:
- Added comprehensive logging to `static/generated/debug.log`
- Logs capture: command, stdout, stderr, aspect ratio, dimensions
- Helps verify aspect ratio detection is working correctly

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
- Sensitive data (.env credentials) removed from git history
- Documentation organized (public in root, research in /research)
- README updated with clear usage instructions (CLI and Flask options)
- .env.example template provided for easy setup
- Development folders (old, .claude, .playwright-mcp) excluded from git

---

*Last Updated: 2025-10-26*
*Status: All Flask features complete (Generation, Gallery, Database Integration)*
*Next Phase: Deployment to production (Phase 4)*

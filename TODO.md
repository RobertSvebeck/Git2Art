# Git2Art - TODO List

## High Priority

### Flask Web Application
- [ ] Create basic Flask app structure
- [ ] Add file upload or GitHub URL input
- [ ] Display generated artwork
- [ ] Allow size and style customization
- [ ] Add download button for artwork
- [ ] Deploy to Heroku/Render/Railway

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
- [ ] Add art style presets (minimalist, maximalist, classic)
- [ ] Create "dark mode" palette variants
- [ ] Add seasonal/themed color schemes
- [ ] Implement multiple aspect ratios (16:9, 4:3, square)
- [ ] Add texture overlay options (canvas, paper, watercolor)

### Features
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
- ✅ Deterministic art generation
- ✅ File-based fingerprinting
- ✅ Commit history visualization

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

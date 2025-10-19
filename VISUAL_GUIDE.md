# Git2Art - Visual Language Guide

## Reading the Artwork: What Each Visual Element Tells You

Git2Art creates artwork that is **visually readable** - you can tell important information about the codebase just by looking at the image!

---

## 🎨 Color Palettes = Programming Languages

Each language has a distinctive color palette inspired by its identity:

### **Python** - Cool Blues & Teals 🐍
- **Colors**: Sky blue, ocean blue, teal
- **Recognition**: Cool, calming blues like Python's logo
- **Means**: Python-dominant codebase

### **JavaScript/TypeScript** - Warm Yellows & Oranges ⚡
- **Colors**: Bright yellow, orange, deep orange
- **Recognition**: Warm, energetic colors like JS logo
- **Means**: Web/JavaScript project

### **PHP** - Purple & Violet 🟣
- **Colors**: Deep purple, violet, lavender
- **Recognition**: Rich purple tones
- **Means**: PHP-dominant backend

### **Java** - Burgundy & Brown ☕
- **Colors**: Red, crimson, professional brown
- **Recognition**: Earthy, enterprise reds
- **Means**: Java/Enterprise codebase

### **Ruby** - Rich Reds & Gems 💎
- **Colors**: Crimson, firebrick, tomato red
- **Recognition**: Vibrant gemstone reds
- **Means**: Ruby/Rails project

### **Go/Rust** - Cyan & Steel ⚙️
- **Colors**: Cyan, blue, metallic steel
- **Recognition**: Modern, industrial blue-grays
- **Means**: Systems programming (Go/Rust)

### **C/C++** - Industrial Gray & Blue 🔧
- **Colors**: Charcoal, dark blue, slate
- **Recognition**: Industrial, low-level grays
- **Means**: C/C++ systems code

### **Mobile (Swift/Kotlin)** - Vibrant Orange & Pink 📱
- **Colors**: Coral, bright orange, pink
- **Recognition**: Energetic, modern mobile colors
- **Means**: iOS/Android mobile app

### **Data Science** - Natural Greens 📊
- **Colors**: Emerald, forest green, teal
- **Recognition**: Fresh, analytical greens
- **Means**: Python + data files (CSV, JSON)

### **Documentation** - Elegant Grays 📝
- **Colors**: Slate, silver, sophisticated grays
- **Recognition**: Neutral, clean grays
- **Means**: Markdown/documentation-heavy

---

## 📐 Visual Structure = Code Organization

### **Element Placement**
- **Centered, organized**: Well-structured codebase
- **Spread across canvas**: Diverse, distributed files
- **Clustered**: Related modules grouped together

### **Element Sizes**
- **Large elements (up to 70% canvas)**: Big, important files
- **Small elements (3% canvas)**: Utility files, helpers
- **Size variety**: Diverse file sizes (good modularity)

### **Number of Elements**
- **Few large elements**: Monolithic structure
- **Many small elements**: Microservices/modular
- **15 elements**: Exactly 15 files in repo

---

## 🔷 Shape Types = File Characteristics

Each file is represented by a shape based on its hash:

1. **Organic Blobs**: Smooth, natural code flow
2. **Star/Spiky Shapes**: Complex, many connections
3. **Polygons**: Structured, geometric code
4. **Stretched Blobs**: Elongated logic paths
5. **Splatter Shapes**: Irregular, creative code

**The shape is deterministic** - same file content = same shape!

---

## 🌀 Decorative Elements = Repository Metrics

### **Spirals** (5-10 visible)
- **More spirals**: More commits
- **Longer spirals**: Higher complexity
- **Smooth spirals**: Refined, polished code

### **Connection Lines**
- **Many connections**: Interconnected modules
- **Curved connections**: Smooth dependencies
- **Thick connections**: Strong relationships

### **Background Texture**
- **Rich texture**: Many small files
- **Smooth background**: Clean, minimal
- **Blurred edges**: Polished, professional

---

## 📊 What You Can Tell at a Glance

### **Example Interpretations**

**Blue/Teal with many small elements, organized center**
→ Well-structured Python project with modular design

**Purple with few large shapes, scattered**
→ PHP project with monolithic files spread out

**Yellow/Orange with many curved connections**
→ JavaScript web app with interconnected modules

**Green with star shapes and rich texture**
→ Data science project with complex notebooks

**Gray with minimal elements**
→ Documentation or starter project

---

## 🎯 Reading Complexity

### **Simple Project** (Low complexity)
- Few elements (< 10)
- Small canvas usage
- Minimal spirals
- Light texture
- Soft colors

### **Medium Project** (Moderate complexity)
- 10-30 elements
- Good variety in sizes
- 5-10 spirals
- Balanced texture
- Rich colors

### **Complex Project** (High complexity)
- 30+ elements
- Large elements dominating
- 10+ spirals with long turns
- Dense texture layers
- Deep, saturated colors

---

## 🔍 Language Detection Logic

Git2Art analyzes your repository and selects a palette based on:

1. **Dominant Language** (>30% of total lines)
   - PHP → Purple
   - Java → Burgundy
   - Ruby → Red
   - Python → Blue
   - JavaScript → Yellow/Orange
   - etc.

2. **Special Cases**
   - Python + Data files (>20%) → Green (Data Science)
   - Markdown-heavy (>50%) → Gray (Documentation)

3. **Fallback**
   - Mixed repos → Palette based on most lines

---

## 🎨 Deterministic Art

**Important**: The same repository state ALWAYS produces the same artwork!

- Same files → Same colors
- Same content → Same shapes
- Same structure → Same composition
- Small code changes → Small visual changes
- Large refactors → Large visual changes

This means you can:
- **Track progress** visually over time
- **Spot major changes** by comparing artworks
- **Verify code state** matches expected art
- **Share reproducible** artwork with your team

---

## 💡 Tips for Interpreting Art

1. **Color = Language**: Look at dominant colors first
2. **Size = Importance**: Biggest shapes = biggest files
3. **Number = Scale**: Count elements ≈ file count
4. **Chaos = Complexity**: More overlapping = more interdependencies
5. **Smoothness = Polish**: Blurred, soft = mature project

---

*Generated art is not just beautiful - it's informative!* 🎨📊

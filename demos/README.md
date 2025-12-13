# Demo Scripts

Visual demonstration and testing scripts for ShokeDex UI components.

## 📋 Overview

Demo scripts provide visual testing, reference screenshot generation, and interactive demonstrations of UI features. They're useful for:
- Verifying visual consistency across implementations
- Generating documentation screenshots
- Manual testing of UI components
- Debugging layout and rendering issues

## 🎬 Available Demos

### Core Demos

**demo_screenshot.py** - Reference Screenshot Generator
```bash
python demos/demo_screenshot.py
```
Generates comprehensive screenshots of all major UI states for documentation:
- Home screen with different generations
- Detail view for multiple Pokémon across all tabs
- Evolution panel variations (linear, branching, single-stage)
- Type badge displays
- Screenshots saved to `screenshots/` with descriptive names

**demo_evolution_display.py** - Evolution Panel Testing
```bash
python demos/demo_evolution_display.py
```
Interactive visual testing of evolution chains:
- Three-stage linear chains (Bulbasaur → Ivysaur → Venusaur)
- Branching evolutions (Eevee → 8 eeveelutions)
- Single-stage Pokémon (Ditto, no evolutions)
- Evolution requirement display (level, stone, trade)
- Real-time rendering with database integration

**demo_tab_system.py** - Tab Navigation Demo
```bash
python demos/demo_tab_system.py
```
Tests tab-based detail view navigation:
- Tab switching with L/R buttons
- Info/Stats/Evolution tab content
- Tab indicator highlighting
- Pokémon navigation while preserving tab state

### Layout & Spacing Demos

**demo_tab_layout_fixes.py** - Tab Layout Testing
```bash
python demos/demo_tab_layout_fixes.py
```
Story 5.7 implementation - validates tab layout fixes:
- Proper vertical spacing between panels
- Tab indicator positioning
- Content alignment across tabs
- Resolution testing (480x320, 800x480)

**demo_stats_tab_spacing.py** - Stats Panel Spacing
```bash
python demos/demo_stats_tab_spacing.py
```
Tests stat bar and type badge spacing:
- Visual progress bars with proper gaps
- Type badge alignment
- Physical measurements display
- Panel boundary validation

**demo_layout_measurement.py** - Layout Measurement Tool
```bash
python demos/demo_layout_measurement.py
```
Diagnostic tool for measuring vertical space usage:
- Component height calculations
- Available space reporting
- Layout debugging assistance
- Helps identify spacing issues

**demo_description_display.py** - Description Text Demo
```bash
python demos/demo_description_display.py
```
Tests Pokédex description text rendering:
- Multi-line text wrapping
- Font rendering quality
- Description panel layout
- Text color and styling

## 🔧 Requirements

All demos require:
- Initialized database with Pokémon data (`python src/data/manage_db.py init`)
- Seeded Gen 1-3 data (`python src/data/manage_db.py seed --gen 1-3`)
- pygame and other dependencies installed

## 📸 Screenshot Generation

To generate fresh documentation screenshots:

```bash
# Activate virtual environment
source venv/bin/activate

# Generate all reference screenshots
python demos/demo_screenshot.py

# View generated screenshots
open screenshots/index.html  # macOS
xdg-open screenshots/index.html  # Linux
```

Screenshots are automatically organized by feature and saved with descriptive names.

## 🧪 Usage in Development

### Visual Testing
Run demos after UI changes to verify:
- Layout consistency across resolutions
- Color scheme adherence (holographic blue theme)
- Font rendering and readability
- Component positioning and spacing

### Story Validation
Story files reference specific demos for acceptance criteria validation:
- Story 5.1-5.6: `demo_evolution_display.py`
- Story 5.7: `demo_tab_layout_fixes.py`, `demo_tab_system.py`
- Story 3.1-3.8: `demo_screenshot.py`

### Performance Benchmarking
Some demos include basic performance metrics:
- Frame render time
- Component initialization time
- Database query duration

For comprehensive performance profiling, use `tools/profile_performance.py` instead.

## 📝 Notes

- Demos run in a pygame window and may require X11/display server on headless systems
- Press ESC to exit most interactive demos
- Demo scripts are NOT included in production builds
- Screenshots are git-ignored by default (large binary files)

## 🔗 Related Documentation

- [UI Guide](../docs/ui_guide.md) - Complete UI component documentation
- [Story Files](../docs/sprint-artifacts/) - Implementation stories referencing demos
- [Tools README](../tools/README.md) - Performance profiling tools
- [Examples](../examples/) - Code examples for specific features

---

For questions or issues with demos, see story files in `docs/sprint-artifacts/` or check git history for demo script changes.

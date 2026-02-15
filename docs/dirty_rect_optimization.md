# Dirty Rectangle Rendering Optimization

## Overview

This document describes the dirty rectangle rendering optimization implemented in ShokeDex to improve frame rendering performance on Raspberry Pi hardware.

## Problem

The original implementation used `pygame.display.flip()` to update the entire display every frame, even when only small portions of the screen changed. This is inefficient, especially on resource-constrained Raspberry Pi hardware.

**Example**: When navigating the Pokémon grid, only the selection highlight changes, but the entire 480x320 display was being redrawn.

## Solution

Implemented a dirty rectangle tracking system that:
1. Tracks which screen regions changed (dirty rects)
2. Only updates those specific regions with `pygame.display.update(dirty_rects)`
3. Caches static UI elements to avoid redundant rendering

### Components

#### 1. DirtyRectManager (`src/ui/dirty_rect_manager.py`)
Manages dirty rectangles and display updates:
- `mark_dirty(rect)` - Mark a region as needing redraw
- `mark_full_update()` - Force full screen update (for transitions)
- `update_display()` - Apply dirty rect updates to display

#### 2. StaticCache (`src/ui/static_cache.py`)
Caches pre-rendered static surfaces:
- `StaticCache` - Cache unchanging UI elements (backgrounds, frames)
- `FontCache` - Reuse font instances (creation is expensive)
- `TextCache` - Cache rendered text surfaces with LRU eviction

#### 3. Screen Base Class Updates (`src/ui/screen.py`)
- Added `needs_full_render()` flag for transitions
- Changed `render()` signature to return `List[pygame.Rect]`
- Screens now track and return their dirty regions

#### 4. ScreenManager Integration (`src/ui/screen_manager.py`)
- Integrated `DirtyRectManager`
- Collects dirty rects from screen rendering
- Calls `update_display()` instead of `flip()`

#### 5. Main Loop Update (`src/main.py`)
- Changed from `pygame.display.flip()` to `screen_manager.update_display()`

## Usage

### Basic Dirty Rect Pattern

```python
def render(self, surface: pygame.Surface) -> List[pygame.Rect]:
    dirty_rects = []
    
    # Render changed elements
    rect = surface.blit(sprite, position)
    dirty_rects.append(rect)
    
    return dirty_rects
```

### Static Element Caching

```python
from src.ui.static_cache import StaticCache

class MyScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.static_cache = StaticCache()
        
        # Register static elements
        self.static_cache.register("background", self._render_background)
    
    def _render_background(self):
        surface = pygame.Surface((480, 320))
        # ... render complex background once
        return surface
    
    def render(self, surface: pygame.Surface):
        # Use cached background
        bg = self.static_cache.get("background")
        surface.blit(bg, (0, 0))
        # ... render dynamic content
        return [...]
```

### Font and Text Caching

```python
from src.ui.static_cache import FontCache, TextCache

class MyScreen(Screen):
    def __init__(self, screen_manager):
        super().__init__(screen_manager)
        self.text_cache = TextCache(max_size=100)
        
        # Use cached fonts
        self.font = FontCache.get_font(None, 24)
    
    def render(self, surface: pygame.Surface):
        # Cache common text
        text_surface = self.text_cache.get_text(
            "Press START",
            self.font,
            (255, 255, 255)
        )
        surface.blit(text_surface, (10, 10))
        return [...]
```

## Current Implementation Status

### ✅ Complete
- Dirty rect infrastructure in place
- All screens updated to return dirty rect lists
- Static caching utilities available
- Font caching ready
- Text caching with LRU eviction

### 🔄 In Progress (Backward Compatible)
All screens currently return empty lists, which triggers full screen updates via the dirty rect manager. This maintains current behavior while enabling gradual optimization.

### 📋 Future Optimizations
Individual screens can be optimized by:
1. Tracking which elements changed
2. Returning specific dirty rects instead of empty list
3. Using static cache for unchanging elements
4. Pre-rendering common text strings

## Performance Benefits

### Expected Improvements
- **Small updates**: 50-70% reduction in update time when only small regions change
- **Static screens**: 80-90% reduction when most content is cached
- **Memory**: Minimal overhead (dirty rect list + cached surfaces)

### Measurement

Use `tools/test_dirty_rect_performance.py` to benchmark:
```bash
python tools/test_dirty_rect_performance.py
```

Run performance tests to verify impact:
```bash
export SDL_VIDEODRIVER=dummy
pytest -m performance -v
```

## Testing

Unit tests in `tests/test_dirty_rect_and_cache.py` cover:
- Dirty rect manager functionality
- Static cache behavior
- Font cache reuse
- Text cache LRU eviction

## Design Decisions

### Why return empty list initially?
Backward compatibility - screens work unchanged while allowing gradual per-screen optimization.

### Why not automatically track dirty rects?
Screens know best what changed. Automatic tracking would require expensive screen diffing.

### Why separate FontCache vs TextCache?
- **FontCache**: Fonts are expensive to create, never evicted
- **TextCache**: Rendered text surfaces consume memory, need LRU eviction

### Why mark_full_render flag?
Screen transitions, tab changes, and initial renders need full updates. This flag ensures proper display refresh.

## Migration Guide

To optimize a screen:

1. **Identify static elements**
   ```python
   # Register in __init__
   self.static_cache.register("background", self._render_background)
   ```

2. **Track dynamic changes**
   ```python
   dirty_rects = []
   if self.selection_changed:
       rect = self._render_selection(surface)
       dirty_rects.append(rect)
   ```

3. **Return dirty rects**
   ```python
   return dirty_rects  # Instead of return []
   ```

4. **Test thoroughly**
   - Verify no visual glitches
   - Check all transitions work
   - Measure performance improvement

## Troubleshooting

### Display not updating?
- Check screen is returning dirty rects
- Verify rects have non-zero width/height
- Try `mark_full_render()` to force full update

### Visual artifacts?
- Ensure static background is rendered first
- Check dirty rects fully cover changed area
- Verify Surface.convert_alpha() is used correctly

### No performance gain?
- Dummy video driver has minimal overhead
- Test on actual Pi hardware
- Check dirty rects aren't too large (defeats optimization)

## References

- pygame display documentation: https://www.pygame.org/docs/ref/display.html
- Dirty rectangle optimization: https://en.wikipedia.org/wiki/Dirty_rectangle
- ShokeDex performance targets: `docs/pi_optimization_guide.md`

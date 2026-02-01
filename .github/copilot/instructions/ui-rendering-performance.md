# UI and Rendering Performance Guide

## Quick Context
ShokeDex uses pygame to render Pokédex screens at 480x320 or 800x480 resolution on small LCD displays. Target is 30 FPS on Pi 3B+ (33.33ms frame budget) or 60 FPS on Pi 4 (16.67ms budget). Any frame taking longer causes visible stuttering.

## Performance Measurement

### Frame Time Profiling
```bash
# Run with performance monitor enabled
SDL_VIDEODRIVER=dummy python tools/profile_performance.py

# Check output for:
# - Average frame time
# - P95/P99 frame time (should be < 33ms for 30 FPS)
# - Frames dropped
```

### Per-Screen Profiling
```python
import time
import pygame

# Inside screen render loop:
frame_start = time.perf_counter()

# ... your rendering code ...

frame_time_ms = (time.perf_counter() - frame_start) * 1000
if frame_time_ms > 33.33:
    print(f"SLOW FRAME: {frame_time_ms:.2f}ms")
```

### Hotspot Identification
```bash
# Profile with cProfile to find slow rendering functions
python -m cProfile -o render.prof src/main.py
python -m pstats render.prof
# In pstats shell: sort cumtime -> stats 20
```

## Common Bottlenecks

### 1. Full Screen Redraws Every Frame
**Current:** `pygame.display.flip()` redraws entire screen  
**Issue:** Wastes CPU redrawing static elements (borders, backgrounds, badges)  
**Fix:** Use dirty rect updates with `pygame.display.update(rect_list)`

**Example:**
```python
# Instead of:
screen.blit(background, (0, 0))
screen.blit(sprite, (x, y))
pygame.display.flip()  # Redraws everything!

# Use:
dirty_rects = []
dirty_rects.append(screen.blit(sprite, (x, y)))
pygame.display.update(dirty_rects)  # Only redraws changed areas
```

### 2. Sprite Loading on Every Render
**Symptom:** Lag when navigating between Pokémon  
**Cause:** Loading sprites from disk during render loop  
**Fix:** Pre-load sprites in background or cache aggressively

### 3. Inefficient Surface Formats
**Issue:** Blitting incompatible surface formats causes conversion overhead  
**Fix:** Convert surfaces to display format once:
```python
sprite = pygame.image.load(path).convert_alpha()  # Not just .load()!
```

### 4. Text Rendering Every Frame
**Issue:** `font.render()` is expensive (bitmap generation + anti-aliasing)  
**Fix:** Cache rendered text surfaces:
```python
text_cache = {}
def get_text_surface(text, font):
    if text not in text_cache:
        text_cache[text] = font.render(text, True, COLOR)
    return text_cache[text]
```

## Optimization Techniques

### Dirty Rectangle Tracking
**Impact:** 2-5x frame rate improvement for mostly-static screens  
**Implementation:**
1. Identify static elements (backgrounds, UI chrome)
2. Render static elements once to separate surface
3. Track which areas change (sprite position, text updates)
4. Only update changed rectangles

### Sprite Cache with LRU Eviction
**Current:** Unbounded dictionary cache (memory leak risk)  
**Optimization:**
```python
from functools import lru_cache
from PIL import Image
import pygame

@lru_cache(maxsize=100)  # Keep 100 most recent sprites
def load_sprite_cached(path: str) -> pygame.Surface:
    img = Image.open(path)
    mode = img.mode
    size = img.size
    data = img.tobytes()
    surface = pygame.image.fromstring(data, size, mode).convert_alpha()
    return surface
```

### Pre-loading Adjacent Pokémon
**Strategy:** When viewing Pokémon #25, pre-load #24 and #26 in background  
**Impact:** Zero lag on L/R navigation  
**Implementation:** Use threading or async to load in background

### Static Element Layering
**Technique:** Render backgrounds/borders once, composite sprites on top  
```python
# One-time rendering:
background_layer = pygame.Surface((480, 320))
# ... draw background, borders, static text ...

# Per-frame rendering:
screen.blit(background_layer, (0, 0))  # Fast blit of pre-rendered layer
screen.blit(pokemon_sprite, (x, y))    # Only dynamic element
pygame.display.update()
```

## Testing Strategy

### Frame Rate Benchmarking
```bash
# Automated frame rate test
pytest -m performance tests/test_performance_mvp.py::test_frame_rate -v

# Expected results:
# - Pi 3B+ target: 30 FPS average, min 25 FPS
# - Pi 4 target: 60 FPS average, min 50 FPS
```

### Visual Regression Testing
After optimization:
1. Capture screenshots of each screen type
2. Compare with baseline screenshots (pixel-perfect diff)
3. Ensure no visual artifacts introduced

### User Journey Testing
Simulate real usage patterns:
- Navigate through 50 Pokémon in sequence (measure frame drops)
- Random jumps between distant IDs (cache miss simulation)
- Rapid button presses (input buffering stress test)

## Pi-Specific Considerations

### GPU Memory Sharing
Pi 3B+ shares 1GB RAM between CPU and GPU. Default GPU allocation: 64MB.  
**Optimization:** Increase GPU memory in `/boot/config.txt`:
```
gpu_mem=128  # For better graphics performance
```

### Display Driver Performance
**Hardware acceleration:** Use `SDL_VIDEODRIVER=rpi` for native framebuffer  
**Fallback:** `SDL_VIDEODRIVER=fbcon` or `SDL_VIDEODRIVER=x11`  
**CI/Testing:** `SDL_VIDEODRIVER=dummy` for headless environments

### LCD-Specific Timing
Some LCDs have refresh rate limitations (e.g., 30Hz max). Check your display specs before targeting 60 FPS.

## Quick Wins
1. ✅ Convert all loaded surfaces with `.convert_alpha()`
2. ✅ Cache rendered text surfaces (don't call `font.render()` per frame)
3. ✅ Implement LRU sprite cache with maxsize=100
4. ✅ Use dirty rect updates for static screens (Details screen)
5. ✅ Pre-load adjacent Pokémon sprites on navigation

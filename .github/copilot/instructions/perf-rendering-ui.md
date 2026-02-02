# Rendering and UI Performance Guide

Optimize pygame rendering for smooth 30 FPS on Raspberry Pi 3B+ and 60 FPS on Pi 4.

## Current Architecture

- **Framework**: pygame 2.5.0+
- **Target FPS**: 30 (Pi 3B+) or 60 (Pi 4)
- **Display**: Small LCDs (480x320 to 800x480)
- **Rendering**: Full screen flip every frame

## Performance Measurement

### Frame Time Analysis
```python
import time

frame_times = []
for _ in range(100):
    start = time.perf_counter()
    # Render frame
    screen.blit(background, (0, 0))
    screen.blit(pokemon_sprite, (100, 100))
    pygame.display.flip()
    frame_times.append((time.perf_counter() - start) * 1000)

avg_ms = sum(frame_times) / len(frame_times)
p95_ms = sorted(frame_times)[int(len(frame_times) * 0.95)]
print(f"Avg: {avg_ms:.2f}ms, P95: {p95_ms:.2f}ms")
```

### FPS Monitoring
Built into `PerformanceMonitor` class:
```python
monitor = PerformanceMonitor()
monitor.update()
fps = monitor.get_fps()
```

### Profile Rendering
```bash
python -m cProfile -s cumtime src/main.py
# Look for time spent in display.flip(), blit(), Surface creation
```

## Critical Optimizations

### 1. Dirty Rectangle Updates
**Problem**: Full screen flip wastes ~10-15ms
**Solution**: Update only changed regions

```python
# Track dirty rects
dirty_rects = []

# Draw changed elements
rect = screen.blit(sprite, pos)
dirty_rects.append(rect)

# Update only dirty areas
pygame.display.update(dirty_rects)
```

### 2. Static Surface Caching
**Problem**: Re-rendering unchanging elements every frame
**Solution**: Pre-render and cache

```python
class PokedexScreen:
    def __init__(self):
        # Cache static elements
        self.background = self._render_background()
        self.ui_frame = self._render_frame()
        
    def render(self, screen):
        # Just blit cached surfaces
        screen.blit(self.background, (0, 0))
        screen.blit(self.ui_frame, (0, 0))
        # Only render dynamic content
```

### 3. Surface Format Optimization
**Problem**: Blitting surfaces with incompatible formats is slow
**Solution**: Convert to display format

```python
# After loading
surface = surface.convert_alpha()  # For transparency
# or
surface = surface.convert()  # For opaque images
```

### 4. Reduce Overdraw
**Problem**: Drawing multiple overlapping layers
**Solution**: Only draw visible portions

```python
# Don't draw completely obscured elements
if element.is_visible() and not element.is_covered():
    screen.blit(element.surface, element.pos)
```

## Text Rendering

### Font Caching
**Problem**: Creating font objects is expensive
**Solution**: Cache font instances

```python
class FontCache:
    _fonts = {}
    
    @classmethod
    def get_font(cls, name, size):
        key = (name, size)
        if key not in cls._fonts:
            cls._fonts[key] = pygame.font.Font(name, size)
        return cls._fonts[key]
```

### Pre-rendered Text
**Problem**: Rendering text every frame is slow
**Solution**: Cache rendered text surfaces

```python
# Cache common strings
self.text_cache = {}

def get_text_surface(self, text, font, color):
    key = (text, font, color)
    if key not in self.text_cache:
        self.text_cache[key] = font.render(text, True, color)
    return self.text_cache[key]
```

## Testing Performance

### Automated Checks
```python
@pytest.mark.performance
def test_frame_time_target():
    """Verify frame time meets 30 FPS target (33ms)"""
    screen = pygame.display.set_mode((480, 320))
    
    frame_times = []
    for _ in range(100):
        start = time.perf_counter()
        # Simulate typical frame rendering
        screen.fill((0, 0, 0))
        # ... render typical screen content
        pygame.display.flip()
        frame_times.append((time.perf_counter() - start) * 1000)
    
    p95 = sorted(frame_times)[95]
    assert p95 < 33.0, f"P95 frame time {p95:.2f}ms exceeds 33ms"
```

### Visual Profiling
Use pygame's built-in tools:
```python
# Show FPS in development
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

# Each frame:
fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
screen.blit(fps_text, (10, 10))
```

## Raspberry Pi Specifics

### Headless Mode for CI
```bash
export SDL_VIDEODRIVER=dummy
```

### Performance Mode
Consider setting CPU governor on Pi:
```bash
# For consistent testing (prevents thermal throttling effects)
sudo cpufreq-set -g performance
```

## Common Pitfalls

- ❌ Creating new surfaces every frame
- ❌ Loading images during rendering (load in init)
- ❌ Using alpha blending when not needed
- ❌ Rendering off-screen elements
- ❌ Not converting surfaces to display format

## Target Metrics

- **Frame time P95**: <33ms (30 FPS) on Pi 3B+
- **Frame time P95**: <16ms (60 FPS) on Pi 4
- **Static element render**: <1ms (from cache)
- **Display flip/update**: <10ms
- **Memory per screen**: <20MB

## Quick Wins

1. Add surface format conversion (`.convert_alpha()`)
2. Cache static backgrounds and UI frames
3. Cache font instances
4. Implement dirty rect updates
5. Pre-render common text strings

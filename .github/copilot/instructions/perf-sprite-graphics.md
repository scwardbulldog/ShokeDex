# Sprite and Graphics Performance Guide

Optimize sprite loading, caching, and rendering for smooth performance on Raspberry Pi.

## Current Implementation

- **Sprite cache**: Simple dictionary in `src/ui/sprite_loader.py`
- **Pre-processed sizes**: 32x32 thumbnails, 96x96 detail views
- **Format**: PNG with alpha channel
- **Storage**: Local filesystem in `assets/sprites/`

## Measurement Strategies

### Sprite Load Timing
```python
import time
start = time.perf_counter()
sprite = sprite_loader.get_sprite(pokemon_id, size='detail')
load_time = (time.perf_counter() - start) * 1000
print(f"Sprite load: {load_time:.2f}ms")
```

### Cache Performance
```python
# Add to SpriteLoader class
self.cache_hits = 0
self.cache_misses = 0

def get_cache_hit_rate(self):
    total = self.cache_hits + self.cache_misses
    return (self.cache_hits / total * 100) if total > 0 else 0
```

### Memory Tracking
```bash
# Run with memory profiling
python -m memory_profiler tools/test_long_session_stability.py
```

## Critical Optimizations

### 1. LRU Cache with Size Limit
**Problem**: Unbounded cache grows indefinitely
**Solution**: Use collections.OrderedDict or functools.lru_cache

```python
from functools import lru_cache
from PIL import Image

@lru_cache(maxsize=128)  # Keep last 128 sprites
def load_sprite_cached(filepath):
    return Image.open(filepath).convert('RGBA')
```

### 2. Surface Format Conversion
**Problem**: Pygame blitting unoptimized surfaces is slow
**Solution**: Use convert() or convert_alpha()

```python
# Bad: Direct load
sprite = pygame.image.load(path)

# Good: Optimized format
sprite = pygame.image.load(path).convert_alpha()
```

### 3. Pre-loading Adjacent Pokémon
**Problem**: Navigation lag when scrolling
**Solution**: Background pre-load next/previous sprites

```python
def preload_adjacent(current_id):
    # Load current + next 2 + previous 2
    for offset in range(-2, 3):
        neighbor_id = current_id + offset
        if 1 <= neighbor_id <= 386:
            sprite_loader.get_sprite(neighbor_id, 'thumb')
```

## Rendering Optimizations

### Dirty Rect Updates
**Problem**: Full screen flip wastes CPU
**Solution**: Only update changed regions

```python
# Bad: Full flip
pygame.display.flip()

# Good: Dirty rect update
pygame.display.update(dirty_rects)
```

### Static Element Caching
Cache UI elements that don't change:
```python
# Cache background, borders, badges
self.background_surface = self._render_background()
# Reuse on every frame instead of re-rendering
```

## Testing Approach

### Performance Test Template
```python
@pytest.mark.performance
def test_sprite_loading_performance():
    """Verify sprite loading meets target (<50ms P99)"""
    times = []
    for i in range(1, 152):  # Gen 1
        start = time.perf_counter()
        sprite_loader.get_sprite(i, 'detail')
        times.append((time.perf_counter() - start) * 1000)
    
    p99 = sorted(times)[int(len(times) * 0.99)]
    assert p99 < 50.0, f"P99 sprite load {p99:.2f}ms exceeds 50ms"
```

### Memory Leak Detection
```python
def test_cache_memory_stability():
    """Ensure cache doesn't grow unbounded"""
    import tracemalloc
    tracemalloc.start()
    
    # Simulate heavy usage
    for _ in range(10):
        for i in range(1, 387):
            sprite_loader.get_sprite(i, 'thumb')
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Should stabilize under 50MB for sprites
    assert peak < 50 * 1024 * 1024
```

## Raspberry Pi Specific

### Headless Testing
Always set environment variable for CI:
```bash
export SDL_VIDEODRIVER=dummy
```

### Hardware Acceleration
Check if available on target Pi:
```python
# May improve performance on Pi 4
os.environ['SDL_VIDEODRIVER'] = 'kmsdrm'  # Direct rendering
```

## Target Metrics

- **Cache hit rate**: >80% during navigation
- **Sprite load P99**: <50ms
- **Memory usage**: <50MB for sprite cache
- **Frame time impact**: <5ms per sprite blit

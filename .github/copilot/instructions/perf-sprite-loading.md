# Performance Engineering Guide: Sprite Loading & Rendering

**Context:** ShokeDex displays Pokémon sprites (32x32 thumbnails, 96x96 detail views). Sprite loading/caching directly impacts navigation smoothness.

## Quick Performance Measurement

**Profile sprite loading:**
```bash
# Run sprite-focused performance tests
SDL_VIDEODRIVER=dummy pytest tests/test_sprite_loader.py -v --benchmark

# Measure load time
python -c "
import time
from src.ui.sprite_loader import SpriteLoader
sl = SpriteLoader()
start = time.perf_counter()
sprite = sl.load_thumb(25)
print(f'Load time: {(time.perf_counter()-start)*1000:.2f}ms')
"
```

**Monitor cache behavior:**
```python
# Add to SpriteLoader class for debugging
def cache_stats(self):
    total = len(self._thumb_cache) + len(self._detail_cache)
    print(f"Cache: {len(self._thumb_cache)} thumbs, {len(self._detail_cache)} details = {total} total")
```

## Key Optimization Targets

**1. Bounded Cache with LRU (CRITICAL)**
- Current: Unbounded dict cache (memory leak risk on extended use)
- Target: LRU cache with size limits (e.g., 50 thumbs, 20 detail sprites)
- Expected gain: Prevent OOM, maintain 95%+ hit rate for navigation

**2. Pre-loading Adjacent Sprites**
- Anticipate L/R navigation by pre-loading ±1-2 Pokémon
- Background loading during idle frames
- Reduces perceived latency from 20-50ms to <5ms

**3. Surface Format Optimization**
```python
# Convert surfaces to display format for faster blitting
sprite = pygame.image.load(path)
sprite = sprite.convert_alpha()  # 2-3x faster blitting
```

**4. Progressive Loading**
- For detail view: show thumbnail, then swap to high-res when loaded
- Maintains 30 FPS even if high-res load takes 50ms

## Measurement Strategy

**Synthetic benchmark:**
```python
import time
from src.ui.sprite_loader import SpriteLoader

sl = SpriteLoader()
times = []
for i in range(1, 152):  # Gen 1
    start = time.perf_counter()
    sl.load_thumb(i)
    times.append(time.perf_counter() - start)

print(f"P50: {sorted(times)[75]*1000:.1f}ms")
print(f"P95: {sorted(times)[143]*1000:.1f}ms")
print(f"P99: {sorted(times)[149]*1000:.1f}ms")
```

**Real-world test:**
- Navigate through Pokédex (ID 1→151) using arrow keys
- Measure frame time and sprite load latency with `PerformanceMonitor`
- Target: Frame time P95 < 33ms (30 FPS), sprite load P99 < 50ms

## Common Pitfalls

- **Premature eviction:** Too-small cache causes thrashing (re-loading same sprites)
- **Blocking loads:** Loading on main thread blocks rendering; consider async
- **Forgotten alpha:** Missing `convert_alpha()` causes 2-3x slower blits
- **Wrong size cached:** Cache pre-scaled sprites (32x32, 96x96), not originals

## Success Metrics

- Cache hit rate > 85% during sequential navigation
- Cache hit rate > 70% during random jumps
- Memory: ~50 sprites × 10KB/sprite = ~500KB overhead (acceptable)
- P99 sprite load latency < 50ms (cold) or < 5ms (cached)

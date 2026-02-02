# Performance Engineering Guide: Memory & Resource Management

**Context:** Raspberry Pi 3B+ has 1GB RAM. ShokeDex targets <150MB usage to leave headroom for OS. Extended sessions risk memory leaks.

## Quick Performance Measurement

**Monitor memory usage:**
```bash
# Real-time monitoring
python tools/profile_performance.py  # includes memory tracking

# Or manually
python -c "
import psutil, time
from src.main import main
proc = psutil.Process()
print(f'Start: {proc.memory_info().rss / 1024**2:.1f} MB')
# ... run application ...
time.sleep(60)
print(f'After 60s: {proc.memory_info().rss / 1024**2:.1f} MB')
"
```

**Memory profiling:**
```bash
# Install memory_profiler
pip install memory_profiler

# Profile function
python -m memory_profiler src/ui/sprite_loader.py

# Or use decorator
@profile
def load_sprites():
    # ... code ...
```

## Key Optimization Targets

**1. Sprite Cache Size Limits (CRITICAL)**
- Current: Unbounded dict caches (thumb + detail)
- Risk: 386 Pokémon × 2 sprites × 10KB = ~8MB, but can grow with variants
- Target: LRU cache with limits (50 thumbs + 20 detail = ~700KB)

**2. Surface Format Optimization**
```python
# 32-bit RGBA (default): 4 bytes/pixel
# 24-bit RGB: 3 bytes/pixel (25% savings, no alpha)
# 8-bit indexed: 1 byte/pixel (75% savings, palette-based)

# For static sprites, convert to display format
sprite = sprite.convert()  # or convert_alpha() if transparency needed
# Reduces memory AND improves blit speed
```

**3. Detect Memory Leaks**
```python
# Add to test suite
import gc, weakref

def test_no_sprite_cache_leak():
    loader = SpriteLoader()
    initial_count = len(gc.get_objects())
    
    # Load sprites
    for i in range(1, 152):
        loader.load_thumb(i)
    
    # Clear cache
    loader._thumb_cache.clear()
    gc.collect()
    
    final_count = len(gc.get_objects())
    assert final_count <= initial_count + 10, "Potential memory leak detected"
```

**4. Lazy Loading**
- Don't load all data at startup
- Load sprites/stats on-demand
- Implement progressive disclosure

## Measurement Strategy

**Long-running session test:**
```bash
# Run stability test
python tools/test_long_session_stability.py
# Monitors memory over 1-hour session with navigation
```

**Memory snapshot comparison:**
```python
import tracemalloc

tracemalloc.start()
snapshot1 = tracemalloc.take_snapshot()

# ... perform operations ...

snapshot2 = tracemalloc.take_snapshot()
top_stats = snapshot2.compare_to(snapshot1, 'lineno')

for stat in top_stats[:10]:
    print(stat)
```

**Baseline target:** Run for 1 hour, navigate 100+ Pokémon
- Memory should stabilize (plateau)
- No steady growth (indicates leak)
- Peak < 150MB on Pi 3B+, < 200MB on Pi 4

## Common Pitfalls

- **Circular references:** Python GC handles most, but pygame surfaces can leak
- **Event accumulation:** `pygame.event.get()` must be called regularly
- **Cached errors:** Exception objects in cache hold references
- **Surface copies:** `sprite.copy()` doubles memory; use references where possible

## Memory Budget (Pi 3B+ = 1GB total)

- OS + background: 400MB
- Python runtime: 50MB
- pygame: 50MB
- ShokeDex code: 20MB
- **Available for caches/data: 480MB**
- **Target usage: <150MB (70% headroom)**

Breakdown:
- Database connection: 10MB
- Sprite cache (bounded): 5MB
- UI surfaces (static): 10MB
- Font cache: 2MB
- Working memory: 123MB

## Success Metrics

- Startup memory < 100MB
- Stable memory after 1 hour < 150MB (Pi 3B+) or < 200MB (Pi 4)
- No memory growth rate > 1MB/hour
- Cache eviction happens gracefully (no performance cliff)
- No crashes on extended sessions (4+ hours)

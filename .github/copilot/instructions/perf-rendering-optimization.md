# Performance Engineering Guide: Rendering Optimization

**Context:** ShokeDex renders at 30 FPS on Pi 3B+. Every frame must complete in <33ms. Rendering is CPU-bound on Pi.

## Quick Performance Measurement

**Frame time profiling:**
```bash
# Use built-in performance monitor
python tools/profile_performance.py

# Or during testing
SDL_VIDEODRIVER=dummy pytest -m performance -v
```

**Per-screen profiling:**
```python
# Add to screen render() method
import time
start = time.perf_counter()
# ... render code ...
frame_ms = (time.perf_counter() - start) * 1000
if frame_ms > 30:
    print(f"Slow frame: {frame_ms:.1f}ms")
```

## Key Optimization Targets

**1. Dirty Rectangle Updates (HIGHEST IMPACT)**
- Current: Full screen flip every frame via `pygame.display.flip()`
- Target: Update only changed regions with `pygame.display.update(rects)`
- Expected gain: 2-3x reduction in frame time for static screens

Example:
```python
# Instead of:
pygame.display.flip()

# Use:
dirty_rects = []
if pokemon_changed:
    dirty_rects.append(sprite_rect)
if stat_changed:
    dirty_rects.append(stats_panel_rect)
pygame.display.update(dirty_rects)
```

**2. Cache Static UI Elements**
- Render backgrounds, borders, badges once; reuse surfaces
- Detail screen background: render once, blit repeatedly
- Type badges: pre-render all 17 types at startup

**3. Reduce Overdraw**
- Layer compositing: minimize transparent overlays
- Clip regions to visible area
- Profile with `pygame.display.set_caption()` showing FPS

**4. Font Rendering**
```python
# Cache rendered text surfaces
text_cache = {}
def render_text(font, text, color):
    key = (text, color)
    if key not in text_cache:
        text_cache[key] = font.render(text, True, color)
    return text_cache[key]
```

## Measurement Strategy

**Baseline:**
1. Run detail screen for 60 seconds, log frame times
2. Identify P95, P99, max frame time
3. Note CPU% via `PerformanceMonitor`

**Synthetic stress test:**
```python
# Rapidly switch between screens
for _ in range(100):
    state_manager.navigate_to(DETAIL_SCREEN, pokemon_id=random.randint(1,151))
    # Measure frame time during transition
```

**Target metrics:**
- P95 frame time < 30ms (allows 3ms headroom at 30 FPS)
- P99 frame time < 40ms (tolerable occasional spikes)
- Max frame time < 100ms (avoid perceptible stutter)

## Common Pitfalls

- **Over-caching:** Too many cached surfaces = memory pressure
- **Dirty rect complexity:** Tracking rects can add overhead; profile first
- **Alpha blending cost:** Multiple alpha layers stack up; use sparingly
- **Font anti-aliasing:** Beautiful but slow; consider disabling on Pi 3B+

## Render Budget Breakdown (30 FPS = 33ms)

- Event processing: 2ms
- State updates: 3ms
- **Rendering: 25ms** ← optimization target
- Display flip: 3ms

Focus optimizations on the 25ms render budget.

## Success Metrics

- Frame time P95 < 30ms (smooth 30 FPS)
- CPU usage < 70% during rendering (headroom for other tasks)
- Memory overhead from caching < 10MB
- No visible tearing or artifacts from dirty rect updates

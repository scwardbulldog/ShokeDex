# Memory Profiling Guide

## Story 1.7: Memory Leak Detection (Task 5)

This guide explains how to perform memory profiling and leak detection for ShokeDex.

## Quick Start

### 1. Install Memory Profiler

Already included in `requirements.txt`:

```bash
pip install memory_profiler
```

### 2. Add @profile Decorator

Add the `@profile` decorator to methods you want to analyze:

```python
# In src/ui/home_screen.py

@profile
def update(self, delta_time: float):
    """Frame update with memory profiling."""
    # ... existing code ...
```

**Key methods to profile:**
- `HomeScreen.update()` - Called every frame
- `HomeScreen.render()` - Rendering operations
- `HomeScreen.handle_input()` - Input processing
- `sprite_loader.load_thumb()` - Sprite loading

### 3. Run Memory Profiler

```bash
# Profile during normal operation
mprof run python src/main.py

# View memory usage over time
mprof plot

# Clean profile data
mprof clean
```

## Stress Testing

### AC #5 Requirements

- **Duration:** 30+ minutes of operation
- **Actions:** 100+ generation switches, 500+ scrolls
- **Memory Growth:** < 50MB increase
- **Sprite Cache:** Max 50 sprites (verified by LRU implementation)
- **Detection:** No unbounded growth in Python memory profiler

### Automated Stress Test

The `test_memory_stability_during_navigation` test in `tests/test_performance_mvp.py` performs a shorter stress test:

```bash
pytest tests/test_performance_mvp.py::TestMemoryStability::test_memory_stability_during_navigation -v
```

This simulates:
- 100 generation switches
- 500 scroll operations (5 per generation switch)
- Verifies memory increase < 5MB (proportional to shorter duration)

### Manual Stress Test

For full 30-minute validation:

1. **Start Profiling:**
   ```bash
   mprof run --interval 1.0 python src/main.py
   ```

2. **Perform Actions:**
   - Navigate continuously for 30 minutes
   - Mix generation switches (L/R buttons)
   - Scroll through Pokémon (Up/Down)
   - Hold-to-scroll for fast traversal
   - Return to previously viewed Pokémon

3. **Check Results:**
   ```bash
   mprof plot
   ```
   
   Look for:
   - **Flat line after initial ramp:** Memory stabilizes after cache fills
   - **No upward trend:** Memory doesn't continuously grow
   - **Periodic spikes:** Garbage collection is normal
   - **Total increase < 50MB:** From baseline to 30-minute mark

## What to Look For

### Normal Memory Patterns

✅ **Initial Ramp (0-5 minutes):**
- Memory increases as sprite cache fills
- Database loaded into memory
- Pygame surfaces allocated
- **Expected increase:** 20-30MB

✅ **Stable Plateau (5-30 minutes):**
- Memory stays relatively flat
- Small oscillations from GC
- No continuous upward trend
- **Expected variation:** ±5MB

✅ **Sprite Cache LRU:**
- Cache size bounded to 50 sprites
- Old sprites evicted automatically
- Verified by `get_cache_stats()`

### Memory Leak Indicators

❌ **Continuous Growth:**
- Memory steadily increases over time
- No plateau after initial ramp
- Exceeds 50MB increase

❌ **Unbounded Lists:**
- `pokemon_list` keeps growing
- Event queues not cleared
- Cache doesn't evict old items

❌ **Circular References:**
- Objects not garbage collected
- Parent-child reference cycles
- Event handlers not unregistered

## Common Leak Sources (and Fixes)

### 1. Sprite Cache (FIXED ✅)

**Problem:** Unbounded dictionary cache
```python
_CACHE: Dict[str, object] = {}  # Grows forever
```

**Solution:** LRU cache with max size
```python
_CACHE: OrderedDict[str, object] = OrderedDict()
_CACHE_MAX_SIZE = 50

def _evict_lru_if_needed():
    while len(_CACHE) > _CACHE_MAX_SIZE:
        _CACHE.popitem(last=False)
```

### 2. Event Listeners

**Problem:** Event handlers not unregistered
```python
pygame.event.post()  # Creates events
# Never cleared from queue
```

**Solution:** Clear event queue in `Screen.on_exit()`
```python
def on_exit(self):
    pygame.event.clear()
```

### 3. Circular References

**Problem:** Parent-child reference cycles
```python
class Parent:
    def __init__(self):
        self.child = Child(self)  # Child holds reference to parent

class Child:
    def __init__(self, parent):
        self.parent = parent  # Circular reference
```

**Solution:** Use weak references or explicit cleanup
```python
import weakref

class Child:
    def __init__(self, parent):
        self.parent = weakref.ref(parent)  # Weak reference
```

### 4. Pygame Surfaces

**Problem:** Creating new surfaces every frame
```python
def render(self):
    temp_surface = pygame.Surface((100, 100))  # New every frame!
    # ... use surface ...
```

**Solution:** Reuse surfaces or ensure proper cleanup
```python
def __init__(self):
    self.temp_surface = pygame.Surface((100, 100))  # Create once

def render(self):
    self.temp_surface.fill((0, 0, 0))  # Reuse
```

## Line-by-Line Profiling (Advanced)

For detailed analysis of specific functions:

```bash
# Install line_profiler
pip install line_profiler

# Add @profile decorator to target function
# Run with kernprof
kernprof -l -v src/main.py

# View results
python -m line_profiler script.py.lprof
```

## Continuous Monitoring

The `PerformanceMonitor` class tracks memory in real-time:

```python
from src.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# Each frame
monitor.record_cpu_memory()

# Check stats
stats = monitor.get_stats()
print(f"Memory: {stats['memory_mb']:.1f} MB")
print(f"Memory avg: {stats['memory_avg_mb']:.1f} MB")
```

## Raspberry Pi Considerations

Memory constraints are tighter on Pi 3B+ (1GB RAM total):

- **OS + Services:** ~400-500MB
- **ShokeDex Target:** < 300MB
- **Headroom:** ~200-300MB for other processes

**Pi-Specific Testing:**
```bash
# Monitor memory on Pi
watch -n 1 'free -m'

# Check process memory
ps aux | grep python

# Run profiler on Pi
mprof run --interval 2.0 python src/main.py
```

## Success Criteria (AC #5)

✅ **Memory Stability:** No continuous growth over 30+ minutes
✅ **Sprite Cache:** Bounded to 50 sprites (LRU eviction working)
✅ **Memory Increase:** < 50MB from baseline to 30-minute mark
✅ **No Unbounded Lists:** All collections have defined limits
✅ **Automated Tests:** `test_memory_stability_during_navigation` passes

## References

- Story 1.7: Performance Optimization and 3-Press Navigation Rule
- AC #5: Memory Stability
- Architecture: Sprite cache max 50 items
- NFR-P4: Memory Efficiency (Raspberry Pi constraints)

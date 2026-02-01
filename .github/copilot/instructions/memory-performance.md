# Memory Performance and Profiling Guide

## Quick Context
Raspberry Pi 3B+ has 1GB RAM shared between CPU and GPU (typically 64-128MB for GPU, leaving 872-936MB for OS and applications). ShokeDex targets <150MB usage on Pi 3B+ and <200MB on Pi 4. Exceeding these limits causes swapping to SD card, which is 100-1000x slower than RAM.

## Performance Measurement

### Real-Time Memory Monitoring
```bash
# Install psutil (already in requirements.txt)
# Monitor memory usage during session:
python -c "
from src.ui.performance_monitor import PerformanceMonitor
import time

monitor = PerformanceMonitor()
for _ in range(60):  # 60 second test
    stats = monitor.get_stats()
    print(f\"Memory: {stats['memory_mb']:.1f}MB\")
    time.sleep(1)
"
```

### Memory Profiling with memory_profiler
```bash
# Install memory_profiler (not in requirements by default)
pip install memory-profiler

# Profile specific function:
python -m memory_profiler src/ui/sprite_loader.py

# Line-by-line memory usage:
@profile
def load_all_sprites():
    # ... code here ...
```

### Process Memory Breakdown
```bash
# On Raspberry Pi or Linux:
ps aux | grep python
# Check RSS (Resident Set Size) column

# Detailed breakdown:
cat /proc/$(pgrep -f 'python.*main.py')/status | grep -E 'VmRSS|VmSize|VmSwap'
```

## Common Bottlenecks

### 1. Unbounded Sprite Cache
**Symptom:** Memory grows continuously during navigation  
**Cause:** `sprite_cache` dictionary never evicts entries  
**Fix:** Implement LRU cache with size limit (see implementation below)

### 2. Large PIL Image Objects
**Issue:** PIL Images kept in memory alongside pygame Surfaces (double memory)  
**Fix:** Convert to pygame Surface immediately, discard PIL object:
```python
from PIL import Image
import pygame

img = Image.open(path)
surface = pygame.image.fromstring(img.tobytes(), img.size, img.mode).convert_alpha()
img.close()  # Release PIL object immediately
del img
```

### 3. Duplicate Surface Storage
**Pattern:** Same sprite loaded multiple times in different formats  
**Fix:** Centralize sprite loading with single cache

### 4. Retained Event History
**Issue:** pygame event queue or custom event history growing unbounded  
**Fix:** Clear event queue regularly, limit history size

## Optimization Techniques

### LRU Cache Implementation
```python
from collections import OrderedDict
from typing import Optional
import pygame

class LRUCache:
    def __init__(self, maxsize: int = 100):
        self.cache = OrderedDict()
        self.maxsize = maxsize
    
    def get(self, key: str) -> Optional[pygame.Surface]:
        if key in self.cache:
            self.cache.move_to_end(key)  # Mark as recently used
            return self.cache[key]
        return None
    
    def put(self, key: str, value: pygame.Surface):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            if len(self.cache) >= self.maxsize:
                # Evict oldest (least recently used)
                evicted_key, evicted_surface = self.cache.popitem(last=False)
                del evicted_surface  # Explicit cleanup
        self.cache[key] = value

# Usage:
sprite_cache = LRUCache(maxsize=100)
```

### Memory-Efficient Surface Formats
```python
# For sprites without transparency (solid backgrounds):
surface = image.convert()  # Uses display's native format (faster, less memory)

# For sprites with transparency:
surface = image.convert_alpha()  # Preserves alpha channel

# Never store as:
surface = pygame.image.load(path)  # Unconverted, inefficient!
```

### Lazy Loading Pattern
**Principle:** Only load data when actually needed  
**Example:**
```python
class PokemonData:
    def __init__(self, pokemon_id):
        self.id = pokemon_id
        self._sprite = None  # Not loaded yet
    
    @property
    def sprite(self):
        if self._sprite is None:
            self._sprite = load_sprite(self.id)  # Load on first access
        return self._sprite
```

### Cache Warming vs Cold Starts
**Tradeoff:** Load sprites at startup (slow start, fast navigation) vs load on demand (fast start, occasional lag)  
**Recommendation:** Hybrid approach - pre-load first 10 Pokémon, lazy-load rest

## Testing Strategy

### Memory Leak Detection
```python
# Test: Navigate through 386 Pokémon, memory should stabilize
import tracemalloc
tracemalloc.start()

# ... run navigation loop ...

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:10]:
    print(stat)
```

### Long-Session Stability Test
```bash
# Run for 1 hour, monitor memory growth
python tools/test_long_session_stability.py

# Expected: Memory stabilizes after initial cache filling
# Red flag: Continuous linear growth = memory leak
```

### Memory Regression Testing
```bash
# Add to performance test suite
pytest -m performance tests/test_performance_mvp.py::test_memory_usage -v

# Assert memory < threshold (150MB for Pi 3B+)
```

## Profiling Workflow

### 1. Baseline Measurement
```bash
# Clean start, measure initial memory
python src/main.py &
PID=$!
sleep 5
ps -p $PID -o rss=
```

### 2. Stress Test
```bash
# Navigate through all 386 Pokémon
# Monitor memory at intervals: 10, 50, 100, 200, 386
```

### 3. Identify Growth Sources
```python
# Use objgraph to find growing objects
import objgraph
objgraph.show_growth()
# ... perform operations ...
objgraph.show_growth()  # Shows which object types increased
```

### 4. Validate Fix
After implementing LRU cache or other optimization:
- Re-run stress test
- Compare memory usage at each interval
- Ensure memory stabilizes (plateau pattern, not linear growth)

## Pi-Specific Considerations

### Swap Usage = Death
If Pi starts swapping to SD card:
- Application becomes unresponsive (100x slowdown)
- SD card wear accelerates

**Monitor swap:**
```bash
free -h
# Swap used should be 0B or minimal
```

### Memory Limits
```python
# Set Python memory limit (optional safety measure)
import resource
resource.setrlimit(resource.RLIMIT_AS, (200 * 1024 * 1024, -1))  # 200MB limit
```

### OOM Killer
If memory exceeds system limits, Linux OOM killer terminates the process.  
**Prevention:** Stay well under limits (150MB target on 1GB system provides safety margin)

## Quick Wins
1. ✅ Replace unlimited dict cache with LRU cache (maxsize=100)
2. ✅ Call `.convert_alpha()` on all loaded sprites
3. ✅ Add memory assertions to performance tests (`assert memory_mb < 150`)
4. ✅ Implement explicit cleanup in cache eviction (`del surface`)
5. ✅ Monitor memory during development with `PerformanceMonitor`

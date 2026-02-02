# Memory Optimization Guide

Strategies for keeping ShokeDex memory usage under limits on resource-constrained Raspberry Pi.

## Target Memory Budgets

- **Pi 3B+ (1GB RAM)**: <150MB total usage
- **Pi 4 (2GB+ RAM)**: <200MB total usage
- **Sprite cache**: <50MB
- **Database connections**: <20MB

## Measurement Tools

### Quick Memory Check
```python
import psutil
import os

process = psutil.Process(os.getpid())
mem_mb = process.memory_info().rss / 1024 / 1024
print(f"Memory usage: {mem_mb:.1f} MB")
```

### Detailed Profiling
```bash
# Install memory_profiler
pip install memory_profiler

# Run with profiling
python -m memory_profiler src/main.py
```

### Track Memory Over Time
```python
import psutil
import time

def monitor_memory(duration_sec=60):
    """Track memory usage over time"""
    process = psutil.Process()
    samples = []
    
    for _ in range(duration_sec):
        mem_mb = process.memory_info().rss / 1024 / 1024
        samples.append(mem_mb)
        time.sleep(1)
    
    print(f"Min: {min(samples):.1f}MB, Max: {max(samples):.1f}MB, Avg: {sum(samples)/len(samples):.1f}MB")
```

## Common Memory Issues

### 1. Unbounded Sprite Cache
**Problem**: Cache grows without limit
**Solution**: LRU cache with max size

```python
from collections import OrderedDict

class BoundedSpriteCache:
    def __init__(self, max_size=128):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if len(self.cache) >= self.max_size:
            # Remove oldest
            self.cache.popitem(last=False)
        self.cache[key] = value
```

### 2. Surface Format Bloat
**Problem**: RGBA surfaces use 4x memory vs indexed color
**Solution**: Use appropriate format

```python
# For images with transparency
surface = pygame.image.load(path).convert_alpha()

# For opaque images (uses less memory)
surface = pygame.image.load(path).convert()
```

### 3. Database Result Accumulation
**Problem**: Fetching all rows at once
**Solution**: Use generators or pagination

```python
# Bad: Loads all into memory
all_pokemon = cursor.fetchall()

# Good: Iterator
def get_pokemon_batch(batch_size=50):
    cursor.execute("SELECT * FROM pokemon")
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield from batch
```

## Caching Strategy

### Size-Limited Cache Pattern
```python
from functools import lru_cache

# Automatically evicts least recently used
@lru_cache(maxsize=256)
def expensive_operation(arg):
    # ... do work
    return result

# Check cache info
print(expensive_operation.cache_info())
# CacheInfo(hits=150, misses=106, maxsize=256, currsize=106)
```

### Manual Cache Management
```python
class SmartCache:
    def __init__(self, max_memory_mb=50):
        self.cache = {}
        self.max_bytes = max_memory_mb * 1024 * 1024
        self.current_bytes = 0
    
    def add(self, key, surface):
        # Estimate surface memory
        size_bytes = surface.get_width() * surface.get_height() * 4
        
        # Evict if needed
        while self.current_bytes + size_bytes > self.max_bytes and self.cache:
            # Remove oldest entry (in practice, use OrderedDict)
            old_key = next(iter(self.cache))
            old_surface = self.cache.pop(old_key)
            self.current_bytes -= old_surface.get_width() * old_surface.get_height() * 4
        
        self.cache[key] = surface
        self.current_bytes += size_bytes
```

## Testing for Memory Leaks

### Extended Session Test
```python
def test_no_memory_leak():
    """Verify memory stable over 1000 operations"""
    import tracemalloc
    
    tracemalloc.start()
    baseline = None
    
    for iteration in range(10):
        # Simulate normal usage
        for i in range(1, 101):
            sprite = sprite_loader.get_sprite(i, 'detail')
        
        current, peak = tracemalloc.get_traced_memory()
        
        if iteration == 1:
            baseline = current
        elif iteration == 9:
            # Memory should stabilize (allow 10% growth)
            assert current < baseline * 1.1, f"Memory leak: {current/1024/1024:.1f}MB vs {baseline/1024/1024:.1f}MB baseline"
    
    tracemalloc.stop()
```

## Optimization Checklist

- ✅ Implement bounded cache with LRU eviction
- ✅ Convert surfaces to optimal format
- ✅ Use generators for large result sets
- ✅ Clear caches on screen transitions
- ✅ Profile memory usage under load
- ✅ Test for leaks in long sessions

## Monitoring in Production

Add to `PerformanceMonitor`:
```python
def get_memory_usage_mb(self):
    """Return current memory usage in MB"""
    return psutil.Process().memory_info().rss / 1024 / 1024

def check_memory_threshold(self, threshold_mb=150):
    """Warn if exceeding memory budget"""
    usage = self.get_memory_usage_mb()
    if usage > threshold_mb:
        print(f"⚠️ Memory usage {usage:.1f}MB exceeds {threshold_mb}MB threshold")
    return usage < threshold_mb
```

## Pitfalls to Avoid

- ❌ Keeping references to large objects unnecessarily
- ❌ Not clearing event queues
- ❌ Accumulating log messages in memory
- ❌ Loading all assets on startup

## Target Metrics

- **Startup memory**: <80MB
- **Stable usage after 10 min**: <120MB (Pi 3B+)
- **Memory growth**: <1% per hour of operation
- **Sprite cache**: <50MB with 128 entry limit

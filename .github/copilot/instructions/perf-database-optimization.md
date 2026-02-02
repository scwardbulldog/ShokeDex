# Performance Engineering Guide: Database Optimization

**Context:** ShokeDex uses SQLite for local Pokémon data storage. Database operations are critical path for screen transitions and data display.

## Quick Performance Measurement

**Baseline profiling:**
```bash
# Time database queries
python -m cProfile -s cumulative src/data/manage_db.py query --id 25
```

**Measure query latency:**
```python
import time
from src.data.database import Database

with Database() as db:
    start = time.perf_counter()
    pokemon = db.get_pokemon_by_id(25)
    print(f"Query time: {(time.perf_counter() - start)*1000:.2f}ms")
```

## Key Optimization Targets

**1. Result Caching (HIGHEST IMPACT)**
- Current: No caching, every query hits SQLite
- Target: LRU cache for frequently accessed Pokémon (e.g., Gen 1 starters)
- Expected gain: 10-50x speedup for cached queries (0.5ms vs 5-50ms)

**2. Connection Management**
- Current: Context manager opens/closes per operation
- Optimization: Consider connection pooling for rapid-fire queries
- Watch: Connection overhead minimal (<1ms) on Pi, but cumulative

**3. Query Optimization**
- Evolution chains may trigger N+1 queries (fetch parent, then children)
- Add composite indexes for common patterns: `(generation, type_id)`, `(name, generation)`
- Profile slow queries: `EXPLAIN QUERY PLAN SELECT ...`

**4. PRAGMA Tuning**
```sql
PRAGMA journal_mode = WAL;        -- Write-Ahead Logging (faster writes)
PRAGMA synchronous = NORMAL;      -- Balance safety vs speed
PRAGMA cache_size = -4000;        -- 4MB cache (default 2MB)
PRAGMA temp_store = MEMORY;       -- Use RAM for temp tables
```

## Measurement Strategy

**Before changes:**
1. Run `tests/test_database.py` to baseline query performance
2. Profile database access during navigation: `python tools/profile_performance.py`
3. Note P50/P95/P99 query latencies

**After changes:**
1. Re-run same tests and profiling
2. Verify cache hit rates (if caching added)
3. Ensure no regressions in memory usage

## Common Pitfalls

- **Unbounded cache:** Use LRU with size limit (e.g., 100 Pokémon = ~10MB)
- **Stale data:** Cache invalidation strategy if data updates (unlikely for Pokémon)
- **Thread safety:** SQLite single-writer, avoid concurrent writes from threads

## Success Metrics

- Query latency P95 < 10ms (current: ~20-50ms for complex queries)
- Cache hit rate > 80% during typical navigation
- Memory overhead < 20MB for cached data

# Database Performance Engineering Guide

## Quick Context
ShokeDex uses SQLite with a relational schema covering 386 Pokémon across Generations 1-3. Database queries power every screen transition, search, and navigation action. Poor database performance directly impacts UI responsiveness.

## Performance Measurement

### Quick Profiling
```python
import time
from src.data.database import Database

with Database() as db:
    start = time.perf_counter()
    result = db.get_pokemon_by_id(25)
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"Query took {elapsed_ms:.2f}ms")
```

### Batch Query Testing
```bash
# Profile multiple queries to get P95/P99 latency
python -c "
from src.data.database import Database
import time
import statistics

times = []
with Database() as db:
    for i in range(1, 101):
        start = time.perf_counter()
        db.get_pokemon_by_id(i % 386 + 1)
        times.append((time.perf_counter() - start) * 1000)

print(f'Mean: {statistics.mean(times):.2f}ms')
print(f'P95: {sorted(times)[94]:.2f}ms')
print(f'P99: {sorted(times)[98]:.2f}ms')
"
```

## Common Bottlenecks

### 1. Evolution Chain Queries (N+1 Problem)
**Symptom:** Evolution screen loads slowly  
**Cause:** Fetching evolution data makes multiple separate queries  
**Fix:** Use JOINs or batch queries instead of individual lookups

### 2. Missing Indexes
**Check index usage:**
```bash
sqlite3 data/pokedex.db "EXPLAIN QUERY PLAN SELECT * FROM pokemon WHERE name = 'pikachu';"
```
If output shows "SCAN TABLE" instead of "SEARCH TABLE USING INDEX", add an index.

### 3. Unbounded Result Sets
**Issue:** Queries like `SELECT * FROM pokemon` load all 386 rows  
**Fix:** Use LIMIT/OFFSET for pagination, add WHERE clauses to filter

## Optimization Techniques

### Query Result Caching
**When:** Pokémon data rarely changes after initial load  
**Implementation:** Use `functools.lru_cache` on getter methods
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_get_pokemon(pokemon_id: int):
    # Database query here
    pass
```
**Impact:** 10-100x faster for repeated lookups

### Connection Reuse
**Current:** Context manager opens/closes per operation  
**Optimization:** Consider connection pooling for rapid queries  
**Tradeoff:** More complex lifecycle management

### PRAGMA Optimizations
Edit `src/data/database.py` to add:
```python
cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging
cursor.execute("PRAGMA synchronous=NORMAL")  # Balance safety/speed
cursor.execute("PRAGMA cache_size=-64000")  # 64MB page cache
cursor.execute("PRAGMA temp_store=MEMORY")  # Use RAM for temp tables
```
**Impact:** 20-50% faster writes, 10-20% faster reads  
**Tradeoff:** Slightly higher memory usage

## Testing Strategy

### Before/After Benchmarking
1. Measure baseline: `pytest -m performance -v`
2. Make optimization changes
3. Re-measure: `pytest -m performance -v`
4. Compare results (look for >10% improvement to be meaningful)

### Realistic Load Patterns
Simulate user navigation:
- Sequential browsing: IDs 1→2→3→4
- Random access: Jump between different Pokémon
- Search operations: Query by name
- Type filtering: Get all Fire-type Pokémon

### Regression Detection
After optimization, ensure:
- All unit tests pass (`pytest -m unit`)
- Integration tests pass (`pytest -m integration`)
- Database integrity maintained (`python src/data/manage_db.py stats`)

## Pi-Specific Considerations

**SD Card I/O:** Raspberry Pi uses SD card storage, which is slower than SSD  
- Minimize writes (use WAL mode)
- Keep database file defragmented (VACUUM occasionally)
- Consider pre-warming cache on startup

**Memory Constraints:** Pi 3B+ has 1GB RAM shared with GPU  
- Don't cache entire database in memory
- Use LRU cache with reasonable maxsize (50-200 items)
- Monitor with: `free -h`

## Quick Wins
1. ✅ Add `@lru_cache` to `get_pokemon_by_id()` and `get_pokemon_by_name()`
2. ✅ Enable WAL mode in database initialization
3. ✅ Add composite indexes for common query patterns
4. ✅ Batch evolution chain queries using JOINs

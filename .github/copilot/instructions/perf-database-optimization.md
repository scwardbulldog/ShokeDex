# Database Performance Optimization Guide

This guide provides practical strategies for optimizing database operations in ShokeDex.

## Current Architecture

- **Database**: SQLite with parameterized queries
- **Connection pattern**: Context manager (`with Database() as db:`)
- **Indexes**: name, generation, types columns
- **Schema**: 12 tables covering Pokémon, types, stats, evolutions, abilities

## Performance Measurement

### Quick Profiling
```python
import time
start = time.perf_counter()
# Database operation
elapsed = time.perf_counter() - start
print(f"Query took {elapsed*1000:.2f}ms")
```

### Comprehensive Analysis
```bash
python -m cProfile -s cumtime src/data/manage_db.py query --id 25
```

## Common Bottlenecks

### 1. N+1 Query Pattern
**Problem**: Evolution chains may trigger multiple queries
```python
# Bad: Separate query for each evolution
for evo in evolutions:
    pokemon = db.get_pokemon_by_id(evo['evolves_to_id'])
```

**Solution**: Use JOIN or batch queries
```python
# Good: Single query with JOIN
SELECT e.*, p.name FROM evolutions e 
JOIN pokemon p ON e.evolves_to_id = p.id 
WHERE e.pokemon_id = ?
```

### 2. Unbounded Queries
**Problem**: Loading all Pokémon at once
**Solution**: Add LIMIT/OFFSET for pagination, use generators for large result sets

### 3. Missing Indexes
**Check**: Run EXPLAIN QUERY PLAN before adding indexes
```sql
EXPLAIN QUERY PLAN SELECT * FROM pokemon WHERE generation = 1;
```

## Quick Wins

### Query Result Caching
Use functools.lru_cache for frequently accessed Pokémon:
```python
from functools import lru_cache

@lru_cache(maxsize=256)
def get_pokemon_cached(pokemon_id):
    with Database() as db:
        return db.get_pokemon_by_id(pokemon_id)
```

### Connection Pooling
For repeated operations, reuse connection:
```python
# Instead of multiple context managers
with Database() as db:
    for i in range(1, 152):
        db.get_pokemon_by_id(i)  # Reuses connection
```

### PRAGMA Optimizations
Document in `src/data/database.py` initialization:
```python
cursor.execute("PRAGMA journal_mode=WAL")  # Better concurrency
cursor.execute("PRAGMA cache_size=-16000")  # 16MB cache
cursor.execute("PRAGMA synchronous=NORMAL")  # Faster writes
```

## Testing Performance Changes

1. **Baseline**: Measure current performance with representative queries
2. **Implement**: Make targeted change
3. **Compare**: Run same queries, verify improvement
4. **Validate**: Ensure all tests still pass

### Example Test Pattern
```python
def test_query_performance():
    iterations = 100
    start = time.perf_counter()
    with Database() as db:
        for i in range(1, iterations + 1):
            db.get_pokemon_by_id(i)
    elapsed = time.perf_counter() - start
    avg_ms = (elapsed / iterations) * 1000
    assert avg_ms < 5.0, f"Avg query time {avg_ms:.2f}ms exceeds 5ms threshold"
```

## Pitfalls to Avoid

- ❌ Never use string formatting for SQL (use parameterized queries)
- ❌ Don't optimize without profiling first
- ❌ Don't add indexes blindly (they slow down writes)
- ❌ Don't cache mutable objects without copying

## Target Metrics

- **Simple queries** (get by ID): <2ms
- **Complex queries** (evolution chains): <10ms
- **Bulk operations** (loading Gen 1): <200ms total
- **Cache hit rate**: >80% during typical navigation

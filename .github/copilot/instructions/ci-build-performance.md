# CI and Build Performance Guide

## Quick Context
ShokeDex CI runs 4 separate test jobs (unit, integration, e2e, performance) on every push/PR. E2E tests include database seeding which takes 10-20 minutes. Faster CI = faster developer feedback and more iterations.

## Current CI Structure

### Job Breakdown
1. **unit-tests**: Fast, parallel (`pytest -n auto`), ~1-2 min
2. **integration-tests**: Moderate, sequential, ~3-5 min
3. **e2e-tests**: Slow, includes DB seeding, ~15-25 min
4. **performance-tests**: Fast, benchmarks only, ~2-3 min
5. **coverage-threshold**: Aggregates coverage, ~2-3 min

**Total runtime:** ~25-40 minutes per CI run

## Performance Measurement

### Job Timing Analysis
```bash
# View recent workflow runs
gh run list --repo scwardbulldog/ShokeDex --workflow test.yml --limit 10

# Detailed timing for specific run
gh run view <run-id> --repo scwardbulldog/ShokeDex
```

### Local Build Profiling
```bash
# Time individual steps locally
time python -m pip install -r requirements.txt
time pytest -m unit -n auto
time pytest -m integration
time python src/data/manage_db.py seed --gen 1-3
```

## Common Bottlenecks

### 1. Database Seeding in E2E Tests
**Current:** Seeds 386 Pokémon from PokéAPI every run (10-20 min)  
**Impact:** 50-80% of total CI time  
**Root cause:** 0.5s rate limiting per API request + network latency

### 2. Redundant Dependency Installation
**Current:** Each job installs dependencies independently  
**Impact:** 4x pip install operations  
**Cache hit:** Usually good due to GitHub Actions cache, but misses add 1-2 min each

### 3. Sequential Test Execution
**Current:** Integration tests run sequentially  
**Opportunity:** Some integration tests could be parallelized

### 4. No Incremental Testing
**Current:** Every CI run tests entire codebase  
**Opportunity:** Only test changed modules (advanced)

## Optimization Techniques

### Pre-Built Database Artifact (HIGHEST IMPACT)
**Strategy:** Seed database once, cache as artifact, reuse across runs

**Implementation:**
```yaml
# In .github/workflows/test.yml

jobs:
  setup-database:
    name: Setup Database Cache
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      
      # Check if cached DB exists
      - name: Cache database
        id: cache-db
        uses: actions/cache@v3
        with:
          path: data/pokedex.db
          key: pokedex-db-${{ hashFiles('src/data/schema.sql', 'src/data/loader.py') }}
      
      # Only seed if cache miss
      - name: Seed database
        if: steps.cache-db.outputs.cache-hit != 'true'
        run: |
          python src/data/manage_db.py init
          python src/data/manage_db.py seed --gen 1-3
      
      - name: Upload DB artifact
        uses: actions/upload-artifact@v3
        with:
          name: seeded-database
          path: data/pokedex.db
  
  e2e-tests:
    needs: setup-database
    steps:
      # Download pre-built DB
      - name: Download database
        uses: actions/download-artifact@v3
        with:
          name: seeded-database
          path: data/
      
      - name: Run E2E tests
        run: pytest -m e2e -v
```

**Impact:** 10-20 min reduction in CI time (only pays seeding cost on cache miss)

### Parallel Test Execution
**Current:** `-n auto` only on unit tests  
**Optimization:** Enable for integration tests too
```bash
pytest -m integration -n auto  # Instead of sequential
```

**Tradeoff:** Some integration tests may have shared state issues (needs investigation)

### Dependency Caching Optimization
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
    cache-dependency-path: requirements.txt  # Explicit cache key
```

**Impact:** Faster cache hits, reduced pip install time

### Test Sharding (Advanced)
For very large test suites, shard across multiple runners:
```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: pytest --shard-id=${{ matrix.shard }} --num-shards=4
```

**Impact:** 4x parallelization (but 4x runner cost)  
**Recommendation:** Not needed yet for ShokeDex (test suite manageable)

## Testing Strategy

### Before/After CI Timing
1. Baseline: Run CI 3 times, record average total time
2. Implement optimization (e.g., DB caching)
3. Run CI 3 times with new setup
4. Compare: Calculate % improvement

**Success metric:** >30% reduction in total CI time

### Cache Hit Rate Monitoring
```bash
# Check cache effectiveness in workflow logs
# Look for "Cache hit: true" or "Cache miss"
gh run view <run-id> --log | grep -i cache
```

### Local Simulation
```bash
# Simulate CI steps locally to validate before pushing
rm -rf data/pokedex.db
time python src/data/manage_db.py init
time python src/data/manage_db.py seed --gen 1-3
# If this is slow locally, it'll be slow in CI
```

## Developer Workflow Optimization

### Fast Feedback Loop for Development
```bash
# During development, run only affected tests
pytest tests/test_database.py -v  # Specific module

# Or use watch mode (requires pytest-watch)
pip install pytest-watch
ptw -- -m unit  # Re-runs on file changes
```

### Pre-Commit Hooks (Optional)
```bash
# Install pre-commit (not in requirements.txt yet)
pip install pre-commit

# Create .pre-commit-config.yaml
# Run fast checks before pushing (linting, unit tests)
```

## Quick Wins
1. ✅ Cache pre-built database as artifact (10-20 min savings)
2. ✅ Enable `-n auto` for integration tests (30-50% faster integration job)
3. ✅ Explicitly set cache-dependency-path for pip (better cache hits)
4. ✅ Run unit tests first (fail fast on common errors)
5. ✅ Make performance tests continue-on-error (don't block on benchmark flakiness)

## Advanced Optimizations (Future)

### Conditional Test Execution
```yaml
- name: Detect changed files
  id: changed-files
  uses: tj-actions/changed-files@v35
  with:
    files: |
      src/**/*.py
      tests/**/*.py

- name: Run relevant tests only
  if: steps.changed-files.outputs.any_changed == 'true'
  run: pytest <changed-test-files>
```

### Matrix Testing (Python Versions)
Currently testing only Python 3.11. If multi-version support needed:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
```

### Incremental Coverage
```bash
# Only measure coverage for changed lines
# Requires tools like diff-cover
pip install diff-cover
diff-cover coverage.xml --compare-branch=main
```

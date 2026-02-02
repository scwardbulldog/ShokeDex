# CI and Build Performance Guide

Optimize CI/CD pipeline and development workflow for faster feedback loops.

## Current CI Structure

- **4 parallel jobs**: unit, integration, e2e, performance
- **Test framework**: pytest with pytest-xdist for parallelization
- **Database seeding**: Runs in e2e tests (~10-20 min)
- **Coverage**: pytest-cov with Codecov uploads

## Measurement

### Local Build Timing
```bash
time pytest -m unit
time pytest -m integration
time pytest -m e2e
```

### CI Workflow Duration
Check GitHub Actions logs for job timing breakdowns

## High-Impact Optimizations

### 1. Pre-built Database Artifact
**Problem**: Seeding database in e2e tests takes 10-20 minutes
**Solution**: Build once, cache as artifact

```yaml
# Add to .github/workflows/test.yml
- name: Cache seeded database
  uses: actions/cache@v3
  with:
    path: data/pokedex.db
    key: pokedex-db-${{ hashFiles('src/data/migrations/*.sql') }}
    
- name: Seed database (if needed)
  if: steps.cache.outputs.cache-hit != 'true'
  run: |
    python src/data/manage_db.py init
    python src/data/manage_db.py seed --gen 1-3
```

### 2. Incremental Testing
**Problem**: Running all tests on small changes is slow
**Solution**: Use pytest-testmon or manual test selection

```bash
# Only run tests affected by changed files
pytest --testmon
```

### 3. Dependency Caching
Already using `cache: 'pip'` in setup-python action - verify effectiveness:
```bash
# Check if cache is being used in CI logs
# Look for "Cache restored from key: ..."
```

## Test Execution Optimization

### Parallel Execution
```bash
# Use all CPU cores
pytest -n auto

# Or specify core count
pytest -n 4
```

### Fail Fast for Development
```bash
# Stop at first failure during development
pytest -x

# Show only short traceback
pytest --tb=short
```

### Profile Slow Tests
```bash
# Identify slowest tests
pytest --durations=10

# Mark and skip slow tests in development
pytest -m "not slow"
```

## Development Workflow Tips

### Skip Database Seeding Locally
If database already exists, skip seeding:
```python
# In manage_db.py seed command
if db.count_pokemon() > 0:
    print("Database already seeded, skipping...")
    return
```

### Quick Smoke Tests
Create minimal test suite for rapid validation:
```bash
# Fast sanity check (~5 seconds)
pytest tests/test_database.py::test_connection -v
```

### Watch Mode for UI Development
```bash
# Re-run tests on file changes (requires pytest-watch)
pytest-watch -c -n -- -m unit
```

## CI-Specific Strategies

### Matrix Testing (if needed later)
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
# Only test critical versions to save time
```

### Conditional Job Execution
```yaml
# Skip performance tests on draft PRs
if: github.event.pull_request.draft == false
```

## Measuring Success

### Before/After Metrics
- **Total CI time**: Baseline vs optimized
- **Feedback loop**: Time from push to test results
- **Test execution**: Local test suite runtime
- **Cache hit rate**: Dependency and database cache effectiveness

### Example Comparison
```
Before:
- Unit tests: 45s
- Integration: 90s  
- E2E (with seeding): 15 min
- Total: ~17 min

After (with db cache):
- Unit tests: 35s (parallel optimization)
- Integration: 70s (parallel optimization)
- E2E (cached db): 2 min
- Total: ~4 min
```

## Quick Wins Checklist

- ✅ Database artifact caching (saves 10+ min)
- ✅ Parallel test execution with `-n auto`
- ✅ Verify pip cache is working
- ⏳ Profile and mark slow tests
- ⏳ Skip unnecessary jobs on draft PRs
- ⏳ Incremental testing for local development

## Avoid These Pitfalls

- ❌ Don't parallelize tests with shared database state
- ❌ Don't cache artifacts that depend on external API data without version key
- ❌ Don't optimize before measuring (profile first!)
- ❌ Don't sacrifice test coverage for speed without good reason

## Target Metrics

- **Local unit tests**: <1 minute
- **Local full suite**: <5 minutes (with cached db)
- **CI total time**: <5 minutes
- **Feedback loop**: <3 minutes for typical PR

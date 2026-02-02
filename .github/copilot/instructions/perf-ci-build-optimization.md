# Performance Engineering Guide: CI/CD & Build Performance

**Context:** ShokeDex CI runs 4 test jobs (unit, integration, e2e, performance). E2E tests include database seeding (~10-20 min). Faster CI = faster iteration.

## Quick Performance Measurement

**Measure test execution:**
```bash
# Time test suites
time pytest -m unit -n auto
time pytest -m integration
time pytest -m e2e
time pytest -m performance

# Identify slow tests
pytest --durations=10 -m unit
```

**Profile CI bottlenecks:**
- Check GitHub Actions logs for step durations
- Focus on: dependency install, database seeding, test execution

## Key Optimization Targets

**1. Database Seeding Artifact (HIGHEST IMPACT)**
- Current: E2E tests seed database every run (~10-20 min)
- Target: Cache pre-seeded database as GitHub Actions artifact
- Expected gain: Reduce e2e job from 20 min → 5 min

Implementation:
```yaml
# In .github/workflows/test.yml
- name: Restore database cache
  uses: actions/cache@v3
  with:
    path: data/pokedex.db
    key: pokedex-db-gen1-3-v1
    
- name: Seed database (if cache miss)
  if: steps.cache.outputs.cache-hit != 'true'
  run: |
    python src/data/manage_db.py init
    python src/data/manage_db.py seed --gen 1-3
```

**2. Parallel Test Execution**
- Already using `pytest -n auto` for unit tests (good!)
- Extend to integration tests where safe
- Profile: Does parallelism help on GitHub runners? (2-4 cores)

**3. Incremental Testing**
- Run only affected tests based on changed files
- Use `pytest --lf` (last failed) for rapid debugging
- Consider test impact analysis tools

**4. Dependency Caching**
- Already using `cache: 'pip'` in setup-python action (good!)
- Verify cache hits in Actions logs
- Consider caching system packages (`apt` cache)

## Measurement Strategy

**Baseline CI performance:**
1. Note total CI time for typical PR
2. Break down by job: unit (X min), integration (Y min), e2e (Z min), perf (W min)
3. Identify longest-running tests within each suite

**After optimization:**
1. Measure reduction in total CI time
2. Check cache hit rates in Actions logs
3. Verify no test coverage loss

**Local development:**
```bash
# Simulate CI performance
time (
  SDL_VIDEODRIVER=dummy pytest -m unit -n auto --cov=src &&
  SDL_VIDEODRIVER=dummy pytest -m integration --cov=src --cov-append &&
  SDL_VIDEODRIVER=dummy pytest -m e2e --cov=src --cov-append &&
  SDL_VIDEODRIVER=dummy pytest -m performance
)
```

## Common Pitfalls

- **Stale cache:** Database schema changes invalidate cached DB (update cache key)
- **Test interdependence:** Parallel tests must be isolated (avoid shared state)
- **Reduced coverage:** Don't skip tests for speed; optimize execution instead
- **Flaky tests:** Parallelism can expose race conditions; fix, don't hide

## Advanced: Performance Regression Detection

Add performance assertions in tests:
```python
@pytest.mark.performance
def test_sprite_load_performance():
    times = [measure_sprite_load(i) for i in range(1, 152)]
    p95 = sorted(times)[int(len(times)*0.95)]
    assert p95 < 50, f"P95 sprite load {p95}ms exceeds 50ms threshold"
```

Track performance metrics over time:
- Store benchmark results as GitHub Actions artifacts
- Compare against baseline on each PR
- Alert on regressions

## Success Metrics

- Total CI time < 15 min (from current ~25-30 min)
- E2E job time < 5 min (from ~20 min via DB caching)
- Unit test time < 2 min (maintain with parallelism)
- Cache hit rate > 90% for dependencies and database

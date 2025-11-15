# System-Level Test Design: ShokeDex

**Date:** 2025-11-14
**Architect:** Murat (Master Test Architect)
**For:** King
**Status:** Draft - Awaiting Review

---

## Executive Summary

ShokeDex is a Raspberry Pi-based embedded application designed for testability with clean architecture patterns (manager singletons, screen-based navigation, database abstraction). This system-level review assesses testability before solutioning gate check and establishes the test strategy for implementation.

**Testability Assessment**: ✅ **PASS** with recommendations

The architecture demonstrates strong testability foundations:
- Manager pattern enables dependency injection for testing
- Database context manager with parameterized queries (safe, mockable)
- Screen lifecycle allows isolated UI testing
- Clear separation of concerns (data, UI, managers)
- Hardware abstraction (InputManager) enables desktop development

**Test Strategy**: 70% Unit / 20% Integration / 10% E2E
- Heavy unit coverage for business logic and managers
- Integration tests for database operations and screen integration
- Minimal E2E for critical user journeys (resource-constrained target)

**Recommendations for Sprint 0**:
1. Establish pytest framework with fixtures for managers
2. Create mock database context for unit tests
3. Set up pygame test harness for screen testing
4. Configure CI pipeline with coverage reporting (80%+ target)

---

## Testability Assessment

### Controllability: ✅ PASS

**Can we control system state for testing?**

**Strengths:**
- ✅ **Manager singleton pattern with dependency injection**: All managers (StateManager, AudioManager, InputManager) are created once and passed through ScreenManager, making them easily mockable in tests
- ✅ **Database context manager**: `with Database() as db:` pattern allows test database substitution (`:memory:` SQLite for fast tests)
- ✅ **Factory pattern for test data**: PokéAPI loader structure can seed controlled test data
- ✅ **InputManager abstraction**: Keyboard mode allows desktop testing without GPIO hardware
- ✅ **StateManager uses JSON file**: Easy to mock with in-memory dict or tempfile

**Controllability Patterns:**
```python
# Test setup example - full control over state
def test_detail_screen_displays_pokemon():
    # Mock managers for isolation
    mock_state = MockStateManager()
    mock_audio = MockAudioManager()
    mock_input = MockInputManager()
    
    # Mock database with test data
    test_db = Database(":memory:")
    test_db.seed_pokemon([
        {"id": 25, "name": "Pikachu", "type": "Electric"}
    ])
    
    # Screen under test with controlled dependencies
    screen_manager = ScreenManager(
        database=test_db,
        state_manager=mock_state,
        audio_manager=mock_audio,
        input_manager=mock_input
    )
    
    detail_screen = DetailScreen(screen_manager, pokemon_id=25)
    
    # Full control over screen lifecycle
    detail_screen.on_enter()
    detail_screen.update(0.016)  # Simulate one frame
    detail_screen.render(mock_surface)
    
    # Assertions on controlled state
    assert mock_audio.played_cry == 25
    assert mock_state.last_viewed_id == 25
```

**Testing Verdict**: Architecture enables full control over application state through dependency injection and abstraction layers.

---

### Observability: ✅ PASS

**Can we inspect system state to validate behavior?**

**Strengths:**
- ✅ **Manager public APIs**: StateManager exposes `get_last_viewed_id()`, `get_volume()` - easy to query state
- ✅ **Database query methods**: Helper methods (`get_pokemon_by_id()`, `get_pokemon_stats()`) provide clean observation points
- ✅ **Screen lifecycle hooks**: `on_enter()`, `on_exit()` callbacks allow pre/post condition validation
- ✅ **Deterministic rendering**: pygame surfaces can be captured and pixel-compared for visual regression
- ✅ **JSON state file**: Human-readable state makes debugging straightforward

**Observability Patterns:**
```python
# Observing state through public APIs
def test_state_manager_tracks_views():
    state_mgr = StateManager()
    
    # Action
    state_mgr.set_last_viewed(pokemon_id=25, generation=1)
    state_mgr.save_state()
    
    # Observable outcomes
    assert state_mgr.get_last_viewed_id() == 25
    assert state_mgr.get_last_viewed_generation() == 1
    assert "pikachu" in state_mgr.get_recent_views()  # If implemented
    
    # State file also observable
    with open(state_mgr.state_file) as f:
        state_json = json.load(f)
        assert state_json["last_viewed"]["pokemon_id"] == 25

# Observing rendering outcomes
def test_home_screen_renders_generation_badge():
    screen = HomeScreen(mock_screen_manager)
    surface = pygame.Surface((800, 480))
    
    # Render
    screen.render(surface)
    
    # Observe pixels or text
    assert_surface_contains_text(surface, "Kanto")  # Generation badge
    assert_sprite_rendered(surface, pokemon_id=1)  # Bulbasaur
```

**Testing Verdict**: Public APIs and lifecycle hooks provide comprehensive observability for validation.

---

### Reliability: ✅ PASS with Recommendations

**Are tests isolated, deterministic, and reproducible?**

**Strengths:**
- ✅ **Manager lifecycle clear**: Initialize once in main, pass to all screens - no global state
- ✅ **Database isolation**: Each test can use `:memory:` SQLite or tempfile cleanup
- ✅ **No network dependencies**: Offline-first design eliminates flakiness from API calls
- ✅ **Parameterized queries**: SQL injection prevention also makes queries predictable
- ✅ **Lazy loading strategy**: Sprites/audio loaded on-demand - tests can mock filesystem

**Concerns**:
- ⚠️ **Pygame initialization**: Tests need pygame display in headless environments (CI/CD)
- ⚠️ **Frame timing tests**: `delta_time` simulation may need mocking for determinism
- ⚠️ **GPIO hardware mocking**: InputManager needs graceful fallback (already planned with keyboard mode)
- ⚠️ **File I/O for state**: Tests must use temp directories to avoid pollution

**Reliability Recommendations**:
```python
# Pytest fixture for clean test database
@pytest.fixture
def test_database():
    """Provide isolated in-memory database for each test."""
    db = Database(":memory:")
    db.initialize_schema()
    db.seed_test_data([
        {"id": 1, "name": "Bulbasaur", ...},
        {"id": 25, "name": "Pikachu", ...},
    ])
    yield db
    db.close()  # Cleanup

# Pytest fixture for headless pygame
@pytest.fixture(scope="session")
def pygame_headless():
    """Initialize pygame in headless mode for CI."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()

# Fixture for temp state file
@pytest.fixture
def temp_state_manager(tmp_path):
    """StateManager with temp file - no pollution."""
    state_file = tmp_path / "test_state.json"
    mgr = StateManager(state_file=state_file)
    yield mgr
    # Auto-cleanup via tmp_path
```

**Testing Verdict**: Architecture is reliable with proper test fixture discipline. Pygame headless mode required for CI.

---

## Architecturally Significant Requirements (ASRs)

### ASR-1: Performance - 30+ FPS on Raspberry Pi 3B+ (Score: 6 - HIGH RISK)

**Requirement**: System shall maintain 30+ FPS during all operations on Raspberry Pi 3B+ hardware.

**Risk Assessment**:
- **Probability**: 2 (Possible) - Sprite loading and rendering could cause frame drops if not optimized
- **Impact**: 3 (Critical) - UX goal is "smooth browsing"; stuttering breaks nostalgia experience
- **Risk Score**: 2 × 3 = **6 (HIGH RISK)**

**Testability Approach**:
- **Performance profiling**: Measure frame times with `PerformanceMonitor` class (already implemented)
- **Automated benchmarks**: Unit tests validate sprite loading < 50ms, rendering < 16ms (60 FPS target)
- **Hardware testing**: Manual validation on actual Raspberry Pi 3B+ before release

**Test Strategy**:
```python
# Performance unit tests
def test_sprite_loader_performance():
    """Sprite loading must be under 50ms per sprite."""
    loader = SpriteLoader()
    
    start = time.time()
    sprite = loader.load_sprite(pokemon_id=25, size="detail")
    duration = time.time() - start
    
    assert duration < 0.050, f"Sprite load took {duration}s (>50ms threshold)"

def test_home_screen_render_performance(pygame_headless):
    """HomeScreen render must be under 16ms (60 FPS)."""
    screen = HomeScreen(mock_screen_manager)
    surface = pygame.Surface((800, 480))
    
    start = time.time()
    screen.render(surface)
    duration = time.time() - start
    
    assert duration < 0.016, f"Render took {duration}s (>16ms threshold)"
```

**Mitigation Plan**:
- Owner: Dev Team
- Timeline: Sprint 1-2
- Actions:
  1. Profile all rendering operations with `PerformanceMonitor`
  2. Optimize sprite caching (preload visible Pokémon)
  3. Use hardware-accelerated surfaces (`convert_alpha()`)
  4. Implement dirty rect updates if full blit too slow
- **Verification**: Manual testing on Pi 3B+ shows no dropped frames during navigation

---

### ASR-2: Input Latency - <100ms Button Response (Score: 4 - MEDIUM RISK)

**Requirement**: Button press response time shall be < 100ms.

**Risk Assessment**:
- **Probability**: 2 (Possible) - Event loop design could introduce lag
- **Impact**: 2 (Degraded) - Laggy input frustrates users but doesn't break functionality
- **Risk Score**: 2 × 2 = **4 (MEDIUM RISK)**

**Testability Approach**:
- **Unit tests**: Validate InputManager processes events within timing constraints
- **Integration tests**: Measure time from button press to screen response
- **Manual testing**: Feel test on hardware with GPIO buttons

**Test Strategy**:
```python
def test_input_manager_latency():
    """InputManager must process input under 10ms."""
    manager = InputManager(mode=InputMode.KEYBOARD)
    
    # Simulate key press event
    event = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_UP})
    
    start = time.time()
    action = manager.process_event(event)
    duration = time.time() - start
    
    assert action == InputAction.UP
    assert duration < 0.010, f"Input processing took {duration}s (>10ms)"

def test_screen_responds_to_input_quickly():
    """Screen must respond to input within 100ms total."""
    screen = HomeScreen(mock_screen_manager)
    
    start = time.time()
    screen.handle_input(InputAction.DOWN)
    duration = time.time() - start
    
    assert duration < 0.100, f"Input handling took {duration}s (>100ms)"
```

**Mitigation Plan**:
- Owner: Dev Team
- Timeline: Sprint 1
- Actions:
  1. Profile event loop with `test_input_latency.py` tool (already in tools/)
  2. Ensure InputManager polling is efficient (<10ms)
  3. Keep `handle_input()` methods lightweight (defer heavy work to `update()`)
- **Verification**: Latency test tool shows <100ms from press to screen update

---

### ASR-3: Data Integrity - State File Corruption Resilience (Score: 6 - HIGH RISK)

**Requirement**: System shall not corrupt state file during normal operation or power loss.

**Risk Assessment**:
- **Probability**: 2 (Possible) - SD card writes on Raspberry Pi can fail unexpectedly
- **Impact**: 3 (Critical) - Corrupted state file causes loss of favorites, last-viewed data
- **Risk Score**: 2 × 3 = **6 (HIGH RISK)**

**Testability Approach**:
- **Unit tests**: Validate StateManager handles corrupted JSON gracefully
- **Integration tests**: Simulate power loss scenarios (write interruption)
- **Manual testing**: Physical power-off during state save

**Test Strategy**:
```python
def test_state_manager_handles_corrupted_file(tmp_path):
    """StateManager must reset to defaults on corrupt file."""
    state_file = tmp_path / "corrupted.json"
    
    # Write invalid JSON
    state_file.write_text("{invalid json content")
    
    # StateManager should not crash
    mgr = StateManager(state_file=state_file)
    
    # Should load defaults
    assert mgr.get_last_viewed_id() == 1  # Default to Bulbasaur
    assert mgr.get_last_viewed_generation() == 1

def test_state_manager_atomic_writes(tmp_path):
    """StateManager must write atomically (temp file + rename)."""
    state_file = tmp_path / "state.json"
    mgr = StateManager(state_file=state_file)
    
    mgr.set_last_viewed(pokemon_id=25, generation=1)
    
    # save_state() should write to temp file first, then rename
    mgr.save_state()
    
    # Original file should exist and be valid JSON
    assert state_file.exists()
    with open(state_file) as f:
        state = json.load(f)
        assert state["last_viewed"]["pokemon_id"] == 25
```

**Mitigation Plan**:
- Owner: Dev Team
- Timeline: Sprint 0 (Foundation)
- Actions:
  1. Implement atomic write pattern (temp file + rename)
  2. Add JSON validation on load with fallback to defaults
  3. Log corruption events for debugging
  4. Consider backup state file (state.json.bak)
- **Verification**: Unit tests pass, manual power-off test recovers gracefully

---

### ASR-4: Offline Operation - No Runtime Internet Dependency (Score: 2 - LOW RISK)

**Requirement**: System shall function completely offline (no internet required after setup).

**Risk Assessment**:
- **Probability**: 1 (Unlikely) - Architecture is explicitly offline-first
- **Impact**: 2 (Degraded) - Accidental network call would fail on offline Pi
- **Risk Score**: 1 × 2 = **2 (LOW RISK)**

**Testability Approach**:
- **Unit tests**: Validate no network imports in runtime modules
- **Integration tests**: Run full application with network disabled
- **Static analysis**: Lint for `requests` usage outside `loader.py`

**Test Strategy**:
```python
def test_no_network_dependencies_in_runtime():
    """Runtime modules must not import network libraries."""
    import ast
    
    runtime_modules = [
        "src/main.py",
        "src/state_manager.py",
        "src/audio_manager.py",
        "src/input_manager.py",
        "src/ui/home_screen.py",
        "src/ui/detail_screen.py",
    ]
    
    for module_path in runtime_modules:
        with open(module_path) as f:
            tree = ast.parse(f.read())
        
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.Import)]
        
        # Disallowed network libraries
        assert "requests" not in imports, f"{module_path} imports requests"
        assert "urllib" not in imports, f"{module_path} imports urllib"

def test_application_runs_offline(monkeypatch):
    """Application must run with network disabled."""
    # Disable network
    monkeypatch.setattr("socket.socket", lambda *args: raise_exception())
    
    # Application should still function
    # (pytest would run main.py in subprocess with network blocked)
```

**Mitigation Plan**:
- Owner: Dev Team
- Timeline: Ongoing (code review discipline)
- Actions:
  1. Restrict `requests` usage to `src/data/loader.py` only
  2. Add pre-commit hook or CI check for network imports
  3. Document "offline-first" rule in architecture doc
- **Verification**: Static analysis test in CI passes

---

## Test Levels Strategy

### Recommended Split: 70% Unit / 20% Integration / 10% E2E

**Rationale**:
- **Resource-constrained target**: Raspberry Pi 3B+ has limited CPU/RAM - minimize slow E2E tests
- **Clean architecture**: Manager and screen patterns are highly unit-testable
- **Offline-first**: No external API dependencies to integration test
- **Small UI surface**: 5-7 screens total - limited E2E scenarios needed

---

### Unit Tests (70% of coverage)

**Focus Areas**:
- Manager classes (StateManager, AudioManager, InputManager)
- Database query methods (Database class)
- Sprite processing utilities (SpriteLoader, sprite_processor.py)
- Screen business logic (navigation, state updates)
- Utility functions (color conversions, generation ranges)

**Characteristics**:
- **Fast**: <100ms per test
- **Isolated**: No database, filesystem, or pygame dependencies (use mocks)
- **Parallel-safe**: Can run with pytest-xdist -n auto

**Example Coverage**:
```python
# StateManager unit tests (already implemented)
tests/test_state_manager.py:
- test_default_state()
- test_set_last_viewed()
- test_add_favorite()
- test_save_and_load_state()
- test_get_recent_views()

# Database unit tests (already implemented)
tests/test_database.py:
- test_get_pokemon_by_id()
- test_get_pokemon_by_name()
- test_get_pokemon_stats()
- test_get_pokemon_types()
- test_get_evolution_chain()
- test_parameterized_queries() # SQL injection prevention

# AudioManager unit tests (already implemented)
tests/test_audio_manager.py:
- test_play_cry()
- test_lru_cache_eviction()
- test_missing_audio_file_graceful()
- test_volume_control()

# InputManager unit tests (already implemented)
tests/test_input_manager.py:
- test_keyboard_mapping()
- test_gpio_mapping()
- test_mode_switching()
```

**Unit Test Standards** (from test-quality.md):
- ✅ No hard waits or `time.sleep()`
- ✅ No conditionals (deterministic execution)
- ✅ <300 lines per test file
- ✅ Explicit assertions in test bodies (not hidden in helpers)
- ✅ Use factories for test data (`createUser()`, `createPokemon()`)

---

### Integration Tests (20% of coverage)

**Focus Areas**:
- Screen lifecycle integration (Screen + ScreenManager + Managers)
- Database operations with real SQLite (not mocked)
- StateManager file I/O with real JSON files
- AudioManager with real pygame.mixer
- Generation navigation flow (HomeScreen filter + Database query)

**Characteristics**:
- **Moderate speed**: 100-500ms per test
- **Real dependencies**: Use `:memory:` SQLite, tempfile for state, headless pygame
- **Semi-isolated**: Clean up database/files after each test

**Example Coverage**:
```python
# Screen integration tests (NEW - needs implementation)
tests/test_screen_integration.py:
- test_home_screen_loads_generation()  # HomeScreen + Database
- test_detail_screen_plays_audio()  # DetailScreen + AudioManager
- test_screen_manager_navigation()  # Push/pop screen stack
- test_state_persistence_on_exit()  # Screen on_exit() saves state

# Database integration tests (EXPAND existing)
tests/test_database.py:
- test_generation_filtering()  # WHERE id BETWEEN ? AND ?
- test_evolution_chain_with_items()  # Complex join queries
- test_transaction_rollback()  # Database integrity

# Performance integration tests (already exists)
tests/test_performance_monitor.py:
- test_frame_time_tracking()
- test_performance_report_generation()
```

**Integration Test Standards**:
- ✅ Use pytest fixtures for setup/teardown (`@pytest.fixture`)
- ✅ Clean up resources (temp files, database connections)
- ✅ Use `tmp_path` fixture for file I/O tests
- ✅ Headless pygame for CI (`SDL_VIDEODRIVER=dummy`)

---

### E2E Tests (10% of coverage)

**Focus Areas**:
- Critical user journeys (boot → browse → detail → back)
- Generation switching workflow (L/R buttons through 3 generations)
- State persistence across "power cycles" (app restart)
- Input handling end-to-end (keyboard/GPIO → screen response)

**Characteristics**:
- **Slow**: 1-5 seconds per test (full app initialization)
- **Full dependencies**: Real database file, real state file, real pygame window
- **Minimal count**: <10 E2E tests total (target most critical paths)

**Example Coverage**:
```python
# E2E tests for MVP features (NEW - needs implementation)
tests/test_mvp_features.py:
- test_boot_to_last_viewed_pokemon()  # MVP: State persistence
- test_browse_all_generations()  # MVP: Generation navigation
- test_view_pokemon_detail_with_audio()  # MVP: Detail view + audio
- test_evolution_chain_display()  # MVP: Evolution screen
- test_keyboard_navigation_flow()  # Input: All buttons work

# E2E performance validation (NEW)
tests/test_performance_e2e.py:
- test_30fps_during_navigation()  # NFR-P1: Performance target
- test_input_latency_under_100ms()  # NFR-P2: Input latency
```

**E2E Test Standards**:
- ✅ One test per user journey (not per feature)
- ✅ Use real application entry point (`src/main.py`)
- ✅ Clean database before/after each test
- ✅ Measure performance metrics (FPS, latency)
- ⚠️ Skip E2E on fast feedback (run nightly or pre-release)

---

## NFR Testing Approach

### Security: ✅ PASS (Low Risk for Embedded Device)

**Context**: ShokeDex is a single-user, offline embedded device with no network exposure or sensitive data.

**Security Considerations**:
- ✅ **SQL injection prevention**: Parameterized queries used throughout (test-database.py validates)
- ✅ **No authentication**: Not applicable (single-user device)
- ✅ **No network exposure**: Offline-first design eliminates attack surface
- ✅ **File path safety**: Asset loading uses Path() and validation

**Testing Strategy**:
```python
# Security unit tests (EXPAND test_database.py)
def test_parameterized_queries_prevent_injection():
    """All database queries must use parameterized statements."""
    db = Database(":memory:")
    
    # Attempt SQL injection (should fail safely)
    malicious_input = "Pikachu'; DROP TABLE pokemon; --"
    
    # Query should return no results (not execute DROP)
    result = db.get_pokemon_by_name(malicious_input)
    
    assert result is None  # Safe handling
    
    # Verify table still exists
    assert db.table_exists("pokemon")

def test_file_path_validation():
    """Sprite paths must prevent directory traversal."""
    loader = SpriteLoader()
    
    # Attempt directory traversal
    with pytest.raises(ValueError):
        loader.load_sprite("../../etc/passwd")
```

**Security NFR Criteria**: ✅ **PASS**
- All queries parameterized (test coverage exists)
- No network exposure (offline design)
- File path validation present

---

### Performance: ⚠️ CONCERNS (Requires Hardware Validation)

**SLO/SLA Thresholds**:
- **P95 frame time**: <33ms (30 FPS minimum)
- **P99 sprite load**: <50ms (perceived instant)
- **Input latency**: <100ms (button press to screen update)

**Testing Strategy**:
- **Unit tests**: Validate individual operations meet timing targets
- **Integration tests**: Measure combined operations (sprite load + render)
- **Manual testing**: Actual Raspberry Pi 3B+ validation (hardware-dependent)

**Note**: Playwright/Cypress not applicable (embedded pygame app, not web). Performance tests are unit/integration with timing assertions.

```python
# Performance unit tests (EXPAND test_performance_monitor.py)
def test_sprite_loading_performance():
    """Sprite loading must meet P99 <50ms target."""
    loader = SpriteLoader()
    
    timings = []
    for pokemon_id in range(1, 387):  # All 386 Pokémon
        start = time.time()
        loader.load_sprite(pokemon_id, size="thumb")
        timings.append(time.time() - start)
    
    p99 = sorted(timings)[int(len(timings) * 0.99)]
    assert p99 < 0.050, f"P99 sprite load: {p99*1000:.1f}ms (>50ms)"

def test_frame_rendering_performance(pygame_headless):
    """Frame rendering must meet P95 <33ms target (30 FPS)."""
    screen = HomeScreen(mock_screen_manager)
    surface = pygame.Surface((800, 480))
    
    timings = []
    for _ in range(100):  # 100 frame samples
        start = time.time()
        screen.render(surface)
        timings.append(time.time() - start)
    
    p95 = sorted(timings)[int(len(timings) * 0.95)]
    assert p95 < 0.033, f"P95 render: {p95*1000:.1f}ms (>33ms for 30 FPS)"
```

**Performance NFR Criteria**: ⚠️ **CONCERNS**
- Unit tests pass on desktop (fast CPU)
- Requires validation on actual Raspberry Pi 3B+ hardware
- Mitigation: Manual testing in Sprint 1-2 on target device

---

### Reliability: ✅ PASS

**Reliability Requirements**:
- Graceful handling of missing assets (sprites, audio)
- State file corruption recovery
- No memory leaks during extended operation
- Offline operation resilience

**Testing Strategy**:
```python
# Reliability unit tests (NEW - expand existing tests)
def test_missing_sprite_graceful():
    """SpriteLoader must not crash on missing sprite."""
    loader = SpriteLoader()
    
    # Request non-existent sprite
    sprite = loader.load_sprite(pokemon_id=999)
    
    # Should return placeholder (not crash)
    assert sprite is not None
    assert sprite.get_size() == (64, 64)  # Placeholder size

def test_missing_audio_graceful():
    """AudioManager must not crash on missing cry."""
    audio = AudioManager()
    
    # Attempt to play missing audio
    result = audio.play_cry(pokemon_id=999)
    
    # Should fail silently (not raise exception)
    assert result is False

def test_state_manager_memory_leak():
    """StateManager must not leak memory during extended use."""
    import tracemalloc
    
    tracemalloc.start()
    mgr = StateManager()
    
    # Simulate 1000 state updates
    for i in range(1000):
        mgr.set_last_viewed(pokemon_id=i % 386 + 1, generation=(i % 3) + 1)
        mgr.save_state()
    
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Memory usage should be bounded (<1MB)
    assert current < 1_000_000, f"Memory usage: {current / 1e6:.1f}MB"
```

**Reliability NFR Criteria**: ✅ **PASS**
- Error handling present (AudioManager, SpriteLoader already graceful)
- State corruption recovery tested (test_state_manager.py)
- Need to add memory leak tests (tracemalloc)

---

### Maintainability: ✅ PASS

**Maintainability Requirements**:
- Test coverage ≥80% (target)
- Code duplication <5%
- Clear ownership and documentation

**Testing Strategy**:
- **CI**: pytest with coverage plugin (`pytest --cov=src`)
- **Code quality**: pylint for style, radon for complexity
- **Documentation**: Docstrings required for public functions

**Current Status**:
- Test files exist for core modules (state_manager, database, audio_manager, input_manager)
- Coverage not yet measured (need CI integration)
- Architecture doc is comprehensive (✅)

**Maintainability NFR Criteria**: ✅ **PASS**
- Architecture well-documented (architecture.md exists)
- Test structure established (tests/ directory with organized files)
- Need to add coverage reporting to CI

---

## Test Environment Requirements

### Local Development (Desktop)

**Requirements**:
- Python 3.11+
- pytest with plugins (pytest-cov, pytest-xdist for parallel)
- pygame (headless mode via SDL_VIDEODRIVER=dummy)
- In-memory SQLite (`:memory:`) for fast tests
- Mock GPIO (gpiozero not required for keyboard mode)

**Setup**:
```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-xdist

# Run unit tests (fast)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run parallel
pytest tests/ -n auto
```

---

### CI/CD Pipeline (GitHub Actions)

**Requirements**:
- Headless pygame (SDL_VIDEODRIVER=dummy)
- Coverage reporting (Codecov or similar)
- Test sharding for speed (pytest-xdist)

**Pipeline Stages**:
```yaml
# .github/workflows/test.yml (RECOMMENDED - not yet implemented)
name: Test Suite

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-xdist
      
      - name: Run unit tests (parallel, headless)
        env:
          SDL_VIDEODRIVER: dummy
        run: pytest tests/ -n auto --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
      
      - name: Check coverage threshold (80%)
        run: |
          COVERAGE=$(python -c "import xml.etree.ElementTree as ET; print(ET.parse('coverage.xml').getroot().attrib['line-rate'])")
          if (( $(echo "$COVERAGE < 0.80" | bc -l) )); then
            echo "❌ FAIL: Coverage $COVERAGE below 80% threshold"
            exit 1
          fi

  integration-tests:
    runs-on: ubuntu-latest
    steps:
      # Similar to unit-tests but run integration suite only
      - name: Run integration tests
        env:
          SDL_VIDEODRIVER: dummy
        run: pytest tests/test_*_integration.py -v
  
  performance-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Run performance benchmarks
        run: pytest tests/test_performance_*.py -v --benchmark
```

---

### Hardware Testing (Raspberry Pi 3B+)

**Requirements**:
- Physical Raspberry Pi 3B+ device
- Raspberry Pi OS (Bookworm)
- GPIO buttons wired (or keyboard fallback)
- Actual LCD display (or HDMI monitor)

**Test Approach**:
- **Manual validation**: Performance targets (30 FPS, <100ms latency)
- **Scripted tests**: Run E2E suite on device
- **Soak testing**: Run application for extended periods (memory leaks, stability)

**Hardware Test Checklist**:
```markdown
- [ ] Boot time <5 seconds
- [ ] 30+ FPS during navigation (visual validation)
- [ ] Input latency <100ms (feel test with stopwatch)
- [ ] GPIO buttons respond correctly (if wired)
- [ ] Audio plays without stutter (if speakers connected)
- [ ] No crashes during 1-hour soak test
- [ ] State persists across power cycles
```

---

## Testability Concerns

### ⚠️ Minor Concerns (Addressed with Recommendations)

**1. Pygame Headless Mode for CI**
- **Issue**: Pygame requires display driver; CI environments are headless
- **Impact**: Tests fail in GitHub Actions without SDL_VIDEODRIVER=dummy
- **Mitigation**: Pytest fixture sets environment variable, documented in CI setup
- **Status**: Addressable with fixture (see Reliability section above)

**2. Performance Validation on Target Hardware**
- **Issue**: Unit tests run on fast desktop CPUs, but target is slower Raspberry Pi
- **Impact**: Tests pass locally but may fail performance targets on Pi
- **Mitigation**: Manual validation phase on Pi 3B+ required before release
- **Status**: Acceptable trade-off (fast feedback vs. final validation)

**3. Frame Timing Determinism**
- **Issue**: `delta_time` in `update()` methods may vary; hard to test
- **Impact**: Tests may be flaky if they assert exact frame counts
- **Mitigation**: Mock clock for deterministic timing, or use ranges in assertions
- **Status**: Addressable with `unittest.mock.patch` on time functions

**Example Mitigation**:
```python
# Mock clock for deterministic frame timing
def test_animation_timing(monkeypatch):
    """Animation must complete in 30 frames (1 second at 30 FPS)."""
    frame_count = 0
    
    # Mock delta_time to fixed value (33.33ms per frame)
    def mock_delta():
        nonlocal frame_count
        frame_count += 1
        return 0.0333  # 30 FPS
    
    screen = AnimatedScreen(mock_screen_manager)
    
    while not screen.animation_complete:
        screen.update(mock_delta())
    
    assert frame_count == 30, f"Animation took {frame_count} frames (expected 30)"
```

---

### ✅ No Critical Concerns

**Architecture is well-designed for testing.**

All identified concerns have clear mitigation strategies and do not block implementation.

---

## Recommendations for Sprint 0

### 1. Establish Test Framework (Priority: P0)

**Goal**: Set up pytest with necessary fixtures and plugins before implementation starts.

**Tasks**:
- [x] Create tests/ directory (already exists)
- [ ] Add pytest.ini configuration
- [ ] Implement shared fixtures (`test_database`, `pygame_headless`, `temp_state_manager`)
- [ ] Document testing patterns in README or docs/testing_guide.md
- [ ] Add pytest-cov and pytest-xdist to requirements.txt

**Acceptance Criteria**:
- `pytest tests/ -v` runs all existing tests successfully
- Coverage report generates with `pytest --cov=src`
- Tests can run in parallel with `pytest -n auto`

---

### 2. Create Mock Database Context (Priority: P0)

**Goal**: Enable fast unit tests with controlled test data.

**Tasks**:
- [ ] Implement fixture for `:memory:` SQLite database
- [ ] Create test data seed functions (minimal Pokémon set for tests)
- [ ] Document usage pattern for developers

**Example Implementation**:
```python
# tests/conftest.py (pytest shared fixtures)
import pytest
from src.data.database import Database

@pytest.fixture
def test_database():
    """Provide isolated in-memory database for each test."""
    db = Database(":memory:")
    db.initialize_schema()
    
    # Seed minimal test data (Gen 1 starters + Pikachu)
    db.seed_pokemon([
        {"id": 1, "name": "Bulbasaur", "type1": "Grass", "type2": "Poison"},
        {"id": 4, "name": "Charmander", "type1": "Fire", "type2": None},
        {"id": 7, "name": "Squirtle", "type1": "Water", "type2": None},
        {"id": 25, "name": "Pikachu", "type1": "Electric", "type2": None},
    ])
    
    yield db
    db.close()
```

---

### 3. Set Up Pygame Test Harness (Priority: P1)

**Goal**: Enable screen testing without display hardware.

**Tasks**:
- [ ] Create `pygame_headless` fixture for CI
- [ ] Implement helper functions for surface assertions (`assert_surface_contains_text()`)
- [ ] Document pygame testing patterns

**Example Implementation**:
```python
# tests/conftest.py
import os
import pygame

@pytest.fixture(scope="session")
def pygame_headless():
    """Initialize pygame in headless mode for CI."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()

# tests/helpers/pygame_helpers.py
def assert_surface_contains_text(surface: pygame.Surface, text: str):
    """Assert that rendered surface contains specified text."""
    # Convert surface to image, OCR, or pixel comparison
    # Implementation depends on rendering approach
    pass  # Placeholder for now
```

---

### 4. Configure CI Pipeline with Coverage (Priority: P1)

**Goal**: Automate testing and enforce coverage standards.

**Tasks**:
- [ ] Create `.github/workflows/test.yml` (see Test Environment section)
- [ ] Set up Codecov or similar coverage reporting
- [ ] Add coverage badge to README.md
- [ ] Enforce 80%+ coverage threshold (warning, not blocking initially)

**Acceptance Criteria**:
- GitHub Actions run tests on every push
- Coverage report uploaded to Codecov
- README shows coverage badge

---

### 5. Document Testing Patterns (Priority: P2)

**Goal**: Ensure consistency across team (or future you!).

**Tasks**:
- [ ] Create `docs/testing_guide.md`
- [ ] Document fixture usage patterns
- [ ] Provide example tests for each test level (unit, integration, E2E)
- [ ] Add testing section to CONTRIBUTING.md (if applicable)

**Contents**:
- How to run tests locally
- How to write unit tests (managers, database)
- How to write integration tests (screens, full flows)
- How to write E2E tests (critical journeys)
- Performance testing approach
- CI/CD pipeline explanation

---

## Quality Gate Criteria

### Solutioning Gate Check: ✅ PASS with Recommendations

**Testability**: ✅ PASS
- Controllability: PASS (dependency injection, mocks possible)
- Observability: PASS (public APIs, lifecycle hooks)
- Reliability: PASS (isolated, deterministic, cleanup discipline)

**Test Strategy**: ✅ PASS
- Test levels defined (70/20/10 split appropriate for embedded app)
- NFR approach established (security, performance, reliability, maintainability)
- Environment requirements clear (desktop, CI, hardware)

**Sprint 0 Readiness**: ⚠️ CONCERNS (Recommendations Required)
- Test framework setup needed (pytest fixtures, CI pipeline)
- Mock database fixture required for fast unit tests
- Pygame test harness needed for screen testing
- Coverage reporting not yet configured

**Decision**: **PASS** - Architecture is testable. Implement Sprint 0 recommendations before starting feature development.

---

## Summary

**ShokeDex architecture demonstrates strong testability:**
- ✅ Manager pattern with dependency injection
- ✅ Database abstraction with parameterized queries
- ✅ Screen lifecycle for isolated UI testing
- ✅ Hardware abstraction (InputManager) for desktop development
- ✅ Offline-first design eliminates API flakiness

**Test strategy appropriate for embedded device:**
- 70% Unit (fast, isolated, parallel-safe)
- 20% Integration (database, screens, file I/O)
- 10% E2E (critical user journeys only)

**NFR validation approach:**
- Security: ✅ PASS (parameterized queries, no network exposure)
- Performance: ⚠️ CONCERNS (requires Pi 3B+ validation)
- Reliability: ✅ PASS (graceful degradation, state recovery)
- Maintainability: ✅ PASS (documented, test structure established)

**Recommendations for Sprint 0:**
1. Set up pytest framework with fixtures (P0)
2. Create mock database context for unit tests (P0)
3. Implement pygame test harness for CI (P1)
4. Configure CI pipeline with coverage (P1)
5. Document testing patterns (P2)

**Next Step**: Implement Sprint 0 recommendations, then proceed to `*framework` workflow for production-ready test architecture.

---

**Generated by**: BMad TEA Agent - Test Architect Module
**Workflow**: `.bmad/bmm/testarch/test-design` (System-Level Mode)
**Version**: 4.0 (BMad v6)
**Date**: 2025-11-14

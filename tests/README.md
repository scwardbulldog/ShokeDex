# ShokeDex Test Suite

Comprehensive test suite for ShokeDex using pytest framework with fixtures, helpers, and best practices.

## Quick Start

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-xdist

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run tests in parallel (fast)
pytest -n auto

# Run specific test categories
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest -m e2e            # E2E tests only
pytest -m performance    # Performance tests only
```

## Test Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures
├── helpers/                       # Test utilities (NO assertions)
│   ├── pokemon_factory.py         # Test data factories
│   └── pygame_helpers.py          # Pygame testing utilities
├── test_state_manager.py          # StateManager unit tests
├── test_database.py               # Database integration tests
├── test_audio_manager.py          # AudioManager unit tests
├── test_input_manager.py          # InputManager unit tests
├── test_sprite_processor.py       # Sprite processing tests
├── test_performance_monitor.py    # Performance tests
└── test_mvp_features.py           # E2E feature tests
```

## Test Categories (Markers)

Tests are organized by markers for selective execution:

- **`@pytest.mark.unit`**: Fast, isolated tests with no dependencies (70% of suite)
- **`@pytest.mark.integration`**: Tests with real database, file I/O, or manager integration (20%)
- **`@pytest.mark.e2e`**: Full application flow tests (10%)
- **`@pytest.mark.performance`**: Performance benchmarks (FPS, latency)
- **`@pytest.mark.slow`**: Tests taking >1 second
- **`@pytest.mark.hardware`**: Tests requiring actual Raspberry Pi hardware

## Fixtures

### Database Fixtures

```python
def test_get_pokemon(test_database):
    """test_database provides in-memory SQLite with test data."""
    pokemon = test_database.get_pokemon_by_id(1)
    assert pokemon["name"] == "Bulbasaur"
```

### Manager Fixtures

```python
def test_state_persistence(temp_state_manager):
    """temp_state_manager uses temporary file (auto-cleanup)."""
    temp_state_manager.set_last_viewed(25)
    assert temp_state_manager.get_last_viewed_id() == 25

def test_audio_playback(mock_audio_manager):
    """mock_audio_manager doesn't actually play sounds."""
    mock_audio_manager.play_cry(25)  # Silent, fast

def test_keyboard_input(keyboard_input_manager):
    """keyboard_input_manager for testing without GPIO."""
    action = keyboard_input_manager.map_key(pygame.K_UP)
    assert action == InputAction.UP
```

### Pygame Fixtures

```python
def test_screen_rendering(pygame_headless, mock_pygame_surface):
    """pygame_headless initializes pygame for CI (no display needed)."""
    screen = HomeScreen(mock_screen_manager)
    screen.render(mock_pygame_surface)
    # Verify rendering succeeded (no exceptions)
```

## Test Data Factories

Use factories from `tests/helpers/pokemon_factory.py` for consistent test data:

```python
from tests.helpers.pokemon_factory import create_pokemon, GEN_1_STARTERS

def test_with_custom_pokemon():
    # Create with overrides
    pikachu = create_pokemon(id=25, name="Pikachu", type1="Electric")
    
    # Use predefined data sets
    for starter in GEN_1_STARTERS:
        process_pokemon(starter)
```

## Pygame Testing Helpers

Use helpers from `tests/helpers/pygame_helpers.py` for surface validation:

```python
from tests.helpers.pygame_helpers import (
    count_non_background_pixels,
    find_color_region,
    compare_surfaces
)

def test_sprite_rendering(mock_pygame_surface):
    render_sprite(mock_pygame_surface, pokemon_id=25)
    
    # Verify something was rendered
    non_bg = count_non_background_pixels(mock_pygame_surface)
    assert non_bg > 0, "Sprite not rendered"
    
    # Find sprite region
    sprite_region = find_color_region(mock_pygame_surface, (255, 200, 50))
    assert sprite_region is not None, "Yellow sprite not found"
```

## Writing Tests

### Unit Test Pattern

```python
import pytest

@pytest.mark.unit
def test_generation_detection(temp_state_manager):
    """Test automatic generation detection from Pokémon ID."""
    # Gen 1
    temp_state_manager.set_last_viewed(25)
    assert temp_state_manager.get_last_viewed_generation() == 1
    
    # Gen 2
    temp_state_manager.set_last_viewed(152)
    assert temp_state_manager.get_last_viewed_generation() == 2
    
    # Gen 3
    temp_state_manager.set_last_viewed(252)
    assert temp_state_manager.get_last_viewed_generation() == 3
```

### Integration Test Pattern

```python
@pytest.mark.integration
def test_screen_state_integration(
    test_database,
    temp_state_manager,
    pygame_headless
):
    """Test HomeScreen integrates with StateManager correctly."""
    screen = HomeScreen(
        screen_manager=MockScreenManager(
            database=test_database,
            state_manager=temp_state_manager
        )
    )
    
    # Change Pokémon
    screen._select_pokemon(25)
    
    # Verify state updated
    assert temp_state_manager.get_last_viewed_id() == 25
```

### Performance Test Pattern

```python
@pytest.mark.performance
def test_sprite_loading_performance(benchmark_timer):
    """Sprite loading must be under 50ms (P99 target)."""
    loader = SpriteLoader()
    
    with benchmark_timer as timer:
        sprite = loader.load_sprite(25, size="detail")
    
    assert timer.elapsed < 0.050, f"Load took {timer.elapsed*1000:.1f}ms (>50ms)"
```

## Best Practices

### ✅ DO

- Use fixtures for setup/teardown (auto-cleanup)
- Keep tests under 300 lines (split if longer)
- Use factories for test data (consistent, unique)
- Keep assertions explicit in test bodies (not helpers)
- Mock external dependencies (filesystem, audio, GPIO)
- Use descriptive test names (`test_what_when_then`)

### ❌ DON'T

- Use `time.sleep()` or hard waits (use event-driven patterns)
- Use conditionals in tests (should be deterministic)
- Hide assertions in helper functions (keep them visible)
- Hardcode IDs or test data (use factories)
- Create tests that depend on execution order
- Leave temporary files or state behind (use fixtures)

## CI/CD Integration

Tests run automatically in CI with:

```yaml
# .github/workflows/test.yml (recommended)
name: Test Suite
on: [push, pull_request]

jobs:
  test:
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
      
      - name: Run tests
        env:
          SDL_VIDEODRIVER: dummy  # Headless pygame
        run: pytest -n auto --cov=src --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Test Coverage Goals

- **Overall**: ≥80% line coverage
- **Core Managers**: ≥90% (StateManager, AudioManager, InputManager)
- **Database**: ≥85% (critical for data integrity)
- **UI Screens**: ≥70% (harder to test, focus on business logic)
- **Utilities**: ≥90% (pure functions, easy to test)

Check coverage with:

```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View detailed report
```

## Performance Targets

Tests validate these NFRs:

- **Frame time**: P95 < 33ms (30 FPS minimum)
- **Sprite load**: P99 < 50ms (perceived instant)
- **Input latency**: < 100ms (button press to screen update)
- **Startup time**: < 5 seconds (boot to Pokémon display)

## Troubleshooting

### Pygame initialization fails

```bash
# Set headless mode
export SDL_VIDEODRIVER=dummy
pytest
```

### Tests fail in parallel

```bash
# Some tests may have shared state issues
# Run serially to debug
pytest -n 0
```

### Import errors

```bash
# Ensure src/ is in PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
pytest
```

### Coverage not measuring src/

```bash
# Use --cov=src (not --cov=tests)
pytest --cov=src --cov-report=term
```

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov plugin](https://pytest-cov.readthedocs.io/)
- [pytest-xdist (parallel execution)](https://pytest-xdist.readthedocs.io/)
- [Pygame testing tips](https://www.pygame.org/wiki/UnitTest)

## Architecture References

- **Test Design**: `docs/test-design-system.md` - System-level test strategy
- **Architecture**: `docs/architecture.md` - Application architecture patterns
- **PRD**: `docs/PRD.md` - Product requirements and NFRs

---

**Framework Version**: 1.0 (pytest-based)
**Last Updated**: 2025-11-14
**Maintained by**: King

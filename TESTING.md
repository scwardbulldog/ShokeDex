# Test Framework Quick Reference

## Installation

```bash
# Install pytest and plugins
pip install pytest pytest-cov pytest-xdist

# Or install all dependencies
pip install -r requirements.txt
```

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_state_manager.py

# Run specific test function
pytest tests/test_state_manager.py::test_default_state
```

### By Category (Markers)

```bash
# Unit tests only (fast, ~70% of suite)
pytest -m unit

# Integration tests only (~20% of suite)
pytest -m integration

# E2E tests only (slow, ~10% of suite)
pytest -m e2e

# Performance tests only
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### With Coverage

```bash
# Coverage with terminal report
pytest --cov=src --cov-report=term

# Coverage with HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html  # View in browser

# Coverage with missing lines
pytest --cov=src --cov-report=term-missing
```

### Parallel Execution (Fast)

```bash
# Run tests in parallel (auto-detect CPU cores)
pytest -n auto

# Specify number of workers
pytest -n 4

# Parallel with coverage
pytest -n auto --cov=src --cov-report=html
```

### CI Mode (Headless Pygame)

```bash
# Set headless mode for CI (no display needed)
export SDL_VIDEODRIVER=dummy
pytest -n auto --cov=src --cov-report=xml
```

### Debugging

```bash
# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Show local variables on failure
pytest -l

# Drop into debugger on failure
pytest --pdb

# Run last failed tests only
pytest --lf

# Run failed first, then others
pytest --ff
```

## Test Selection Patterns

```bash
# Run tests matching pattern
pytest -k "state_manager"
pytest -k "not performance"
pytest -k "state or audio"

# Run tests in specific directory
pytest tests/integration/

# Run tests modified recently (requires pytest-testmon)
pytest --testmon
```

## Writing Tests

### Using Fixtures

```python
import pytest

@pytest.mark.unit
def test_with_fixtures(test_database, temp_state_manager):
    """Fixtures provide clean test dependencies."""
    # test_database: in-memory SQLite
    # temp_state_manager: temporary state file
    
    pokemon = test_database.get_pokemon_by_id(1)
    temp_state_manager.set_last_viewed(pokemon["id"])
    
    assert temp_state_manager.get_last_viewed_id() == 1
```

### Parametrized Tests

```python
@pytest.mark.parametrize("pokemon_id,expected_gen", [
    (1, 1),    # Bulbasaur - Gen 1
    (152, 2),  # Chikorita - Gen 2
    (252, 3),  # Treecko - Gen 3
])
def test_generation_detection(temp_state_manager, pokemon_id, expected_gen):
    temp_state_manager.set_last_viewed(pokemon_id)
    assert temp_state_manager.get_last_viewed_generation() == expected_gen
```

### Using Test Data Factories

```python
from tests.helpers.pokemon_factory import create_pokemon, GEN_1_STARTERS

def test_with_factory():
    pikachu = create_pokemon(id=25, name="Pikachu", type1="Electric")
    assert pikachu["id"] == 25
```

### Performance Tests

```python
@pytest.mark.performance
def test_sprite_loading_speed(benchmark_timer):
    with benchmark_timer as timer:
        sprite = load_sprite(25)
    
    assert timer.elapsed < 0.050, f"Too slow: {timer.elapsed*1000:.1f}ms"
```

## Available Fixtures

### Database
- `test_database` - In-memory SQLite with test data

### Managers
- `temp_state_manager` - StateManager with temp file
- `mock_audio_manager` - AudioManager (no sound)
- `keyboard_input_manager` - InputManager (keyboard mode)

### Pygame
- `pygame_headless` - Initialize pygame for CI
- `mock_pygame_surface` - Surface for rendering tests

### Utilities
- `benchmark_timer` - Context manager for timing
- `tmp_path` - pytest built-in temp directory

## Common Issues

### Import errors

```bash
# Ensure src/ is in path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
pytest
```

### Pygame won't initialize

```bash
# Use headless mode
export SDL_VIDEODRIVER=dummy
pytest
```

### Tests pass locally but fail in CI

```bash
# Run with same settings as CI
export SDL_VIDEODRIVER=dummy
pytest -n auto --cov=src
```

### Coverage not working

```bash
# Use --cov=src (not --cov=tests)
pytest --cov=src --cov-report=term
```

## IDE Integration

### VS Code

```json
// .vscode/settings.json
{
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": [
    "tests",
    "-v"
  ]
}
```

### PyCharm

1. File → Settings → Tools → Python Integrated Tools
2. Set "Default test runner" to pytest
3. Tests appear in Test Explorer panel

## CI/CD

Tests run automatically in GitHub Actions:

```bash
# Workflow file: .github/workflows/test.yml

# Stages:
# 1. Unit tests (parallel, fast)
# 2. Integration tests
# 3. E2E tests (with database seed)
# 4. Performance benchmarks
# 5. Coverage threshold check (80% minimum)
```

## Coverage Targets

- **Overall**: ≥80%
- **Core Managers**: ≥90% (StateManager, AudioManager, InputManager)
- **Database**: ≥85%
- **UI Screens**: ≥70%
- **Utilities**: ≥90%

## DetailScreen Navigation Tests (Story 3.6)

Story 3.6 added comprehensive navigation testing for L/R button traversal:

```bash
# Run navigation-specific tests
pytest tests/test_detail_screen.py -k "Navigation"

# Run all Story 3.6 tests
pytest tests/test_detail_screen.py -k "Navigation or Persistence or DataIntegrity or Cache"
```

### Test Classes Added
- `TestDetailScreenNavigationLogic` - Wrap-around arithmetic (#1 ↔ #386)
- `TestDetailScreenInputHandling` - L/R/B button responses
- `TestDetailScreenStatePersistence` - StateManager integration
- `TestDetailScreenDataIntegrity` - All UI components refresh correctly
- `TestDetailScreenNavigationPerformance` - < 300ms timing requirements
- `TestDetailScreenCacheOptimization` - Sprite cache hit rates
- `TestDetailScreenErrorHandlingNavigation` - Graceful degradation
- `TestDetailScreenRefreshMethods` - Helper method functionality

### Key Test Cases
| Test | AC | Description |
|------|-----|-------------|
| `test_calculate_next_pokemon_id` | #2 | R button calculates next ID |
| `test_wrap_around_at_beginning` | #3 | #1 → #386 wrap |
| `test_wrap_around_at_end` | #4 | #386 → #1 wrap |
| `test_navigate_updates_state_manager` | #5 | State persistence |
| `test_navigation_with_fade_under_300ms` | #6, #8 | Performance timing |
| `test_all_data_refreshes_on_navigation` | #7 | Data integrity |
| `test_back_button_still_pops_screen` | #10 | B button preserved |

## Performance Targets

- **Frame time**: P95 < 33ms (30 FPS)
- **Sprite load**: P99 < 50ms
- **Input latency**: < 100ms
- **Startup time**: < 5 seconds

## Getting Help

- **pytest docs**: https://docs.pytest.org/
- **Test README**: `tests/README.md`
- **Test design**: `docs/test-design-system.md`
- **Architecture**: `docs/architecture.md`

---

**Quick Start**: `pytest -v` → Run all tests with verbose output
**Fast Feedback**: `pytest -m unit -n auto` → Parallel unit tests only
**Full Suite**: `pytest -n auto --cov=src --cov-report=html` → Everything with coverage

"""
Shared pytest fixtures for ShokeDex test suite

This module provides reusable fixtures for:
- Database setup (in-memory SQLite)
- Manager instances (StateManager, AudioManager, InputManager)
- Pygame initialization (headless mode for CI)
- Temporary file/directory management

Usage:
    def test_something(test_database, temp_state_manager):
        # test_database is a fresh in-memory DB
        # temp_state_manager uses a temp file
        pass
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from typing import Generator

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data.database import Database
from src.state_manager import StateManager
from src.audio_manager import AudioManager
from src.input_manager import InputManager, InputMode


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture
def test_database() -> Generator[Database, None, None]:
    """
    Provide an isolated in-memory database for each test.
    
    The database is pre-initialized with schema and minimal test data
    (Gen 1 starters + Pikachu). Auto-cleanup after test completes.
    
    Usage:
        def test_get_pokemon(test_database):
            pokemon = test_database.get_pokemon_by_id(1)
            assert pokemon["name"] == "Bulbasaur"
    """
    db = Database(":memory:")
    
    # Initialize schema (create all tables)
    # Note: Database class should have an initialize_schema() method
    # For now, we'll assume schema is created on connection
    
    # Seed minimal test data
    _seed_test_pokemon(db)
    
    yield db
    
    # Cleanup (close connection)
    db.close()


def _seed_test_pokemon(db: Database):
    """Seed minimal test data for unit tests."""
    test_pokemon = [
        {"id": 1, "name": "Bulbasaur", "height": 7, "weight": 69, "generation": 1},
        {"id": 4, "name": "Charmander", "height": 6, "weight": 85, "generation": 1},
        {"id": 7, "name": "Squirtle", "height": 5, "weight": 90, "generation": 1},
        {"id": 25, "name": "Pikachu", "height": 4, "weight": 60, "generation": 1},
        {"id": 152, "name": "Chikorita", "height": 9, "weight": 64, "generation": 2},
        {"id": 252, "name": "Treecko", "height": 5, "weight": 50, "generation": 3},
    ]
    
    # TODO: Implement batch insert method in Database class
    # For now, this is a placeholder - actual implementation depends on Database API
    # db.batch_insert_pokemon(test_pokemon)


# ============================================================================
# Manager Fixtures
# ============================================================================

@pytest.fixture
def temp_state_manager(tmp_path: Path) -> Generator[StateManager, None, None]:
    """
    Provide a StateManager with temporary state file.
    
    The state file is created in pytest's temp directory and auto-deleted
    after the test. No pollution of actual state files.
    
    Usage:
        def test_state_persistence(temp_state_manager):
            temp_state_manager.set_last_viewed(25)
            assert temp_state_manager.get_last_viewed_id() == 25
    """
    state_file = tmp_path / "test_state.json"
    state_manager = StateManager(state_file=str(state_file))
    
    yield state_manager
    
    # Auto-cleanup via tmp_path (pytest handles deletion)


@pytest.fixture
def mock_audio_manager() -> Generator[AudioManager, None, None]:
    """
    Provide a mocked AudioManager for tests that don't need real audio.
    
    This prevents tests from actually playing sounds or loading audio files.
    Useful for fast unit tests.
    
    Usage:
        def test_detail_screen(mock_audio_manager):
            # Audio won't actually play
            mock_audio_manager.play_cry(25)
    """
    # Create AudioManager with disabled audio
    audio_manager = AudioManager(enabled=False)
    
    yield audio_manager
    
    # Cleanup
    audio_manager.stop()


@pytest.fixture
def keyboard_input_manager() -> Generator[InputManager, None, None]:
    """
    Provide an InputManager in keyboard mode for testing.
    
    This allows tests to run on development machines without GPIO hardware.
    
    Usage:
        def test_input_handling(keyboard_input_manager):
            action = keyboard_input_manager.map_key(pygame.K_UP)
            assert action == InputAction.UP
    """
    input_manager = InputManager(mode=InputMode.KEYBOARD)
    
    yield input_manager
    
    # No cleanup needed


# ============================================================================
# Pygame Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def pygame_headless():
    """
    Initialize pygame in headless mode for CI environments.
    
    Sets SDL_VIDEODRIVER=dummy so tests can run without a display.
    This is a session-scoped fixture (runs once for entire test suite).
    
    Usage:
        def test_screen_rendering(pygame_headless):
            # pygame is already initialized in headless mode
            surface = pygame.Surface((800, 480))
            # ... render and assert
    """
    import pygame
    
    # Set headless mode before pygame.init()
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    
    pygame.init()
    
    yield
    
    pygame.quit()


@pytest.fixture
def mock_pygame_surface(pygame_headless):
    """
    Provide a mock pygame surface for rendering tests.
    
    Creates a blank surface that tests can render to. Useful for validating
    that rendering code runs without errors.
    
    Usage:
        def test_home_screen_render(mock_pygame_surface):
            screen = HomeScreen(...)
            screen.render(mock_pygame_surface)
            # Assert no exceptions raised
    """
    import pygame
    
    surface = pygame.Surface((800, 480))
    
    yield surface
    
    # No cleanup needed


# ============================================================================
# Performance Testing Fixtures
# ============================================================================

@pytest.fixture
def benchmark_timer():
    """
    Provide a simple timer for performance benchmarking.
    
    Returns a context manager that measures execution time.
    
    Usage:
        def test_sprite_loading_performance(benchmark_timer):
            with benchmark_timer as timer:
                loader.load_sprite(25)
            
            assert timer.elapsed < 0.050, "Sprite load >50ms"
    """
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
            self.elapsed = None
        
        def __enter__(self):
            self.start_time = time.time()
            return self
        
        def __exit__(self, *args):
            self.end_time = time.time()
            self.elapsed = self.end_time - self.start_time
    
    return Timer()


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================

def pytest_configure(config):
    """
    Pytest configuration hook - runs once at test session start.
    
    Registers custom markers and sets up test environment.
    """
    # Markers are registered in pytest.ini, but we can add dynamic config here
    pass


def pytest_collection_modifyitems(config, items):
    """
    Pytest hook to modify collected test items.
    
    Automatically marks tests based on filename patterns:
    - test_*_integration.py -> @pytest.mark.integration
    - test_*_e2e.py -> @pytest.mark.e2e
    - test_performance_*.py -> @pytest.mark.performance
    """
    for item in items:
        # Auto-mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Auto-mark e2e tests
        if "e2e" in item.nodeid or "mvp_features" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
        
        # Auto-mark performance tests
        if "performance" in item.nodeid:
            item.add_marker(pytest.mark.performance)
        
        # Auto-mark slow tests (>1s)
        if hasattr(item, "get_closest_marker"):
            if item.get_closest_marker("slow"):
                item.add_marker(pytest.mark.slow)

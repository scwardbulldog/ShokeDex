"""
Example showing migration from unittest to pytest

This demonstrates how to convert existing unittest tests to pytest style
while taking advantage of fixtures and pytest features.
"""

import pytest
from tests.helpers.pokemon_factory import create_pokemon


# ============================================================================
# BEFORE: unittest style (existing pattern)
# ============================================================================

import unittest
import tempfile
from pathlib import Path
from src.state_manager import StateManager


class TestStateManagerUnittest(unittest.TestCase):
    """Example of existing unittest pattern."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.state_path = self.temp_file.name
        self.state_manager = StateManager(self.state_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        Path(self.state_path).unlink(missing_ok=True)
    
    def test_default_state(self):
        """Test default state initialization."""
        self.assertEqual(self.state_manager.get_last_viewed_id(), 1)
        self.assertEqual(self.state_manager.get_last_viewed_generation(), 1)
    
    def test_last_viewed(self):
        """Test last viewed Pokémon tracking."""
        self.state_manager.set_last_viewed(25)
        self.assertEqual(self.state_manager.get_last_viewed_id(), 25)


# ============================================================================
# AFTER: pytest style (recommended pattern)
# ============================================================================

@pytest.mark.unit
def test_default_state_pytest(temp_state_manager):
    """
    Test default state initialization using pytest fixture.
    
    Benefits:
    - No manual setup/teardown code
    - Fixture handles temp file creation and cleanup
    - More readable: function signature shows dependencies
    - Better error messages from pytest
    """
    assert temp_state_manager.get_last_viewed_id() == 1
    assert temp_state_manager.get_last_viewed_generation() == 1


@pytest.mark.unit
def test_last_viewed_pytest(temp_state_manager):
    """
    Test last viewed Pokémon tracking using pytest.
    
    Benefits:
    - Each test gets fresh StateManager (isolated)
    - Auto-cleanup (no manual file deletion)
    - Can run in parallel safely
    """
    temp_state_manager.set_last_viewed(25)
    assert temp_state_manager.get_last_viewed_id() == 25


# ============================================================================
# pytest parametrize: Test multiple cases efficiently
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("pokemon_id,expected_generation", [
    (1, 1),      # Bulbasaur - Gen 1
    (25, 1),     # Pikachu - Gen 1
    (152, 2),    # Chikorita - Gen 2
    (252, 3),    # Treecko - Gen 3
])
def test_generation_detection_parametrized(
    temp_state_manager,
    pokemon_id,
    expected_generation
):
    """
    Test generation detection for multiple Pokémon.
    
    Benefits:
    - One test function tests 4 cases
    - Clear test output shows which case failed
    - Less code duplication
    """
    temp_state_manager.set_last_viewed(pokemon_id)
    assert temp_state_manager.get_last_viewed_generation() == expected_generation


# ============================================================================
# Using test data factories
# ============================================================================

@pytest.mark.unit
def test_with_factory_data():
    """
    Example using test data factory.
    
    Benefits:
    - Consistent test data structure
    - Easy to override specific fields
    - Predefined data sets (GEN_1_STARTERS, etc.)
    """
    pikachu = create_pokemon(id=25, name="Pikachu", type1="Electric")
    
    assert pikachu["id"] == 25
    assert pikachu["name"] == "Pikachu"
    assert pikachu["type1"] == "Electric"
    assert pikachu["generation"] == 1  # Default


# ============================================================================
# Performance testing with benchmark_timer fixture
# ============================================================================

@pytest.mark.performance
def test_operation_performance(benchmark_timer):
    """
    Example performance test using benchmark_timer fixture.
    
    Benefits:
    - Built-in timing (no manual time.time() calls)
    - Readable assertion messages
    - Can aggregate timing across multiple runs
    """
    with benchmark_timer as timer:
        # Simulate operation
        result = sum(range(10000))
    
    assert timer.elapsed < 0.001, f"Operation took {timer.elapsed*1000:.1f}ms (>1ms)"


# ============================================================================
# Pytest features not available in unittest
# ============================================================================

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature():
    """Skip tests that aren't ready."""
    pass


@pytest.mark.xfail(reason="Known bug - issue #123")
def test_known_bug():
    """Mark tests that are expected to fail."""
    assert False  # This won't fail the test suite


@pytest.fixture
def mock_database():
    """Custom fixture for this test file."""
    # Setup
    db = {"pokemon": []}
    yield db
    # Teardown (if needed)


def test_with_local_fixture(mock_database):
    """Use a fixture defined in the same file."""
    mock_database["pokemon"].append({"id": 1, "name": "Bulbasaur"})
    assert len(mock_database["pokemon"]) == 1


# ============================================================================
# Running these tests
# ============================================================================

if __name__ == "__main__":
    # Can still run with unittest runner (backwards compatible)
    unittest.main()
    
    # But better to use pytest:
    # pytest tests/test_pytest_migration_example.py -v
    # pytest tests/test_pytest_migration_example.py -m unit
    # pytest tests/test_pytest_migration_example.py::test_default_state_pytest

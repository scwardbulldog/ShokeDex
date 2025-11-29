"""
Tests for StateManager

Tests state persistence, favorites, preferences, and statistics tracking.
"""

import unittest
import json
import tempfile
from pathlib import Path

from src.state_manager import StateManager


class TestStateManager(unittest.TestCase):
    """Test cases for StateManager"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary state file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.state_path = self.temp_file.name
        
        # Create state manager with temp file
        self.state_manager = StateManager(self.state_path)
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temp file
        Path(self.state_path).unlink(missing_ok=True)
    
    def test_default_state(self):
        """Test default state initialization"""
        self.assertEqual(self.state_manager.get_last_viewed_id(), 1)
        self.assertEqual(self.state_manager.get_last_viewed_generation(), 1)
        self.assertEqual(self.state_manager.get_favorites(), [])
        self.assertEqual(self.state_manager.get_recent(), [])
    
    def test_last_viewed(self):
        """Test last viewed Pokémon tracking"""
        # Set last viewed
        self.state_manager.set_last_viewed(25)  # Pikachu
        self.assertEqual(self.state_manager.get_last_viewed_id(), 25)
        self.assertEqual(self.state_manager.get_last_viewed_generation(), 1)
        
        # Set with explicit generation
        self.state_manager.set_last_viewed(150, generation=1)  # Mewtwo
        self.assertEqual(self.state_manager.get_last_viewed_id(), 150)
        self.assertEqual(self.state_manager.get_last_viewed_generation(), 1)
    
    def test_generation_detection(self):
        """Test automatic generation detection"""
        # Gen 1
        self.state_manager.set_last_viewed(25)
        self.assertEqual(self.state_manager.get_last_viewed_generation(), 1)
        
        # Gen 2
        self.state_manager.set_last_viewed(152)  # Chikorita
        self.assertEqual(self.state_manager.get_last_viewed_generation(), 2)
        
        # Gen 3
        self.state_manager.set_last_viewed(252)  # Treecko
        self.assertEqual(self.state_manager.get_last_viewed_generation(), 3)
    
    def test_favorites(self):
        """Test favorites management"""
        # Add favorites
        self.state_manager.add_favorite(25)  # Pikachu
        self.state_manager.add_favorite(150)  # Mewtwo
        self.state_manager.add_favorite(249)  # Lugia
        
        favorites = self.state_manager.get_favorites()
        self.assertEqual(len(favorites), 3)
        self.assertIn(25, favorites)
        self.assertIn(150, favorites)
        self.assertIn(249, favorites)
        
        # Check is_favorite
        self.assertTrue(self.state_manager.is_favorite(25))
        self.assertFalse(self.state_manager.is_favorite(1))
        
        # Remove favorite
        self.state_manager.remove_favorite(25)
        self.assertFalse(self.state_manager.is_favorite(25))
        self.assertEqual(len(self.state_manager.get_favorites()), 2)
    
    def test_toggle_favorite(self):
        """Test toggling favorite status"""
        # Toggle on
        result = self.state_manager.toggle_favorite(25)
        self.assertTrue(result)
        self.assertTrue(self.state_manager.is_favorite(25))
        
        # Toggle off
        result = self.state_manager.toggle_favorite(25)
        self.assertFalse(result)
        self.assertFalse(self.state_manager.is_favorite(25))
    
    def test_recent_tracking(self):
        """Test recent Pokémon tracking"""
        # View several Pokémon
        for pokemon_id in [1, 2, 3, 4, 5]:
            self.state_manager.set_last_viewed(pokemon_id)
        
        recent = self.state_manager.get_recent()
        self.assertEqual(len(recent), 5)
        self.assertEqual(recent[0], 5)  # Most recent first
        self.assertEqual(recent[-1], 1)  # Oldest last
        
        # View same Pokémon again (should move to front)
        self.state_manager.set_last_viewed(2)
        recent = self.state_manager.get_recent()
        self.assertEqual(recent[0], 2)
    
    def test_recent_max_size(self):
        """Test recent list maintains max size of 10"""
        # View 15 Pokémon
        for pokemon_id in range(1, 16):
            self.state_manager.set_last_viewed(pokemon_id)
        
        recent = self.state_manager.get_recent()
        self.assertEqual(len(recent), 10)  # Max 10
        self.assertEqual(recent[0], 15)  # Most recent
        self.assertEqual(recent[-1], 6)  # 10th most recent
    
    def test_preferences(self):
        """Test preferences storage"""
        # Set preferences
        self.state_manager.set_preference('test_key', 'test_value')
        self.assertEqual(self.state_manager.get_preference('test_key'), 'test_value')
        
        # Get with default
        self.assertEqual(
            self.state_manager.get_preference('nonexistent', 'default'),
            'default'
        )
    
    def test_volume(self):
        """Test volume preference"""
        # Set volume
        self.state_manager.set_volume(0.5)
        self.assertEqual(self.state_manager.get_volume(), 0.5)
        
        # Test clamping
        self.state_manager.set_volume(1.5)  # Over max
        self.assertEqual(self.state_manager.get_volume(), 1.0)
        
        self.state_manager.set_volume(-0.5)  # Under min
        self.assertEqual(self.state_manager.get_volume(), 0.0)
    
    def test_input_mode(self):
        """Test input mode preference"""
        self.state_manager.set_input_mode('gpio')
        self.assertEqual(self.state_manager.get_input_mode(), 'gpio')
        
        self.state_manager.set_input_mode('keyboard')
        self.assertEqual(self.state_manager.get_input_mode(), 'keyboard')
        
        # Invalid mode should be ignored
        self.state_manager.set_input_mode('invalid')
        self.assertEqual(self.state_manager.get_input_mode(), 'keyboard')
    
    def test_stats(self):
        """Test statistics tracking"""
        # Increment session
        self.state_manager.increment_session()
        stats = self.state_manager.get_stats()
        self.assertEqual(stats['sessions'], 1)
        
        # Update unique viewed
        self.state_manager.update_unique_viewed(150)
        stats = self.state_manager.get_stats()
        self.assertEqual(stats['unique_viewed'], 150)
        
        # Total views increments with set_last_viewed
        initial_views = stats['total_views']
        self.state_manager.set_last_viewed(25)
        stats = self.state_manager.get_stats()
        self.assertEqual(stats['total_views'], initial_views + 1)
    
    def test_save_load(self):
        """Test state persistence"""
        # Set some state
        self.state_manager.set_last_viewed(25)
        self.state_manager.add_favorite(150)
        self.state_manager.set_volume(0.8)
        
        # Save
        self.assertTrue(self.state_manager.save_state())
        
        # Create new state manager with same file
        new_state_manager = StateManager(self.state_path)
        
        # Verify state loaded correctly
        self.assertEqual(new_state_manager.get_last_viewed_id(), 25)
        self.assertIn(150, new_state_manager.get_favorites())
        self.assertEqual(new_state_manager.get_volume(), 0.8)
    
    def test_export_import(self):
        """Test state export and import"""
        # Set some state
        self.state_manager.set_last_viewed(25)
        self.state_manager.add_favorite(150)
        
        # Export
        exported = self.state_manager.export_state()
        self.assertIsInstance(exported, str)
        
        # Parse and validate
        data = json.loads(exported)
        self.assertEqual(data['last_viewed']['pokemon_id'], 25)
        
        # Create new state manager and import
        new_state_manager = StateManager(self.state_path)
        self.assertTrue(new_state_manager.import_state(exported))
        
        # Verify
        self.assertEqual(new_state_manager.get_last_viewed_id(), 25)
        self.assertIn(150, new_state_manager.get_favorites())
    
    def test_reset_state(self):
        """Test state reset"""
        # Set some state
        self.state_manager.set_last_viewed(25)
        self.state_manager.add_favorite(150)
        
        # Reset
        self.state_manager.reset_state()
        
        # Verify back to defaults
        self.assertEqual(self.state_manager.get_last_viewed_id(), 1)
        self.assertEqual(self.state_manager.get_favorites(), [])


class TestFirstBootStateInitialization(unittest.TestCase):
    """
    Story 4.1: First Boot State Initialization Tests
    
    Tests that verify state file creation and defaults on first boot.
    """
    
    def setUp(self):
        """Set up test fixtures with temporary directory for state file"""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.state_path = Path(self.temp_dir) / "shokedex_state.json"
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove state file and temp directory
        if self.state_path.exists():
            self.state_path.unlink()
        # Remove temp directory
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_init_creates_default_state_file(self):
        """AC #1: State file created at data/shokedex_state.json on first boot"""
        # Ensure file doesn't exist
        self.assertFalse(self.state_path.exists())
        
        # Create StateManager - should create file on first boot
        state_manager = StateManager(str(self.state_path))
        
        # Verify file was created
        self.assertTrue(self.state_path.exists())
        
        # Verify file contains valid JSON
        with open(self.state_path, 'r') as f:
            state = json.load(f)
        self.assertIsInstance(state, dict)
    
    def test_default_pokemon_id_is_bulbasaur(self):
        """AC #2: pokemon_id defaults to 1 (Bulbasaur)"""
        state_manager = StateManager(str(self.state_path))
        
        self.assertEqual(state_manager.get_last_viewed_id(), 1)
    
    def test_default_generation_is_kanto(self):
        """AC #3: generation defaults to 1 (Kanto)"""
        state_manager = StateManager(str(self.state_path))
        
        self.assertEqual(state_manager.get_last_viewed_generation(), 1)
    
    def test_default_input_mode_is_keyboard(self):
        """AC #4: input_mode defaults to 'keyboard'"""
        state_manager = StateManager(str(self.state_path))
        
        self.assertEqual(state_manager.get_input_mode(), 'keyboard')
    
    def test_default_volume_is_0_7(self):
        """AC #5: volume defaults to 0.7 (70%)"""
        state_manager = StateManager(str(self.state_path))
        
        self.assertAlmostEqual(state_manager.get_volume(), 0.7, places=2)
    
    def test_state_file_json_structure(self):
        """AC #8: JSON structure contains all required fields"""
        state_manager = StateManager(str(self.state_path))
        
        # Read the file and validate structure
        with open(self.state_path, 'r') as f:
            state = json.load(f)
        
        # Verify version field
        self.assertEqual(state.get('version'), '1.0.0')
        
        # Verify last_viewed section
        self.assertIn('last_viewed', state)
        self.assertEqual(state['last_viewed'].get('pokemon_id'), 1)
        self.assertEqual(state['last_viewed'].get('generation'), 1)
        
        # Verify preferences section
        self.assertIn('preferences', state)
        self.assertEqual(state['preferences'].get('input_mode'), 'keyboard')
        self.assertAlmostEqual(state['preferences'].get('volume'), 0.7, places=2)
    
    def test_state_file_persisted_on_first_boot(self):
        """AC #1: State file exists after StateManager init (not just in memory)"""
        # Create StateManager
        state_manager = StateManager(str(self.state_path))
        
        # Delete the state_manager object to ensure we're reading from disk
        del state_manager
        
        # File should still exist
        self.assertTrue(self.state_path.exists())
        
        # Create new StateManager - should load from file
        new_state_manager = StateManager(str(self.state_path))
        
        # Verify values match defaults (loaded from persisted file)
        self.assertEqual(new_state_manager.get_last_viewed_id(), 1)
        self.assertEqual(new_state_manager.get_last_viewed_generation(), 1)


class TestDirectoryCreation(unittest.TestCase):
    """
    Story 4.1: Task 7 - Directory Creation Tests
    
    Tests that verify data/ directory is created on first boot.
    """
    
    def setUp(self):
        """Set up test fixtures with nested directory path"""
        self.temp_base = tempfile.mkdtemp()
        # Create a nested path that doesn't exist yet
        self.state_path = Path(self.temp_base) / "data" / "nested" / "shokedex_state.json"
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_base).exists():
            shutil.rmtree(self.temp_base)
    
    def test_creates_data_directory_if_missing(self):
        """AC #7: data/ directory created automatically if missing"""
        # Ensure directory doesn't exist
        self.assertFalse(self.state_path.parent.exists())
        
        # Create StateManager - should create directory
        state_manager = StateManager(str(self.state_path))
        
        # Verify directory was created
        self.assertTrue(self.state_path.parent.exists())
        
        # Verify file was created
        self.assertTrue(self.state_path.exists())
    
    def test_file_permissions_correct(self):
        """AC #7: Verify file is readable and writable by user"""
        # Create StateManager
        state_manager = StateManager(str(self.state_path))
        
        # Verify file is readable
        self.assertTrue(self.state_path.exists())
        with open(self.state_path, 'r') as f:
            content = f.read()
        self.assertTrue(len(content) > 0)
        
        # Verify file is writable (save state should succeed)
        self.assertTrue(state_manager.save_state())


class TestStatePersistenceIntegration(unittest.TestCase):
    """
    Story 1.5/4.1: State Persistence Integration Tests
    
    Tests for corruption recovery and value validation.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.state_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up test fixtures"""
        Path(self.state_path).unlink(missing_ok=True)
    
    def test_first_boot_creates_state_file(self):
        """Test first boot creates state file with defaults (AC #1)"""
        # Remove temp file to simulate first boot
        Path(self.state_path).unlink(missing_ok=True)
        
        # Create new state manager
        state_manager = StateManager(self.state_path)
        
        # Verify file was created
        self.assertTrue(Path(self.state_path).exists())
        
        # Verify defaults
        self.assertEqual(state_manager.get_last_viewed_id(), 1)
        self.assertEqual(state_manager.get_last_viewed_generation(), 1)
        self.assertEqual(state_manager.get_volume(), 0.7)
        self.assertEqual(state_manager.get_input_mode(), 'keyboard')
    
    def test_state_corruption_recovery(self):
        """Test corrupted JSON resets to defaults without crash (AC #6)"""
        # Write invalid JSON to state file
        with open(self.state_path, 'w') as f:
            f.write("{invalid json content here")
        
        # Create state manager - should not crash
        state_manager = StateManager(self.state_path)
        
        # Should load defaults
        self.assertEqual(state_manager.get_last_viewed_id(), 1)
        self.assertEqual(state_manager.get_last_viewed_generation(), 1)
        
        # Verify corrupt file was overwritten with valid defaults
        with open(self.state_path, 'r') as f:
            state = json.load(f)  # Should parse successfully now
            self.assertEqual(state['last_viewed']['pokemon_id'], 1)
    
    def test_invalid_pokemon_id_clamped(self):
        """Test invalid pokemon_id is clamped to valid range (AC #6)"""
        # Manually write invalid pokemon_id to file
        state_manager = StateManager(self.state_path)
        invalid_state = state_manager._get_default_state()
        invalid_state['last_viewed']['pokemon_id'] = 999  # Out of range
        
        with open(self.state_path, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state - should clamp value
        state_manager = StateManager(self.state_path)
        
        # Should be clamped to 386 (max valid ID)
        self.assertEqual(state_manager.get_last_viewed_id(), 386)
    
    def test_invalid_generation_clamped(self):
        """Test invalid generation is clamped to valid range (AC #6)"""
        # Manually write invalid generation to file
        state_manager = StateManager(self.state_path)
        invalid_state = state_manager._get_default_state()
        invalid_state['last_viewed']['generation'] = 5  # Out of range
        
        with open(self.state_path, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state - should clamp value
        state_manager = StateManager(self.state_path)
        
        # Should be clamped to 3 (max valid generation)
        self.assertEqual(state_manager.get_last_viewed_generation(), 3)
    
    def test_invalid_volume_clamped(self):
        """Test invalid volume is clamped to 0.0-1.0 range (AC #5, #6)"""
        state_manager = StateManager(self.state_path)
        
        # Test over max
        invalid_state = state_manager._get_default_state()
        invalid_state['preferences']['volume'] = 1.5
        
        with open(self.state_path, 'w') as f:
            json.dump(invalid_state, f)
        
        state_manager = StateManager(self.state_path)
        self.assertEqual(state_manager.get_volume(), 1.0)
        
        # Test under min
        invalid_state['preferences']['volume'] = -0.5
        
        with open(self.state_path, 'w') as f:
            json.dump(invalid_state, f)
        
        state_manager = StateManager(self.state_path)
        self.assertEqual(state_manager.get_volume(), 0.0)
    
    def test_invalid_input_mode_validation(self):
        """Test invalid input_mode defaults to keyboard (AC #5, #6)"""
        state_manager = StateManager(self.state_path)
        
        # Manually write invalid input_mode to file
        invalid_state = state_manager._get_default_state()
        invalid_state['preferences']['input_mode'] = 'invalid_mode'
        
        with open(self.state_path, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state - should default to keyboard
        state_manager = StateManager(self.state_path)
        
        self.assertEqual(state_manager.get_input_mode(), 'keyboard')


if __name__ == '__main__':
    unittest.main()

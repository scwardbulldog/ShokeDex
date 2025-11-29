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


class TestLastViewedPokemonPersistence(unittest.TestCase):
    """
    Story 4.2: Last Viewed Pokémon Persistence Tests
    
    Tests for state save/restore across screen transitions and app restarts.
    """
    
    def setUp(self):
        """Set up test fixtures with temporary directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_path = Path(self.temp_dir) / "shokedex_state.json"
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_set_last_viewed_updates_memory(self):
        """AC #6: set_last_viewed() updates in-memory state immediately (Task 5.1)"""
        state_manager = StateManager(str(self.state_path))
        
        # Initial state is Bulbasaur
        self.assertEqual(state_manager.get_last_viewed_id(), 1)
        
        # Update to Pikachu
        state_manager.set_last_viewed(25, generation=1)
        
        # Verify in-memory state changed immediately
        self.assertEqual(state_manager.get_last_viewed_id(), 25)
        self.assertEqual(state_manager.get_last_viewed_generation(), 1)
    
    def test_save_state_persists_to_file(self):
        """AC #1, #2: save_state() persists to JSON file (Task 5.2)"""
        state_manager = StateManager(str(self.state_path))
        
        # Update state
        state_manager.set_last_viewed(25, generation=1)
        
        # Save to file
        result = state_manager.save_state()
        self.assertTrue(result)
        
        # Verify file contents
        with open(self.state_path, 'r') as f:
            saved_state = json.load(f)
        
        self.assertEqual(saved_state['last_viewed']['pokemon_id'], 25)
        self.assertEqual(saved_state['last_viewed']['generation'], 1)
    
    def test_get_last_viewed_id_returns_saved(self):
        """AC #3: getter returns saved value after restart (Task 5.3)"""
        # Create first state manager and save Pikachu
        state_manager1 = StateManager(str(self.state_path))
        state_manager1.set_last_viewed(25, generation=1)
        state_manager1.save_state()
        
        # Simulate restart by creating new StateManager
        state_manager2 = StateManager(str(self.state_path))
        
        # Verify restored values
        self.assertEqual(state_manager2.get_last_viewed_id(), 25)
        self.assertEqual(state_manager2.get_last_viewed_generation(), 1)
    
    def test_generation_auto_detection_gen1(self):
        """AC #6, #7: Auto-detect Gen 1 for IDs 1-151 (Task 5.4)"""
        state_manager = StateManager(str(self.state_path))
        
        # Test Gen 1 boundaries
        state_manager.set_last_viewed(1)  # Bulbasaur
        self.assertEqual(state_manager.get_last_viewed_generation(), 1)
        
        state_manager.set_last_viewed(151)  # Mew
        self.assertEqual(state_manager.get_last_viewed_generation(), 1)
        
        state_manager.set_last_viewed(25)  # Pikachu
        self.assertEqual(state_manager.get_last_viewed_generation(), 1)
    
    def test_generation_auto_detection_gen2(self):
        """AC #6, #7: Auto-detect Gen 2 for IDs 152-251 (Task 5.4)"""
        state_manager = StateManager(str(self.state_path))
        
        # Test Gen 2 boundaries
        state_manager.set_last_viewed(152)  # Chikorita
        self.assertEqual(state_manager.get_last_viewed_generation(), 2)
        
        state_manager.set_last_viewed(251)  # Celebi
        self.assertEqual(state_manager.get_last_viewed_generation(), 2)
        
        state_manager.set_last_viewed(200)  # Misdreavus
        self.assertEqual(state_manager.get_last_viewed_generation(), 2)
    
    def test_generation_auto_detection_gen3(self):
        """AC #6, #7: Auto-detect Gen 3 for IDs 252-386 (Task 5.4)"""
        state_manager = StateManager(str(self.state_path))
        
        # Test Gen 3 boundaries
        state_manager.set_last_viewed(252)  # Treecko
        self.assertEqual(state_manager.get_last_viewed_generation(), 3)
        
        state_manager.set_last_viewed(386)  # Deoxys
        self.assertEqual(state_manager.get_last_viewed_generation(), 3)
        
        state_manager.set_last_viewed(300)  # Skitty
        self.assertEqual(state_manager.get_last_viewed_generation(), 3)
    
    def test_cross_generation_persistence_johto(self):
        """AC #4: Johto (Gen 2) state persists across restart (Task 5.5)"""
        # Save Chikorita in Johto
        state_manager1 = StateManager(str(self.state_path))
        state_manager1.set_last_viewed(152, generation=2)
        state_manager1.save_state()
        
        # Simulate restart
        state_manager2 = StateManager(str(self.state_path))
        
        # Verify Johto restored
        self.assertEqual(state_manager2.get_last_viewed_id(), 152)
        self.assertEqual(state_manager2.get_last_viewed_generation(), 2)
    
    def test_cross_generation_persistence_hoenn(self):
        """AC #5: Hoenn (Gen 3) state persists across restart (Task 5.5)"""
        # Save Treecko in Hoenn
        state_manager1 = StateManager(str(self.state_path))
        state_manager1.set_last_viewed(252, generation=3)
        state_manager1.save_state()
        
        # Simulate restart
        state_manager2 = StateManager(str(self.state_path))
        
        # Verify Hoenn restored
        self.assertEqual(state_manager2.get_last_viewed_id(), 252)
        self.assertEqual(state_manager2.get_last_viewed_generation(), 3)
    
    def test_atomic_write_creates_temp_file(self):
        """AC #2: save_state() uses atomic write with temp file"""
        state_manager = StateManager(str(self.state_path))
        state_manager.set_last_viewed(25, generation=1)
        
        # Save state
        result = state_manager.save_state()
        self.assertTrue(result)
        
        # Verify final file exists
        self.assertTrue(self.state_path.exists())
        
        # Temp file should be cleaned up after rename
        temp_path = Path(str(self.state_path) + '.tmp')
        self.assertFalse(temp_path.exists())


class TestStatePersistencePerformance(unittest.TestCase):
    """
    Story 4.2: Performance Validation Tests (AC #8)
    
    Tests that save/load operations meet < 50ms target.
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_path = Path(self.temp_dir) / "shokedex_state.json"
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_save_state_performance(self):
        """AC #8: save_state() completes in < 50ms (Task 7.2)"""
        import time
        
        state_manager = StateManager(str(self.state_path))
        state_manager.set_last_viewed(25, generation=1)
        
        # Time 100 iterations
        start = time.perf_counter()
        for _ in range(100):
            state_manager.save_state()
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        avg_time = elapsed / 100
        self.assertLess(avg_time, 50, f"Average save time {avg_time:.2f}ms exceeds 50ms target")
    
    def test_load_state_performance(self):
        """AC #8: _load_state() completes in < 50ms (Task 7.3)"""
        import time
        
        # Create initial state file
        state_manager = StateManager(str(self.state_path))
        state_manager.set_last_viewed(25, generation=1)
        state_manager.save_state()
        
        # Time 100 load operations
        start = time.perf_counter()
        for _ in range(100):
            new_manager = StateManager(str(self.state_path))
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        avg_time = elapsed / 100
        self.assertLess(avg_time, 50, f"Average load time {avg_time:.2f}ms exceeds 50ms target")
    
    def test_navigation_state_update_performance(self):
        """AC #8: set_last_viewed() is fast enough for real-time navigation"""
        import time
        
        state_manager = StateManager(str(self.state_path))
        
        # Simulate rapid navigation (1000 state updates)
        start = time.perf_counter()
        for pokemon_id in range(1, 387):  # All Gen 1-3 Pokemon
            state_manager.set_last_viewed(pokemon_id)
        elapsed = (time.perf_counter() - start) * 1000  # ms
        
        # Should complete all 386 updates in well under 1 second
        self.assertLess(elapsed, 1000, f"Navigation updates took {elapsed:.2f}ms")
        
        # Each update should be sub-millisecond
        avg_time = elapsed / 386
        self.assertLess(avg_time, 1, f"Average update time {avg_time:.3f}ms is too slow")


if __name__ == '__main__':
    unittest.main()


# =============================================================================
# Story 4.4: Volume and Input Mode Preferences Tests
# =============================================================================

class TestVolumePreference:
    """
    Story 4.4: Volume Preference Tests
    
    Tests for volume preference persistence and validation (AC #1, #2, #5, #7).
    """
    
    def test_set_and_get_volume(self, temp_state_manager):
        """AC #1, #2: Set volume and verify getter returns same value (Task 4.1)"""
        temp_state_manager.set_volume(0.5)
        assert temp_state_manager.get_volume() == 0.5
        
        temp_state_manager.set_volume(0.0)
        assert temp_state_manager.get_volume() == 0.0
        
        temp_state_manager.set_volume(1.0)
        assert temp_state_manager.get_volume() == 1.0
    
    def test_volume_clamping_low(self, temp_state_manager):
        """AC #5: Negative volume clamped to 0.0 (Task 4.2)"""
        temp_state_manager.set_volume(-0.5)
        assert temp_state_manager.get_volume() == 0.0
        
        temp_state_manager.set_volume(-1.0)
        assert temp_state_manager.get_volume() == 0.0
        
        temp_state_manager.set_volume(-0.001)
        assert temp_state_manager.get_volume() == 0.0
    
    def test_volume_clamping_high(self, temp_state_manager):
        """AC #5: Volume > 1.0 clamped to 1.0 (Task 4.3)"""
        temp_state_manager.set_volume(1.5)
        assert temp_state_manager.get_volume() == 1.0
        
        temp_state_manager.set_volume(2.0)
        assert temp_state_manager.get_volume() == 1.0
        
        temp_state_manager.set_volume(1.001)
        assert temp_state_manager.get_volume() == 1.0
    
    def test_volume_boundary_values(self, temp_state_manager):
        """AC #5: Boundary values preserved unchanged"""
        # Exact boundaries should be preserved
        temp_state_manager.set_volume(0.0)
        assert temp_state_manager.get_volume() == 0.0
        
        temp_state_manager.set_volume(1.0)
        assert temp_state_manager.get_volume() == 1.0
        
        # Near boundaries should be preserved
        temp_state_manager.set_volume(0.001)
        assert abs(temp_state_manager.get_volume() - 0.001) < 0.0001
        
        temp_state_manager.set_volume(0.999)
        assert abs(temp_state_manager.get_volume() - 0.999) < 0.0001
    
    def test_volume_persists_through_save_reload(self, tmp_path):
        """AC #1, #2: Volume persists through save_state() and reload (Task 4.4)"""
        state_file = tmp_path / "test_state.json"
        
        # Create first StateManager, set volume, save
        sm1 = StateManager(str(state_file))
        sm1.set_volume(0.5)
        sm1.save_state()
        
        # Create NEW StateManager with same file path
        sm2 = StateManager(str(state_file))
        
        # Verify volume persisted
        assert sm2.get_volume() == 0.5
    
    def test_volume_validation_on_load(self, tmp_path, caplog):
        """AC #7: Invalid volume in file is clamped on load (Task 4.5)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Create initial state with invalid volume
        invalid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 2.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state - should clamp and log warning
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Verify volume was clamped to 1.0
        assert sm.get_volume() == 1.0
        
        # Verify warning was logged
        assert any("volume" in record.message.lower() and "clamped" in record.message.lower() 
                  for record in caplog.records)
    
    def test_volume_validation_on_load_negative(self, tmp_path, caplog):
        """AC #7: Negative volume in file is clamped to 0.0 on load"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Create initial state with negative volume
        invalid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": -0.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state - should clamp to 0.0
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Verify volume was clamped to 0.0
        assert sm.get_volume() == 0.0
    
    def test_volume_default_value(self, tmp_path):
        """AC #1: New state file has volume=0.7 (Task 4.6)"""
        state_file = tmp_path / "test_state.json"
        
        # Ensure file doesn't exist
        assert not state_file.exists()
        
        # Create new StateManager
        sm = StateManager(str(state_file))
        
        # Verify default volume is 0.7
        assert sm.get_volume() == 0.7
    
    def test_volume_corrected_file_written_back(self, tmp_path):
        """AC #7: Corrected volume value written back to state file"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Create initial state with invalid volume
        invalid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 2.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state (triggers correction)
        sm = StateManager(str(state_file))
        
        # Verify corrected value was written back to file
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state['preferences']['volume'] == 1.0


class TestInputModePreference:
    """
    Story 4.4: Input Mode Preference Tests
    
    Tests for input mode preference persistence and validation (AC #3, #4, #6).
    """
    
    def test_set_and_get_input_mode_keyboard(self, temp_state_manager):
        """AC #3, #4: Set input_mode="keyboard" and verify (Task 5.1)"""
        temp_state_manager.set_input_mode('keyboard')
        assert temp_state_manager.get_input_mode() == 'keyboard'
    
    def test_set_and_get_input_mode_gpio(self, temp_state_manager):
        """AC #3, #4: Set input_mode="gpio" and verify (Task 5.2)"""
        temp_state_manager.set_input_mode('gpio')
        assert temp_state_manager.get_input_mode() == 'gpio'
    
    def test_input_mode_invalid_ignored(self, temp_state_manager):
        """AC #6: Invalid mode values are silently ignored (Task 5.3)"""
        # Set a valid mode first
        temp_state_manager.set_input_mode('gpio')
        
        # Try to set invalid mode - should be ignored
        temp_state_manager.set_input_mode('touchscreen')
        assert temp_state_manager.get_input_mode() == 'gpio'
        
        temp_state_manager.set_input_mode('joystick')
        assert temp_state_manager.get_input_mode() == 'gpio'
        
        temp_state_manager.set_input_mode('')
        assert temp_state_manager.get_input_mode() == 'gpio'
    
    def test_input_mode_case_sensitive(self, temp_state_manager):
        """AC #6: Input mode is case-sensitive - uppercase rejected"""
        temp_state_manager.set_input_mode('keyboard')
        
        # Uppercase should be rejected
        temp_state_manager.set_input_mode('GPIO')
        assert temp_state_manager.get_input_mode() == 'keyboard'
        
        temp_state_manager.set_input_mode('KEYBOARD')
        assert temp_state_manager.get_input_mode() == 'keyboard'
        
        temp_state_manager.set_input_mode('Gpio')
        assert temp_state_manager.get_input_mode() == 'keyboard'
    
    def test_input_mode_persists_through_save_reload(self, tmp_path):
        """AC #3, #4: Input mode persists through save and reload (Task 5.4)"""
        state_file = tmp_path / "test_state.json"
        
        # Create first StateManager, set gpio, save
        sm1 = StateManager(str(state_file))
        sm1.set_input_mode('gpio')
        sm1.save_state()
        
        # Create NEW StateManager with same file path
        sm2 = StateManager(str(state_file))
        
        # Verify input_mode persisted
        assert sm2.get_input_mode() == 'gpio'
    
    def test_input_mode_validation_on_load(self, tmp_path, caplog):
        """AC #6: Invalid input_mode in file resets to "keyboard" (Task 5.5)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Create initial state with invalid input_mode
        invalid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "touchscreen", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state - should default to keyboard and log warning
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Verify input_mode was reset to keyboard
        assert sm.get_input_mode() == 'keyboard'
        
        # Verify warning was logged
        assert any("input_mode" in record.message.lower() and "keyboard" in record.message.lower()
                  for record in caplog.records)
    
    def test_input_mode_default_value(self, tmp_path):
        """AC #3: New state file has input_mode="keyboard" (Task 5.6)"""
        state_file = tmp_path / "test_state.json"
        
        # Ensure file doesn't exist
        assert not state_file.exists()
        
        # Create new StateManager
        sm = StateManager(str(state_file))
        
        # Verify default input_mode is "keyboard"
        assert sm.get_input_mode() == 'keyboard'
    
    def test_input_mode_corrected_file_written_back(self, tmp_path):
        """AC #6: Corrected input_mode value written back to state file"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Create initial state with invalid input_mode
        invalid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "invalid_mode", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state (triggers correction)
        sm = StateManager(str(state_file))
        
        # Verify corrected value was written back to file
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state['preferences']['input_mode'] == 'keyboard'


class TestPreferencesPowerCycle:
    """
    Story 4.4: Power Cycle Simulation Tests
    
    Integration test for preferences surviving application restart (AC #8).
    """
    
    def test_preferences_survive_power_cycle(self, tmp_path):
        """AC #8: Both preferences restored after save/restart cycle (Task 6.1)"""
        state_file = tmp_path / "test_state.json"
        
        # Create StateManager with temp file
        sm1 = StateManager(str(state_file))
        
        # Set volume=0.3, input_mode="gpio"
        sm1.set_volume(0.3)
        sm1.set_input_mode('gpio')
        
        # Call save_state()
        sm1.save_state()
        
        # Create NEW StateManager instance with same file path (simulates power cycle)
        sm2 = StateManager(str(state_file))
        
        # Verify get_volume() returns 0.3
        assert sm2.get_volume() == 0.3
        
        # Verify get_input_mode() returns "gpio"
        assert sm2.get_input_mode() == 'gpio'
    
    def test_multiple_preference_changes_persist(self, tmp_path):
        """AC #8: Multiple preference changes all persist"""
        state_file = tmp_path / "test_state.json"
        
        # Create and modify StateManager multiple times
        sm1 = StateManager(str(state_file))
        sm1.set_volume(0.1)
        sm1.set_input_mode('keyboard')
        sm1.save_state()
        
        # Modify again
        sm2 = StateManager(str(state_file))
        sm2.set_volume(0.9)
        sm2.set_input_mode('gpio')
        sm2.save_state()
        
        # Final reload should have latest values
        sm3 = StateManager(str(state_file))
        assert sm3.get_volume() == 0.9
        assert sm3.get_input_mode() == 'gpio'
    
    def test_preferences_with_other_state_data(self, tmp_path):
        """AC #8: Preferences persist alongside other state data"""
        state_file = tmp_path / "test_state.json"
        
        # Create StateManager and set various state
        sm1 = StateManager(str(state_file))
        sm1.set_last_viewed(25, generation=1)  # Pikachu
        sm1.add_favorite(150)  # Mewtwo
        sm1.set_volume(0.5)
        sm1.set_input_mode('gpio')
        sm1.save_state()
        
        # Create new StateManager
        sm2 = StateManager(str(state_file))
        
        # Verify all state restored
        assert sm2.get_last_viewed_id() == 25
        assert sm2.is_favorite(150)
        assert sm2.get_volume() == 0.5
        assert sm2.get_input_mode() == 'gpio'


class TestValidationLogging:
    """
    Story 4.4: Validation Warning Logging Tests
    
    Tests for proper warning logs during validation (AC #6, #7).
    """
    
    def test_invalid_volume_logs_warning(self, tmp_path, caplog):
        """AC #7: Loading invalid volume logs warning with clamped values (Task 7.1)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Create state with invalid volume
        invalid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 2.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state with log capture
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Find the volume warning
        volume_warnings = [r for r in caplog.records 
                         if 'volume' in r.message.lower() and r.levelno == logging.WARNING]
        
        assert len(volume_warnings) >= 1, "Expected warning log for invalid volume"
        
        # Verify warning mentions both original and clamped value
        warning_msg = volume_warnings[0].message.lower()
        assert '2.5' in warning_msg or 'out of range' in warning_msg
        assert '1.0' in warning_msg or 'clamped' in warning_msg
    
    def test_invalid_input_mode_logs_warning(self, tmp_path, caplog):
        """AC #6: Loading invalid input_mode logs warning about reset (Task 7.2)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Create state with invalid input_mode
        invalid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "invalid_mode", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(invalid_state, f)
        
        # Load state with log capture
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Find the input_mode warning
        mode_warnings = [r for r in caplog.records 
                        if 'input_mode' in r.message.lower() and r.levelno == logging.WARNING]
        
        assert len(mode_warnings) >= 1, "Expected warning log for invalid input_mode"
        
        # Verify warning mentions keyboard default
        warning_msg = mode_warnings[0].message.lower()
        assert 'keyboard' in warning_msg or 'default' in warning_msg
    
    def test_valid_values_no_warnings(self, tmp_path, caplog):
        """AC #6, #7: Valid values do not trigger warnings (Task 7.3)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Create state with valid values
        valid_state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 25, "generation": 1},
            "preferences": {"input_mode": "gpio", "volume": 0.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(valid_state, f)
        
        # Load state with log capture
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Filter for preference-related warnings
        pref_warnings = [r for r in caplog.records 
                        if r.levelno == logging.WARNING and 
                        ('volume' in r.message.lower() or 'input_mode' in r.message.lower())]
        
        assert len(pref_warnings) == 0, f"Unexpected warnings: {[r.message for r in pref_warnings]}"


# =============================================================================
# Story 4.5: State File Corruption Recovery Tests
# =============================================================================

class TestCorruptionRecovery:
    """
    Story 4.5: Corruption Recovery Tests
    
    Tests for graceful recovery from corrupted state files (AC #1-4).
    """
    
    def test_corrupt_json_does_not_crash(self, tmp_path):
        """AC #1: Application does not crash on corrupted JSON (Task 3.1)"""
        state_file = tmp_path / "test_state.json"
        
        # Write invalid JSON
        with open(state_file, 'w') as f:
            f.write("{invalid json content here")
        
        # Should not raise exception
        sm = StateManager(str(state_file))
        
        # Verify StateManager is functional
        assert sm is not None
        assert sm.get_last_viewed_id() is not None
    
    def test_corrupt_json_returns_defaults(self, tmp_path):
        """AC #2: Corrupted JSON returns default values (Task 3.2)"""
        state_file = tmp_path / "test_state.json"
        
        # Write invalid JSON
        with open(state_file, 'w') as f:
            f.write("{this is not valid json}")
        
        # Create StateManager - should recover with defaults
        sm = StateManager(str(state_file))
        
        # Verify default values
        assert sm.get_last_viewed_id() == 1  # Bulbasaur
        assert sm.get_last_viewed_generation() == 1  # Kanto
        assert sm.get_input_mode() == 'keyboard'
        assert sm.get_volume() == 0.7
    
    def test_corrupt_json_overwrites_file(self, tmp_path):
        """AC #3: Corrupt file overwritten with valid defaults (Task 3.3)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Write invalid JSON
        with open(state_file, 'w') as f:
            f.write("{broken json}")
        
        # Create StateManager - should overwrite corrupt file
        sm = StateManager(str(state_file))
        
        # Verify file now contains valid JSON
        with open(state_file, 'r') as f:
            state = json.load(f)  # Should not raise JSONDecodeError
        
        # Verify file contains expected fields
        assert state['version'] == '1.0.0'
        assert state['last_viewed']['pokemon_id'] == 1
        assert state['last_viewed']['generation'] == 1
        assert state['preferences']['input_mode'] == 'keyboard'
        assert state['preferences']['volume'] == 0.7
    
    def test_corrupt_json_logs_warning(self, tmp_path, caplog):
        """AC #4: Warning logged on corruption (Task 3.4)"""
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Write invalid JSON
        with open(state_file, 'w') as f:
            f.write("{invalid json}")
        
        # Load with log capture
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Verify warning was logged
        corruption_warnings = [r for r in caplog.records 
                              if 'corrupted' in r.message.lower() and r.levelno == logging.WARNING]
        
        assert len(corruption_warnings) >= 1, "Expected warning log for corruption"
        
        # Verify message format includes "resetting to defaults"
        warning_msg = corruption_warnings[0].message.lower()
        assert 'defaults' in warning_msg
    
    def test_truncated_json_handled(self, tmp_path):
        """AC #1: Truncated JSON is handled gracefully (Task 3.5)"""
        state_file = tmp_path / "test_state.json"
        
        # Write truncated JSON
        with open(state_file, 'w') as f:
            f.write('{"version": "1.0.0", "last_viewed": {"pokemon_id": 25')
        
        # Should not crash, should return defaults
        sm = StateManager(str(state_file))
        
        assert sm.get_last_viewed_id() == 1  # Default, not 25
        assert sm.get_volume() == 0.7
    
    def test_empty_file_handled(self, tmp_path):
        """AC #1: Empty file is handled gracefully (Task 3.6)"""
        state_file = tmp_path / "test_state.json"
        
        # Create empty file
        state_file.touch()
        assert state_file.stat().st_size == 0
        
        # Should not crash, should return defaults
        sm = StateManager(str(state_file))
        
        assert sm.get_last_viewed_id() == 1
        assert sm.get_volume() == 0.7
    
    def test_binary_garbage_handled(self, tmp_path):
        """AC #1: Binary garbage is handled gracefully"""
        state_file = tmp_path / "test_state.json"
        
        # Write random bytes
        with open(state_file, 'wb') as f:
            f.write(bytes([0x00, 0xFF, 0x80, 0x7F, 0xAB, 0xCD]))
        
        # Should not crash, should return defaults
        sm = StateManager(str(state_file))
        
        assert sm.get_last_viewed_id() == 1
        assert sm.get_volume() == 0.7
    
    def test_non_json_text_handled(self, tmp_path):
        """AC #1: Non-JSON text file is handled gracefully"""
        state_file = tmp_path / "test_state.json"
        
        # Write plain text (not JSON)
        with open(state_file, 'w') as f:
            f.write("Hello World, this is not JSON!")
        
        # Should not crash, should return defaults
        sm = StateManager(str(state_file))
        
        assert sm.get_last_viewed_id() == 1
        assert sm.get_volume() == 0.7


class TestPokemonIdValidation:
    """
    Story 4.5: Pokemon ID Validation Tests
    
    Tests for pokemon_id clamping to valid range 1-386 (AC #5, #9).
    """
    
    def test_pokemon_id_above_max_clamped(self, tmp_path, caplog):
        """AC #5: pokemon_id=999 clamped to 386 (Task 4.1)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        # Create state with invalid pokemon_id
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 999, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Load and verify clamping
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        assert sm.get_last_viewed_id() == 386
        
        # Verify warning logged
        id_warnings = [r for r in caplog.records if 'pokemon_id' in r.message.lower()]
        assert len(id_warnings) >= 1
    
    def test_pokemon_id_below_min_clamped(self, tmp_path):
        """AC #9: pokemon_id=-5 clamped to 1 (Task 4.2)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": -5, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_id() == 1
    
    def test_pokemon_id_zero_clamped(self, tmp_path):
        """AC #9: pokemon_id=0 clamped to 1 (Task 4.3)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 0, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_id() == 1
    
    def test_pokemon_id_valid_unchanged(self, tmp_path):
        """AC #5: Valid pokemon_id=25 remains unchanged (Task 4.4)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 25, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_id() == 25
    
    def test_pokemon_id_boundary_values(self, tmp_path):
        """AC #5: Boundary values 1 and 386 unchanged (Task 4.5)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Test min boundary (1)
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_id() == 1
        
        # Test max boundary (386)
        state['last_viewed']['pokemon_id'] = 386
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_id() == 386
    
    def test_pokemon_id_corrected_written_back(self, tmp_path):
        """AC #5: Corrected pokemon_id written back to file"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 999, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Load (triggers correction)
        sm = StateManager(str(state_file))
        
        # Verify corrected value written back
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state['last_viewed']['pokemon_id'] == 386


class TestGenerationValidation:
    """
    Story 4.5: Generation Validation Tests
    
    Tests for generation clamping to valid range 1-3 (AC #6, #9).
    """
    
    def test_generation_above_max_clamped(self, tmp_path, caplog):
        """AC #6: generation=5 clamped to 3 (Task 5.1)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 5},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        assert sm.get_last_viewed_generation() == 3
        
        # Verify warning logged
        gen_warnings = [r for r in caplog.records if 'generation' in r.message.lower()]
        assert len(gen_warnings) >= 1
    
    def test_generation_below_min_clamped(self, tmp_path):
        """AC #9: generation=-1 clamped to 1 (Task 5.2)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": -1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_generation() == 1
    
    def test_generation_zero_clamped(self, tmp_path):
        """AC #9: generation=0 clamped to 1 (Task 5.3)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 0},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_generation() == 1
    
    def test_generation_valid_unchanged(self, tmp_path):
        """AC #6: Valid generation=2 remains unchanged (Task 5.4)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 2},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_generation() == 2
    
    def test_generation_boundary_values(self, tmp_path):
        """AC #6: Boundary values 1 and 3 unchanged (Task 5.5)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Test min boundary (1)
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_generation() == 1
        
        # Test max boundary (3)
        state['last_viewed']['generation'] = 3
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_last_viewed_generation() == 3
    
    def test_generation_corrected_written_back(self, tmp_path):
        """AC #6: Corrected generation written back to file"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 5},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Load (triggers correction)
        sm = StateManager(str(state_file))
        
        # Verify corrected value written back
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state['last_viewed']['generation'] == 3


class TestVolumeValidationOnLoad:
    """
    Story 4.5: Volume Validation on Load Tests
    
    Tests for volume clamping to valid range 0.0-1.0 on load (AC #7, #9).
    """
    
    def test_volume_above_max_clamped_on_load(self, tmp_path, caplog):
        """AC #7: volume=2.5 clamped to 1.0 on load (Task 6.1)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 2.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        assert sm.get_volume() == 1.0
        
        # Verify warning logged
        vol_warnings = [r for r in caplog.records if 'volume' in r.message.lower()]
        assert len(vol_warnings) >= 1
    
    def test_volume_below_min_clamped_on_load(self, tmp_path):
        """AC #9: volume=-0.5 clamped to 0.0 on load (Task 6.2)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": -0.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_volume() == 0.0
    
    def test_volume_valid_unchanged_on_load(self, tmp_path):
        """AC #7: Valid volume=0.5 unchanged on load (Task 6.3)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_volume() == 0.5
    
    def test_volume_boundary_values_on_load(self, tmp_path):
        """AC #7: Boundary values 0.0 and 1.0 unchanged on load (Task 6.4)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Test min boundary (0.0)
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.0},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_volume() == 0.0
        
        # Test max boundary (1.0)
        state['preferences']['volume'] = 1.0
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_volume() == 1.0
    
    def test_volume_string_coerced(self, tmp_path):
        """AC #7: Volume as string "0.5" coerced to float (Task 6.5)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": "0.5"},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_volume() == 0.5
        assert isinstance(sm.get_volume(), float)


class TestInputModeValidationOnLoad:
    """
    Story 4.5: Input Mode Validation on Load Tests
    
    Tests for input_mode validation on load (AC #8).
    """
    
    def test_input_mode_invalid_reset_to_keyboard(self, tmp_path, caplog):
        """AC #8: input_mode="touchscreen" reset to "keyboard" (Task 7.1)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "touchscreen", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        assert sm.get_input_mode() == 'keyboard'
        
        # Verify warning logged
        mode_warnings = [r for r in caplog.records if 'input_mode' in r.message.lower()]
        assert len(mode_warnings) >= 1
    
    def test_input_mode_empty_string_reset(self, tmp_path):
        """AC #8: input_mode="" reset to "keyboard" (Task 7.2)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_input_mode() == 'keyboard'
    
    def test_input_mode_case_sensitive_on_load(self, tmp_path):
        """AC #8: input_mode="GPIO" (uppercase) reset to "keyboard" (Task 7.3)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "GPIO", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_input_mode() == 'keyboard'
    
    def test_input_mode_valid_keyboard_unchanged(self, tmp_path):
        """AC #8: Valid input_mode="keyboard" unchanged (Task 7.4)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_input_mode() == 'keyboard'
    
    def test_input_mode_valid_gpio_unchanged(self, tmp_path):
        """AC #8: Valid input_mode="gpio" unchanged (Task 7.5)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "gpio", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        assert sm.get_input_mode() == 'gpio'
    
    def test_input_mode_corrected_written_back(self, tmp_path):
        """AC #8: Corrected input_mode written back to file"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "touchscreen", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Load (triggers correction)
        sm = StateManager(str(state_file))
        
        # Verify corrected value written back
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state['preferences']['input_mode'] == 'keyboard'


class TestValidationWarningLogs:
    """
    Story 4.5: Validation Warning Log Tests
    
    Tests for proper warning log messages (AC #4, #5, #6, #7, #8).
    """
    
    def test_corrupt_json_warning_format(self, tmp_path, caplog):
        """AC #4: Corrupt JSON warning contains expected message (Task 8.1)"""
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        with open(state_file, 'w') as f:
            f.write("{not valid json}")
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Find corruption warning
        warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
        corruption_warning = next(
            (r for r in warnings if 'corrupted' in r.message.lower()), 
            None
        )
        
        assert corruption_warning is not None, "Expected corruption warning"
        assert 'resetting' in corruption_warning.message.lower() or 'defaults' in corruption_warning.message.lower()
    
    def test_pokemon_id_clamping_warning_format(self, tmp_path, caplog):
        """AC #5: pokemon_id clamping warning contains original and clamped values (Task 8.2)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 999, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Find pokemon_id warning
        id_warning = next(
            (r for r in caplog.records if 'pokemon_id' in r.message.lower()),
            None
        )
        
        assert id_warning is not None, "Expected pokemon_id warning"
        assert '999' in id_warning.message
        assert '386' in id_warning.message
    
    def test_generation_clamping_warning_format(self, tmp_path, caplog):
        """AC #6: generation clamping warning contains original and clamped values (Task 8.3)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 5},
            "preferences": {"input_mode": "keyboard", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Find generation warning
        gen_warning = next(
            (r for r in caplog.records if 'generation' in r.message.lower()),
            None
        )
        
        assert gen_warning is not None, "Expected generation warning"
        assert '5' in gen_warning.message
        assert '3' in gen_warning.message
    
    def test_volume_clamping_warning_format(self, tmp_path, caplog):
        """AC #7: volume clamping warning contains original and clamped values (Task 8.4)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "keyboard", "volume": 2.5},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Find volume warning
        vol_warning = next(
            (r for r in caplog.records if 'volume' in r.message.lower()),
            None
        )
        
        assert vol_warning is not None, "Expected volume warning"
        assert '2.5' in vol_warning.message
        assert '1.0' in vol_warning.message
    
    def test_input_mode_reset_warning_format(self, tmp_path, caplog):
        """AC #8: input_mode reset warning contains invalid value and default (Task 8.5)"""
        import json
        import logging
        
        state_file = tmp_path / "test_state.json"
        
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 1, "generation": 1},
            "preferences": {"input_mode": "touchscreen", "volume": 0.7},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        with caplog.at_level(logging.WARNING):
            sm = StateManager(str(state_file))
        
        # Find input_mode warning
        mode_warning = next(
            (r for r in caplog.records if 'input_mode' in r.message.lower()),
            None
        )
        
        assert mode_warning is not None, "Expected input_mode warning"
        assert 'touchscreen' in mode_warning.message
        assert 'keyboard' in mode_warning.message


class TestFullRecoveryFlow:
    """
    Story 4.5: Full Recovery Flow Integration Tests
    
    Tests for application continuing normally after recovery (AC #10).
    """
    
    def test_recovery_allows_normal_operation(self, tmp_path):
        """AC #10: After recovery, normal operations work (Task 9.1)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Write corrupt JSON
        with open(state_file, 'w') as f:
            f.write("{corrupt data}")
        
        # Initialize StateManager (triggers recovery)
        sm1 = StateManager(str(state_file))
        
        # Verify defaults loaded
        assert sm1.get_last_viewed_id() == 1
        
        # Simulate navigation: set_last_viewed(25, 1)
        sm1.set_last_viewed(25, 1)
        assert sm1.get_last_viewed_id() == 25
        
        # Save state
        sm1.save_state()
        
        # Create new StateManager with same file
        sm2 = StateManager(str(state_file))
        
        # Verify Pikachu (#25) restored correctly
        assert sm2.get_last_viewed_id() == 25
        assert sm2.get_last_viewed_generation() == 1
    
    def test_recovery_file_usable_after_overwrite(self, tmp_path):
        """AC #10: Recovered file is valid and usable JSON (Task 9.2)"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Write corrupt JSON
        with open(state_file, 'w') as f:
            f.write("not json at all!")
        
        # Initialize StateManager
        sm = StateManager(str(state_file))
        
        # Re-read file and verify it's valid JSON
        with open(state_file, 'r') as f:
            state = json.load(f)  # Should not raise
        
        # Verify all expected fields present
        assert 'version' in state
        assert 'last_viewed' in state
        assert 'pokemon_id' in state['last_viewed']
        assert 'generation' in state['last_viewed']
        assert 'preferences' in state
        assert 'input_mode' in state['preferences']
        assert 'volume' in state['preferences']
        assert 'favorites' in state
        assert 'recent' in state
        assert 'stats' in state
    
    def test_recovery_with_multiple_invalid_values(self, tmp_path):
        """AC #10: Multiple invalid values all corrected"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Create state with multiple invalid values
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 999, "generation": 10},
            "preferences": {"input_mode": "invalid", "volume": 5.0},
            "favorites": [],
            "recent": [],
            "stats": {"total_views": 0, "unique_viewed": 0, "sessions": 0}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        # Initialize StateManager - should correct all values
        sm = StateManager(str(state_file))
        
        # Verify all corrected
        assert sm.get_last_viewed_id() == 386
        assert sm.get_last_viewed_generation() == 3
        assert sm.get_input_mode() == 'keyboard'
        assert sm.get_volume() == 1.0
        
        # Verify file updated with corrections
        with open(state_file, 'r') as f:
            saved_state = json.load(f)
        
        assert saved_state['last_viewed']['pokemon_id'] == 386
        assert saved_state['last_viewed']['generation'] == 3
        assert saved_state['preferences']['input_mode'] == 'keyboard'
        assert saved_state['preferences']['volume'] == 1.0
    
    def test_recovery_preserves_valid_data(self, tmp_path):
        """AC #10: Valid data preserved when correcting invalid data"""
        import json
        
        state_file = tmp_path / "test_state.json"
        
        # Create state with mix of valid and invalid values
        state = {
            "version": "1.0.0",
            "last_viewed": {"pokemon_id": 25, "generation": 5},  # id valid, gen invalid
            "preferences": {"input_mode": "gpio", "volume": 2.0},  # mode valid, vol invalid
            "favorites": [1, 4, 7],  # Valid favorites
            "recent": [25, 1],  # Valid recent
            "stats": {"total_views": 100, "unique_viewed": 50, "sessions": 10}
        }
        
        with open(state_file, 'w') as f:
            json.dump(state, f)
        
        sm = StateManager(str(state_file))
        
        # Valid values preserved
        assert sm.get_last_viewed_id() == 25
        assert sm.get_input_mode() == 'gpio'
        assert sm.get_favorites() == [1, 4, 7]
        
        # Invalid values corrected
        assert sm.get_last_viewed_generation() == 3
        assert sm.get_volume() == 1.0


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


if __name__ == '__main__':
    unittest.main()

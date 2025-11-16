"""
Tests for HomeScreen generation filtering and navigation
"""

import unittest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.home_screen import HomeScreen, GENERATION_RANGES, GENERATION_NAMES
from src.data.database import Database


class TestHomeScreenGenerationFiltering(unittest.TestCase):
    """Test HomeScreen generation filtering functionality"""
    
    def setUp(self):
        """Set up test database and HomeScreen"""
        # Create temporary database
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = Database(self.db_path)
        
        # Create schema and populate with test data
        with self.db as db:
            db.create_schema()
            
            # Insert Pokemon from all three generations
            pokemon_data = []
            
            # Kanto: 1-151
            for i in range(1, 152):
                pokemon_data.append((i, f'Pokemon{i}', i, 10, 100, 100, 1, 1))
            
            # Johto: 152-251
            for i in range(152, 252):
                pokemon_data.append((i, f'Pokemon{i}', i, 10, 100, 100, 2, 1))
            
            # Hoenn: 252-386
            for i in range(252, 387):
                pokemon_data.append((i, f'Pokemon{i}', i, 10, 100, 100, 3, 1))
            
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            db.commit()
        
        # Create mock screen manager
        self.mock_screen_manager = Mock()
        self.mock_screen_manager.width = 800
        self.mock_screen_manager.height = 480
        self.mock_screen_manager.database = self.db
        self.mock_screen_manager.state_manager = Mock()
        self.mock_screen_manager.input_manager = Mock()
        
        # Mock pygame display initialization
        with patch('pygame.display.set_mode'), \
             patch('pygame.font.Font'):
            self.screen = HomeScreen(self.mock_screen_manager)
    
    def tearDown(self):
        """Clean up temporary database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_generation_ranges_constant(self):
        """Test GENERATION_RANGES constant has correct values"""
        self.assertEqual(GENERATION_RANGES[1], (1, 151), "Kanto range should be 1-151")
        self.assertEqual(GENERATION_RANGES[2], (152, 251), "Johto range should be 152-251")
        self.assertEqual(GENERATION_RANGES[3], (252, 386), "Hoenn range should be 252-386")
    
    def test_generation_names_constant(self):
        """Test GENERATION_NAMES constant has correct values"""
        self.assertEqual(GENERATION_NAMES[1], "KANTO")
        self.assertEqual(GENERATION_NAMES[2], "JOHTO")
        self.assertEqual(GENERATION_NAMES[3], "HOENN")
    
    def test_load_pokemon_by_generation_kanto(self):
        """Test loading Kanto generation returns 151 Pokemon"""
        self.screen._load_pokemon_by_generation(1)
        
        self.assertEqual(len(self.screen.pokemon_list), 151, "Should load 151 Kanto Pokemon")
        self.assertEqual(self.screen.pokemon_list[0]['id'], 1, "First should be #1")
        self.assertEqual(self.screen.pokemon_list[-1]['id'], 151, "Last should be #151")
    
    def test_load_pokemon_by_generation_johto(self):
        """Test loading Johto generation returns 100 Pokemon"""
        self.screen._load_pokemon_by_generation(2)
        
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should load 100 Johto Pokemon")
        self.assertEqual(self.screen.pokemon_list[0]['id'], 152, "First should be #152")
        self.assertEqual(self.screen.pokemon_list[-1]['id'], 251, "Last should be #251")
    
    def test_load_pokemon_by_generation_hoenn(self):
        """Test loading Hoenn generation returns 135 Pokemon"""
        self.screen._load_pokemon_by_generation(3)
        
        self.assertEqual(len(self.screen.pokemon_list), 135, "Should load 135 Hoenn Pokemon")
        self.assertEqual(self.screen.pokemon_list[0]['id'], 252, "First should be #252")
        self.assertEqual(self.screen.pokemon_list[-1]['id'], 386, "Last should be #386")
    
    def test_switch_generation_forward(self):
        """Test switching to next generation (R button)"""
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to next (Johto)
        self.screen._switch_generation(1)
        self.assertEqual(self.screen.current_generation, 2, "Should switch to Johto")
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should have 100 Johto Pokemon")
        
        # Switch to next (Hoenn)
        self.screen._switch_generation(1)
        self.assertEqual(self.screen.current_generation, 3, "Should switch to Hoenn")
        self.assertEqual(len(self.screen.pokemon_list), 135, "Should have 135 Hoenn Pokemon")
        
        # Switch to next (wrap to Kanto)
        self.screen._switch_generation(1)
        self.assertEqual(self.screen.current_generation, 1, "Should wrap back to Kanto")
        self.assertEqual(len(self.screen.pokemon_list), 151, "Should have 151 Kanto Pokemon")
    
    def test_switch_generation_backward(self):
        """Test switching to previous generation (L button)"""
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to previous (Hoenn - wraps around)
        self.screen._switch_generation(-1)
        self.assertEqual(self.screen.current_generation, 3, "Should wrap to Hoenn")
        self.assertEqual(len(self.screen.pokemon_list), 135, "Should have 135 Hoenn Pokemon")
        
        # Switch to previous (Johto)
        self.screen._switch_generation(-1)
        self.assertEqual(self.screen.current_generation, 2, "Should switch to Johto")
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should have 100 Johto Pokemon")
        
        # Switch to previous (Kanto)
        self.screen._switch_generation(-1)
        self.assertEqual(self.screen.current_generation, 1, "Should switch to Kanto")
        self.assertEqual(len(self.screen.pokemon_list), 151, "Should have 151 Kanto Pokemon")
    
    def test_scroll_position_resets_on_generation_switch(self):
        """Test that scroll position resets when switching generations"""
        # Start at Kanto, scroll to middle
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        self.screen.selected_index = 75  # Middle of Kanto
        
        # Switch to Johto
        self.screen._switch_generation(1)
        
        # Should reset to first Pokemon
        self.assertEqual(self.screen.selected_index, 0, "Selected index should reset to 0")
        self.assertEqual(self.screen.page, 0, "Page should reset to 0")
        self.assertEqual(self.screen.pokemon_list[0]['id'], 152, "First Pokemon should be Chikorita")
    
    def test_generation_badge_updates_on_switch(self):
        """Test that generation badge updates when switching generations"""
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to Johto
        self.screen._switch_generation(1)
        
        # Badge should update
        if self.screen.generation_badge:
            self.assertEqual(self.screen.generation_badge.generation, 2, "Badge should show Johto")
            self.assertEqual(self.screen.generation_badge.pokemon_id, 152, "Badge should show first Johto Pokemon")
    
    def test_state_manager_called_on_generation_switch(self):
        """Test that StateManager is called when switching generations"""
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to Johto
        self.screen._switch_generation(1)
        
        # StateManager should be called with first Pokemon of new generation
        self.mock_screen_manager.state_manager.set_last_viewed.assert_called()
        call_args = self.mock_screen_manager.state_manager.set_last_viewed.call_args
        self.assertEqual(call_args[0][0], 152, "Should save first Johto Pokemon ID")
        self.assertEqual(call_args[0][1], 2, "Should save Johto generation")
    
    def test_invalid_generation_handled_gracefully(self):
        """Test that invalid generation parameter is handled without crashing"""
        # Load valid generation first
        self.screen._load_pokemon_by_generation(1)
        initial_count = len(self.screen.pokemon_list)
        self.assertEqual(initial_count, 151, "Should start with 151 Kanto Pokemon")
        
        # Now try invalid generation - should handle error gracefully
        self.screen._load_pokemon_by_generation(0)
        
        # Should result in empty list (error state) without crashing
        self.assertEqual(len(self.screen.pokemon_list), 0, "Should have empty list on error")
        self.assertEqual(self.screen.total_pokemon, 0, "Total should be 0 on error")


class TestGenerationRangeConstants(unittest.TestCase):
    """Test generation range constants"""
    
    def test_all_generations_defined(self):
        """Test that all three generations are defined"""
        self.assertIn(1, GENERATION_RANGES, "Generation 1 should be defined")
        self.assertIn(2, GENERATION_RANGES, "Generation 2 should be defined")
        self.assertIn(3, GENERATION_RANGES, "Generation 3 should be defined")
    
    def test_generation_ranges_no_overlap(self):
        """Test that generation ID ranges don't overlap"""
        gen1_start, gen1_end = GENERATION_RANGES[1]
        gen2_start, gen2_end = GENERATION_RANGES[2]
        gen3_start, gen3_end = GENERATION_RANGES[3]
        
        # Gen 1 ends before Gen 2 starts
        self.assertEqual(gen1_end + 1, gen2_start, "Gen 1 should end right before Gen 2")
        
        # Gen 2 ends before Gen 3 starts
        self.assertEqual(gen2_end + 1, gen3_start, "Gen 2 should end right before Gen 3")
    
    def test_generation_ranges_cover_all_pokemon(self):
        """Test that ranges cover all 386 Pokemon"""
        gen3_start, gen3_end = GENERATION_RANGES[3]
        
        self.assertEqual(GENERATION_RANGES[1][0], 1, "Should start at Pokemon #1")
        self.assertEqual(gen3_end, 386, "Should end at Pokemon #386")


if __name__ == '__main__':
    unittest.main()

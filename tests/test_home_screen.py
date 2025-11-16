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
from src.input_manager import InputAction


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
        self.screen.update(0.21)  # Complete transition
        self.assertEqual(self.screen.current_generation, 2, "Should switch to Johto")
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should have 100 Johto Pokemon")
        
        # Switch to next (Hoenn)
        self.screen._switch_generation(1)
        self.screen.update(0.21)
        self.assertEqual(self.screen.current_generation, 3, "Should switch to Hoenn")
        self.assertEqual(len(self.screen.pokemon_list), 135, "Should have 135 Hoenn Pokemon")
        
        # Switch to next (wrap to Kanto)
        self.screen._switch_generation(1)
        self.screen.update(0.21)
        self.assertEqual(self.screen.current_generation, 1, "Should wrap back to Kanto")
        self.assertEqual(len(self.screen.pokemon_list), 151, "Should have 151 Kanto Pokemon")
    
    def test_switch_generation_backward(self):
        """Test switching to previous generation (L button)"""
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to previous (Hoenn - wraps around)
        self.screen._switch_generation(-1)
        self.screen.update(0.21)  # Complete transition
        self.assertEqual(self.screen.current_generation, 3, "Should wrap to Hoenn")
        self.assertEqual(len(self.screen.pokemon_list), 135, "Should have 135 Hoenn Pokemon")
        
        # Switch to previous (Johto)
        self.screen._switch_generation(-1)
        self.screen.update(0.21)
        self.assertEqual(self.screen.current_generation, 2, "Should switch to Johto")
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should have 100 Johto Pokemon")
        
        # Switch to previous (Kanto)
        self.screen._switch_generation(-1)
        self.screen.update(0.21)
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
        self.screen.update(0.21)  # Complete transition
        
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
        self.screen.update(0.21)  # Complete transition - this triggers state save
        
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


class TestLRButtonGenerationSwitching(unittest.TestCase):
    """Test L/R button generation switching functionality (Story 1.4)"""
    
    def setUp(self):
        """Set up test database and HomeScreen with pygame mocking"""
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
        
        # Create mock screen manager with state manager
        self.mock_screen_manager = Mock()
        self.mock_screen_manager.width = 480
        self.mock_screen_manager.height = 320
        self.mock_screen_manager.database = self.db
        self.mock_screen_manager.state_manager = Mock()
        self.mock_screen_manager.input_manager = Mock()
        
        # Mock pygame for tests
        with patch('pygame.display.set_mode'), \
             patch('pygame.font.Font'):
            self.screen = HomeScreen(self.mock_screen_manager, database=self.db)
            self.screen.on_enter()
    
    def tearDown(self):
        """Clean up temporary database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_left_button_cycles_generation_backward(self):
        """
        Test L button cycles generations backward: Kanto → Hoenn → Johto → Kanto
        AC#1 from Story 1.4
        """
        # Start at Kanto (generation 1)
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        self.assertEqual(self.screen.current_generation, 1, "Should start at Kanto")
        
        # Press L button (LEFT action) - should go to Hoenn (gen 3)
        self.screen.handle_input(InputAction.LEFT)
        # Simulate transition completion
        self.screen.update(0.2)  # Complete 200ms transition
        self.assertEqual(self.screen.current_generation, 3, "Should cycle to Hoenn")
        self.assertEqual(len(self.screen.pokemon_list), 135, "Should have 135 Hoenn Pokemon")
        
        # Press L again - should go to Johto (gen 2)
        self.screen.handle_input(InputAction.LEFT)
        self.screen.update(0.2)
        self.assertEqual(self.screen.current_generation, 2, "Should cycle to Johto")
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should have 100 Johto Pokemon")
        
        # Press L again - should wrap back to Kanto (gen 1)
        self.screen.handle_input(InputAction.LEFT)
        self.screen.update(0.2)
        self.assertEqual(self.screen.current_generation, 1, "Should wrap back to Kanto")
        self.assertEqual(len(self.screen.pokemon_list), 151, "Should have 151 Kanto Pokemon")
    
    def test_right_button_cycles_generation_forward(self):
        """
        Test R button cycles generations forward: Kanto → Johto → Hoenn → Kanto
        AC#2 from Story 1.4
        """
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        self.assertEqual(self.screen.current_generation, 1, "Should start at Kanto")
        
        # Press R button (RIGHT action) - should go to Johto (gen 2)
        self.screen.handle_input(InputAction.RIGHT)
        self.screen.update(0.2)
        self.assertEqual(self.screen.current_generation, 2, "Should cycle to Johto")
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should have 100 Johto Pokemon")
        
        # Press R again - should go to Hoenn (gen 3)
        self.screen.handle_input(InputAction.RIGHT)
        self.screen.update(0.2)
        self.assertEqual(self.screen.current_generation, 3, "Should cycle to Hoenn")
        self.assertEqual(len(self.screen.pokemon_list), 135, "Should have 135 Hoenn Pokemon")
        
        # Press R again - should wrap back to Kanto (gen 1)
        self.screen.handle_input(InputAction.RIGHT)
        self.screen.update(0.2)
        self.assertEqual(self.screen.current_generation, 1, "Should wrap back to Kanto")
        self.assertEqual(len(self.screen.pokemon_list), 151, "Should have 151 Kanto Pokemon")
    
    def test_generation_switch_resets_scroll_position(self):
        """
        Test scroll position resets to first Pokemon when switching generation
        AC#1 from Story 1.4
        """
        # Start at Kanto, scroll to middle
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        self.screen.selected_index = 75  # Middle of Kanto
        self.screen.page = 6
        
        # Switch to Johto
        self.screen.handle_input(InputAction.RIGHT)
        self.screen.update(0.2)
        
        # Should reset to first Pokemon
        self.assertEqual(self.screen.selected_index, 0, "Selected index should reset to 0")
        self.assertEqual(self.screen.page, 0, "Page should reset to 0")
        self.assertEqual(self.screen.pokemon_list[0]['id'], 152, "First Pokemon should be Chikorita")
    
    def test_generation_switch_saves_state(self):
        """
        Test StateManager.set_last_viewed() is called with new generation
        AC#3 from Story 1.4
        """
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to Johto
        self.screen.handle_input(InputAction.RIGHT)
        self.screen.update(0.2)  # Complete transition
        
        # StateManager should be called with first Pokemon of Johto
        self.mock_screen_manager.state_manager.set_last_viewed.assert_called()
        call_args = self.mock_screen_manager.state_manager.set_last_viewed.call_args[0]
        self.assertEqual(call_args[0], 152, "Should save first Johto Pokemon ID (Chikorita)")
        self.assertEqual(call_args[1], 2, "Should save Johto generation")
    
    def test_generation_badge_glows_on_switch(self):
        """
        Test generation badge triggers glow effect during transition
        AC#2 from Story 1.4
        """
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Ensure badge exists
        self.assertIsNotNone(self.screen.generation_badge, "Badge should exist")
        
        # Badge should not be glowing initially
        self.assertFalse(self.screen.generation_badge.active_glow, "Badge should not glow initially")
        
        # Switch generation
        self.screen.handle_input(InputAction.RIGHT)
        
        # After 0.11s (past switch point at 0.1s), badge should start glowing
        self.screen.update(0.11)
        self.assertTrue(self.screen.generation_badge.active_glow, "Badge should glow during transition")
        self.assertGreater(self.screen.generation_badge.glow_timer, 0, "Glow timer should be active")
        
        # Glow duration is 300ms = 0.3s
        # At 0.11s, glow timer was set to 300ms
        # Need to advance 0.301s to fully expire it (0.11s already used for update_glow calls)
        for _ in range(4):  # 4 * 0.1s = 0.4s total additional time
            self.screen.update(0.1)
        
        # After 0.51s total (0.11 + 0.4), glow should definitely be done
        self.assertFalse(self.screen.generation_badge.active_glow, "Badge glow should fade after 300ms")
    
    def test_transition_completes_within_300ms(self):
        """
        Test generation switch transition completes within 300ms
        AC#2 from Story 1.4
        """
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Trigger switch
        self.screen.handle_input(InputAction.RIGHT)
        
        # Transition should be active
        self.assertTrue(self.screen.is_transitioning, "Transition should be active")
        
        # After 0.21s (past 0.2s transition duration), transition should complete
        self.screen.update(0.21)
        
        # Transition should be complete
        self.assertFalse(self.screen.is_transitioning, "Transition should complete within 300ms (0.2s actual)")
        self.assertEqual(self.screen.transition_alpha, 255, "Alpha should be fully opaque")
        self.assertEqual(self.screen.current_generation, 2, "Should be in Johto")
    
    def test_rapid_button_pressing_no_crash(self):
        """
        Test rapid L/R button presses don't cause crashes or race conditions
        AC#4 from Story 1.4
        """
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Rapidly press R button 10 times with minimal time steps
        for _ in range(10):
            self.screen.handle_input(InputAction.RIGHT)
            self.screen.update(0.01)  # Just 10ms per press
        
        # Complete any pending transition
        self.screen.update(0.5)
        
        # Should still be in valid state (some generation 1-3)
        self.assertIn(self.screen.current_generation, [1, 2, 3], "Should be in valid generation")
        self.assertGreater(len(self.screen.pokemon_list), 0, "Should have Pokemon loaded")
    
    def test_state_manager_missing_graceful(self):
        """
        Test generation switch works gracefully when StateManager is None
        Edge case from Story 1.4
        """
        # Remove state manager
        self.screen.screen_manager.state_manager = None
        
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch generation should not crash
        self.screen.handle_input(InputAction.RIGHT)
        self.screen.update(0.2)
        
        # Should successfully switch to Johto
        self.assertEqual(self.screen.current_generation, 2, "Should switch to Johto")
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should have 100 Johto Pokemon")
    
    def test_badge_updates_with_correct_pokemon_id(self):
        """
        Test generation badge updates with first Pokemon ID of new generation
        AC#1 from Story 1.4
        """
        # Start at Kanto
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to Johto
        self.screen.handle_input(InputAction.RIGHT)
        self.screen.update(0.2)
        
        # Badge should show first Johto Pokemon
        if self.screen.generation_badge:
            self.assertEqual(self.screen.generation_badge.generation, 2, "Badge should show Johto")
            self.assertEqual(self.screen.generation_badge.pokemon_id, 152, "Badge should show Chikorita ID")


if __name__ == '__main__':
    unittest.main()


class TestHomeScreenStatePersistence(unittest.TestCase):
    """Test HomeScreen state persistence integration (Story 1.5)"""
    
    def setUp(self):
        """Set up test database and HomeScreen with mock state manager"""
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
        
        # Create mock screen manager with mock state manager
        self.mock_screen_manager = Mock()
        self.mock_screen_manager.width = 800
        self.mock_screen_manager.height = 480
        self.mock_screen_manager.database = self.db
        self.mock_screen_manager.input_manager = Mock()
        
        # Create mock state manager
        self.mock_state_manager = Mock()
        self.mock_state_manager.get_last_viewed_generation.return_value = 1
        self.mock_state_manager.get_last_viewed_id.return_value = 1
        self.mock_screen_manager.state_manager = self.mock_state_manager
        
        # Mock pygame display initialization
        with patch('pygame.display.set_mode'), \
             patch('pygame.font.Font'):
            self.screen = HomeScreen(self.mock_screen_manager, self.db)
    
    def tearDown(self):
        """Clean up temporary database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
    
    def test_on_enter_loads_last_viewed_generation(self):
        """Test on_enter loads last viewed generation from state (AC #2, #3)"""
        # Set up mock to return Johto generation
        self.mock_state_manager.get_last_viewed_generation.return_value = 2
        self.mock_state_manager.get_last_viewed_id.return_value = 152  # Chikorita
        
        # Call on_enter
        self.screen.on_enter()
        
        # Verify generation was loaded
        self.assertEqual(self.screen.current_generation, 2, "Should load Johto generation")
        
        # Verify Pokemon list is for Johto
        self.assertEqual(len(self.screen.pokemon_list), 100, "Should load 100 Johto Pokemon")
        self.assertEqual(self.screen.pokemon_list[0]['id'], 152, "First should be Chikorita")
    
    def test_on_enter_loads_last_viewed_pokemon(self):
        """Test on_enter sets selected_index to last viewed Pokemon (AC #2, #3)"""
        # Set up mock to return Pikachu in Kanto
        self.mock_state_manager.get_last_viewed_generation.return_value = 1
        self.mock_state_manager.get_last_viewed_id.return_value = 25  # Pikachu
        
        # Call on_enter
        self.screen.on_enter()
        
        # Verify Pikachu is selected
        self.assertEqual(self.screen.pokemon_list[self.screen.selected_index]['id'], 25, "Pikachu should be selected")
        
        # Verify page is calculated correctly for this selection
        expected_page = 24 // self.screen.items_per_page  # Pikachu is at index 24 (0-indexed)
        self.assertEqual(self.screen.page, expected_page, "Page should be calculated correctly")
    
    def test_on_enter_defaults_to_first_if_pokemon_not_in_generation(self):
        """Test on_enter defaults to first Pokemon if last viewed not in current generation"""
        # Set up mock to return Johto generation but Kanto Pokemon
        self.mock_state_manager.get_last_viewed_generation.return_value = 2
        self.mock_state_manager.get_last_viewed_id.return_value = 25  # Pikachu (Kanto)
        
        # Call on_enter
        self.screen.on_enter()
        
        # Should default to first Pokemon in Johto (Chikorita)
        self.assertEqual(self.screen.selected_index, 0, "Should default to first index")
        self.assertEqual(self.screen.pokemon_list[0]['id'], 152, "Should be Chikorita")
    
    def test_on_exit_saves_current_state(self):
        """Test on_exit saves current Pokemon and generation to state (AC #2, #3)"""
        # Set up screen state
        self.screen.on_enter()
        self.screen.current_generation = 2
        self.screen._load_pokemon_by_generation(2)
        self.screen.selected_index = 10  # Some Pokemon in the list
        
        # Call on_exit
        self.screen.on_exit()
        
        # Verify state_manager.set_last_viewed was called
        self.mock_state_manager.set_last_viewed.assert_called_once()
        call_args = self.mock_state_manager.set_last_viewed.call_args
        
        # Check arguments
        self.assertEqual(call_args[0][0], self.screen.pokemon_list[10]['id'], "Should save selected Pokemon ID")
        self.assertEqual(call_args[0][1], 2, "Should save Johto generation")
        
        # Verify save_state was called
        self.mock_state_manager.save_state.assert_called_once()
    
    def test_on_exit_handles_missing_state_manager(self):
        """Test on_exit doesn't crash if state_manager is None"""
        # Remove state manager
        self.mock_screen_manager.state_manager = None
        
        # Recreate screen without state manager
        with patch('pygame.display.set_mode'), \
             patch('pygame.font.Font'):
            screen = HomeScreen(self.mock_screen_manager, self.db)
            screen.on_enter()
            screen.current_generation = 1
            screen._load_pokemon_by_generation(1)
        
        # Should not crash
        screen.on_exit()
    
    def test_generation_switch_saves_new_generation(self):
        """Test generation switch updates state with new generation (AC #3)"""
        # Set up screen
        self.screen.on_enter()
        self.screen.current_generation = 1
        self.screen._load_pokemon_by_generation(1)
        
        # Switch to Johto
        self.screen._switch_generation(1)
        self.screen.update(0.2)  # Complete transition
        
        # Verify state_manager.set_last_viewed was called with new generation
        self.mock_state_manager.set_last_viewed.assert_called()
        
        # Get the last call (from generation switch, not on_enter)
        last_call = self.mock_state_manager.set_last_viewed.call_args_list[-1]
        self.assertEqual(last_call[1]['generation'], 2, "Should save Johto generation")
        self.assertEqual(last_call[1]['pokemon_id'], 152, "Should save first Johto Pokemon")



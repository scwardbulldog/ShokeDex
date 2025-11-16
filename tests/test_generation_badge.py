"""
Tests for GenerationBadge component.
"""

import unittest
import pygame
from unittest.mock import Mock, patch, MagicMock

from src.ui.home_screen import GenerationBadge, GENERATION_NAMES, GENERATION_TOTALS


class TestGenerationBadge(unittest.TestCase):
    """Test GenerationBadge component rendering and behavior."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame for testing."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
    
    @classmethod
    def tearDownClass(cls):
        """Clean up pygame."""
        pygame.quit()
    
    def test_badge_initialization_kanto(self):
        """Test badge initializes correctly for Kanto generation."""
        badge = GenerationBadge(generation=1, pokemon_id=25)
        
        self.assertEqual(badge.generation, 1)
        self.assertEqual(badge.pokemon_id, 25)
    
    def test_badge_initialization_johto(self):
        """Test badge initializes correctly for Johto generation."""
        badge = GenerationBadge(generation=2, pokemon_id=152)
        
        self.assertEqual(badge.generation, 2)
        self.assertEqual(badge.pokemon_id, 152)
    
    def test_badge_initialization_hoenn(self):
        """Test badge initializes correctly for Hoenn generation."""
        badge = GenerationBadge(generation=3, pokemon_id=252)
        
        self.assertEqual(badge.generation, 3)
        self.assertEqual(badge.pokemon_id, 252)
    
    def test_update_pokemon_id(self):
        """Test badge updates position counter when Pokemon changes."""
        badge = GenerationBadge(generation=1, pokemon_id=1)
        
        # Update to different Pokemon
        badge.update(pokemon_id=25)
        
        self.assertEqual(badge.pokemon_id, 25)
    
    def test_set_generation_updates_correctly(self):
        """Test set_generation updates both generation and Pokemon ID."""
        badge = GenerationBadge(generation=1, pokemon_id=25)
        
        # Switch to Johto
        badge.set_generation(generation=2, pokemon_id=152)
        
        self.assertEqual(badge.generation, 2)
        self.assertEqual(badge.pokemon_id, 152)
    
    @patch('os.path.exists')
    @patch('pygame.image.load')
    @patch('pygame.transform.smoothscale')
    def test_logo_loading_success(self, mock_scale, mock_load, mock_exists):
        """Test badge successfully loads logo asset when available."""
        mock_exists.return_value = True
        mock_surface = MagicMock(spec=pygame.Surface)
        mock_load.return_value = mock_surface
        mock_surface.convert_alpha.return_value = mock_surface
        mock_scale.return_value = mock_surface
        
        badge = GenerationBadge(generation=1, pokemon_id=1)
        
        # Logo should be loaded
        self.assertIsNotNone(badge.logo_surface)
        mock_load.assert_called_once()
    
    @patch('os.path.exists')
    def test_logo_loading_fallback(self, mock_exists):
        """Test badge falls back to text-only when logo missing."""
        mock_exists.return_value = False
        
        badge = GenerationBadge(generation=1, pokemon_id=1)
        
        # Logo should be None (text-only fallback)
        self.assertIsNone(badge.logo_surface)
    
    @patch('os.path.exists')
    @patch('pygame.image.load')
    def test_logo_loading_error_handling(self, mock_load, mock_exists):
        """Test badge handles image loading errors gracefully."""
        mock_exists.return_value = True
        mock_load.side_effect = pygame.error("Could not load image")
        
        # Should not raise exception
        badge = GenerationBadge(generation=1, pokemon_id=1)
        
        # Logo should be None after error
        self.assertIsNone(badge.logo_surface)
    
    def test_render_creates_surface(self):
        """Test badge render method creates a valid surface."""
        badge = GenerationBadge(generation=1, pokemon_id=25)
        badge.name_font = pygame.font.Font(None, 24)
        badge.counter_font = pygame.font.Font(None, 18)
        
        # Create test surface
        test_surface = pygame.Surface((480, 320))
        
        # Should not raise exception
        badge.render(test_surface, x=10, y=10)
        
        # Visual inspection would be needed to verify appearance
        # Unit test confirms it doesn't crash
    
    def test_render_without_fonts(self):
        """Test badge render handles missing fonts gracefully."""
        badge = GenerationBadge(generation=1, pokemon_id=25)
        # Don't set fonts
        
        test_surface = pygame.Surface((480, 320))
        
        # Should not crash, just won't render text
        badge.render(test_surface, x=10, y=10)
    
    def test_position_counter_format_kanto(self):
        """Test position counter shows correct format for Kanto (#XXX/151)."""
        badge = GenerationBadge(generation=1, pokemon_id=25)
        
        # Verify data is correct (rendering tested separately)
        self.assertEqual(badge.pokemon_id, 25)
        self.assertEqual(GENERATION_TOTALS[badge.generation], 151)
    
    def test_position_counter_format_johto(self):
        """Test position counter shows correct format for Johto (#XXX/100)."""
        badge = GenerationBadge(generation=2, pokemon_id=152)
        
        self.assertEqual(badge.pokemon_id, 152)
        self.assertEqual(GENERATION_TOTALS[badge.generation], 100)
    
    def test_position_counter_format_hoenn(self):
        """Test position counter shows correct format for Hoenn (#XXX/135)."""
        badge = GenerationBadge(generation=3, pokemon_id=252)
        
        self.assertEqual(badge.pokemon_id, 252)
        self.assertEqual(GENERATION_TOTALS[badge.generation], 135)
    
    def test_generation_names_constant(self):
        """Test GENERATION_NAMES constant has correct values."""
        self.assertEqual(GENERATION_NAMES[1], "KANTO")
        self.assertEqual(GENERATION_NAMES[2], "JOHTO")
        self.assertEqual(GENERATION_NAMES[3], "HOENN")
    
    def test_generation_totals_constant(self):
        """Test GENERATION_TOTALS constant has correct values."""
        self.assertEqual(GENERATION_TOTALS[1], 151)
        self.assertEqual(GENERATION_TOTALS[2], 100)
        self.assertEqual(GENERATION_TOTALS[3], 135)
    
    def test_badge_edge_case_pokemon_1(self):
        """Test badge with first Pokemon in Kanto."""
        badge = GenerationBadge(generation=1, pokemon_id=1)
        
        self.assertEqual(badge.pokemon_id, 1)
        self.assertEqual(badge.generation, 1)
    
    def test_badge_edge_case_pokemon_151(self):
        """Test badge with last Pokemon in Kanto."""
        badge = GenerationBadge(generation=1, pokemon_id=151)
        
        self.assertEqual(badge.pokemon_id, 151)
        self.assertEqual(badge.generation, 1)
    
    def test_badge_edge_case_pokemon_152(self):
        """Test badge with first Pokemon in Johto."""
        badge = GenerationBadge(generation=2, pokemon_id=152)
        
        self.assertEqual(badge.pokemon_id, 152)
        self.assertEqual(badge.generation, 2)
    
    def test_badge_edge_case_pokemon_251(self):
        """Test badge with last Pokemon in Johto."""
        badge = GenerationBadge(generation=2, pokemon_id=251)
        
        self.assertEqual(badge.pokemon_id, 251)
        self.assertEqual(badge.generation, 2)
    
    def test_badge_edge_case_pokemon_386(self):
        """Test badge with last Pokemon in Hoenn."""
        badge = GenerationBadge(generation=3, pokemon_id=386)
        
        self.assertEqual(badge.pokemon_id, 386)
        self.assertEqual(badge.generation, 3)


class TestGenerationBadgeIntegration(unittest.TestCase):
    """Integration tests for GenerationBadge in HomeScreen context."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize pygame for testing."""
        pygame.init()
        pygame.display.set_mode((1, 1))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up pygame."""
        pygame.quit()
    
    def test_badge_update_during_scrolling(self):
        """Test badge position counter updates when user scrolls Pokemon."""
        badge = GenerationBadge(generation=1, pokemon_id=1)
        
        # Simulate scrolling through Pokemon
        for pokemon_id in range(1, 11):
            badge.update(pokemon_id)
            self.assertEqual(badge.pokemon_id, pokemon_id)
    
    def test_badge_generation_switch(self):
        """Test badge updates when switching between generations."""
        badge = GenerationBadge(generation=1, pokemon_id=25)
        
        # Switch to Johto
        badge.set_generation(generation=2, pokemon_id=152)
        self.assertEqual(badge.generation, 2)
        self.assertEqual(badge.pokemon_id, 152)
        
        # Switch to Hoenn
        badge.set_generation(generation=3, pokemon_id=252)
        self.assertEqual(badge.generation, 3)
        self.assertEqual(badge.pokemon_id, 252)
        
        # Wrap back to Kanto
        badge.set_generation(generation=1, pokemon_id=1)
        self.assertEqual(badge.generation, 1)
        self.assertEqual(badge.pokemon_id, 1)


if __name__ == '__main__':
    unittest.main()

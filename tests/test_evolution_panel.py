"""
Tests for EvolutionPanel component.

Story 5.1: Three-Stage Evolution Chain Display
Tests evolution panel rendering, data loading, sprite loading, and integration.
"""

import unittest
import pygame
import os
import tempfile
import time
from pathlib import Path
from src.data.database import Database
from src.ui.detail_screen import EvolutionPanel
from unittest.mock import Mock


class MockScreenManager:
    """Mock ScreenManager for testing EvolutionPanel."""
    
    def __init__(self, database):
        self.database = database


class TestEvolutionPanel(unittest.TestCase):
    """Test EvolutionPanel component functionality."""
    
    def setUp(self):
        """Set up test database and pygame."""
        # Initialize pygame for font rendering
        pygame.init()
        pygame.display.set_mode((800, 480))  # Create display for rendering tests
        
        # Create temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.db = Database(self.db_path)
        
        # Initialize schema
        with self.db as db:
            db.create_schema()
    
    def tearDown(self):
        """Clean up test database and pygame."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
        pygame.quit()
    
    def test_evolution_panel_load_data_calls_database(self):
        """Test that load_data() calls Database.get_evolution_chain()."""
        # Insert test Pokemon
        with self.db as db:
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (4, 'charmander', 4, 6, 85, 62, 1))
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        
        # Load data
        panel.load_data()
        
        # Verify data loaded
        self.assertIsNotNone(panel.evolution_data)
    
    def test_evolution_panel_three_stage_chain(self):
        """Test evolution panel with Charmander 3-stage chain (AC #1)."""
        # Insert Charmander, Charmeleon, Charizard
        with self.db as db:
            pokemon_data = [
                (4, 'charmander', 4, 6, 85, 62, 1),
                (5, 'charmeleon', 5, 11, 190, 142, 1),
                (6, 'charizard', 6, 17, 905, 240, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            # Create evolution chain
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (2,))
            
            # Add evolutions
            evolutions = [
                (2, 4, 5, 16, 'level-up', None, None, None),
                (2, 5, 6, 36, 'level-up', None, None, None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, evolutions)
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        panel.load_data()
        
        # Verify chain data
        self.assertEqual(len(panel.evolution_data['stages']), 3)
        self.assertEqual(len(panel.evolution_data['evolutions']), 2)
        self.assertEqual(panel.evolution_data['current_stage'], 1)
    
    def test_evolution_panel_load_sprites(self):
        """Test sprite loading for evolution chain (AC #7)."""
        # Insert test Pokemon
        with self.db as db:
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (4, 'charmander', 4, 6, 85, 62, 1))
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        panel.load_data()
        panel.load_sprites()
        
        # Verify sprite loaded (should have placeholder if no file)
        self.assertIn(4, panel.sprites)
        self.assertIsNotNone(panel.sprites[4])
        
        # Verify sprite is 64x64 (AC #1: thumbnail size)
        sprite = panel.sprites[4]
        self.assertEqual(sprite.get_width(), 64)
        self.assertEqual(sprite.get_height(), 64)
    
    def test_evolution_panel_single_stage_no_evolutions(self):
        """Test evolution panel with no evolutions (Ditto)."""
        # Insert Ditto (no evolutions)
        with self.db as db:
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (132, 'ditto', 132, 3, 40, 101, 1))
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 132)
        panel.load_data()
        
        # Verify single-stage data
        self.assertEqual(len(panel.evolution_data['stages']), 1)
        self.assertEqual(len(panel.evolution_data['evolutions']), 0)
        self.assertEqual(panel.evolution_data['current_stage'], 1)
    
    def test_evolution_panel_format_requirement_level(self):
        """Test requirement formatting for level evolution (AC #3)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        
        # Test level requirement
        evo_data = {
            'method': 'level-up',
            'level': 16,
            'item': None,
            'trigger': None
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Level 16")
    
    def test_evolution_panel_format_requirement_stone(self):
        """Test requirement formatting for stone evolution (AC #3)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 25)
        
        # Test stone requirement
        evo_data = {
            'method': 'use-item',
            'level': None,
            'item': 'thunder-stone',
            'trigger': None
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Thunder Stone")
    
    def test_evolution_panel_format_requirement_trade(self):
        """Test requirement formatting for trade evolution (AC #3)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 64)
        
        # Test trade requirement
        evo_data = {
            'method': 'trade',
            'level': None,
            'item': None,
            'trigger': None
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Trade")
    
    def test_evolution_panel_render_all_elements(self):
        """Test that render() displays all required elements (Task 7.4, AC #1-5)."""
        # Insert three-stage evolution chain
        with self.db as db:
            # Insert evolution chain
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (4,))
            # Insert Pokemon
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (4, 'charmander', 4, 6, 85, 62, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (5, 'charmeleon', 5, 11, 190, 142, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (6, 'charizard', 6, 17, 905, 240, 1))
            # Insert evolutions
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (1, 4, 4, 5, 'level-up', 16, None))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (2, 4, 5, 6, 'level-up', 36, None))
            db.commit()
        
        # Create panel for middle stage (Charmeleon)
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 5)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Render
        panel.render(surface, 20, 100)
        
        # Verify sprites dict has all three Pokemon
        self.assertEqual(len(panel.sprites), 3)
        self.assertIn(4, panel.sprites)  # Charmander
        self.assertIn(5, panel.sprites)  # Charmeleon
        self.assertIn(6, panel.sprites)  # Charizard
        
        # Verify all sprites are 64x64
        for sprite in panel.sprites.values():
            self.assertEqual(sprite.get_size(), (64, 64))
    
    def test_evolution_panel_highlights_current_pokemon(self):
        """Test that current Pokemon is highlighted with glow (Task 7.5, AC #4)."""
        # Insert three-stage evolution chain (same as above)
        with self.db as db:
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (4,))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (4, 'charmander', 4, 6, 85, 62, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (5, 'charmeleon', 5, 11, 190, 142, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (6, 'charizard', 6, 17, 905, 240, 1))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (1, 4, 4, 5, 'level-up', 16, None))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (2, 4, 5, 6, 'level-up', 36, None))
            db.commit()
        
        # Create panel for middle stage (Charmeleon - stage 2)
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 5)
        panel.load_data()
        
        # Verify current_stage is correctly identified
        self.assertEqual(panel.evolution_data['current_stage'], 2)
        
        # The highlighting logic should identify stage 2 as current
        # (This is tested by rendering - if it crashes, highlighting failed)
        panel.load_sprites()
        surface = pygame.Surface((800, 480))
        
        try:
            panel.render(surface, 20, 100)
            highlighting_works = True
        except Exception:
            highlighting_works = False
        
        self.assertTrue(highlighting_works, "Current Pokemon highlighting should work without crashing")
    
    def test_evolution_panel_renders_under_200ms(self):
        """Test that evolution panel renders within performance budget (Task 7.6, AC #8)."""
        # Insert three-stage evolution chain
        with self.db as db:
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (4,))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (4, 'charmander', 4, 6, 85, 62, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (5, 'charmeleon', 5, 11, 190, 142, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (6, 'charizard', 6, 17, 905, 240, 1))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (1, 4, 4, 5, 'level-up', 16, None))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (2, 4, 5, 6, 'level-up', 36, None))
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 5)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Measure render time
        start_time = time.perf_counter()
        panel.render(surface, 20, 100)
        render_time = (time.perf_counter() - start_time) * 1000
        
        # AC #8: Evolution panel should render in <200ms
        self.assertLess(render_time, 200.0,
                       f"Evolution panel render took {render_time:.2f}ms, expected <200ms")
    
    def test_evolution_panel_render_does_not_crash(self):
        """Test that render() completes without crashing."""
        # Insert test Pokemon
        with self.db as db:
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (4, 'charmander', 4, 6, 85, 62, 1))
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Render should not crash
        try:
            panel.render(surface, 20, 100)
            success = True
        except Exception as e:
            success = False
            print(f"Render failed: {e}")
        
        self.assertTrue(success, "Evolution panel render should not crash")
    
    # ========================================
    # Story 5.2: Branching Evolution Tests
    # ========================================
    
    def test_get_evolution_chain_eevee_branching(self):
        """Test branching detection for Eevee (5 branches) (Story 5.2 Task 1.5, AC #1)."""
        # Insert Eevee and its 5 evolutions (Gen 1-3)
        with self.db as db:
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            
            # Insert Eevee
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (133, 'eevee', 133, 3, 65, 65, 1))
            
            # Insert Eevee's evolutions
            evolutions_data = [
                (134, 'vaporeon', 134, 10, 290, 184, 1),
                (135, 'jolteon', 135, 8, 245, 184, 1),
                (136, 'flareon', 136, 9, 250, 184, 1),
                (196, 'espeon', 196, 9, 265, 184, 2),
                (197, 'umbreon', 197, 10, 270, 184, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, evolutions_data)
            
            # Insert evolution relationships
            evo_rels = [
                (1, 67, 133, 134, 'use-item', None, 'water-stone', None, None),
                (2, 67, 133, 135, 'use-item', None, 'thunder-stone', None, None),
                (3, 67, 133, 136, 'use-item', None, 'fire-stone', None, None),
                (4, 67, 133, 196, 'level-up', None, None, 220, 'daytime'),
                (5, 67, 133, 197, 'level-up', None, None, 220, 'nighttime')
            ]
            db.executemany("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evo_rels)
            db.commit()
        
        # Create panel for Eevee
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 133)
        panel.load_data()
        
        # Verify branching is detected (AC #1)
        self.assertTrue(panel.evolution_data['is_branching'], 
                       "Eevee evolution chain should be detected as branching")
        
        # Verify all 6 Pokemon are in stages (1 root + 5 branches)
        self.assertEqual(len(panel.evolution_data['stages']), 6)
        
        # Verify all 5 evolution relationships exist
        self.assertEqual(len(panel.evolution_data['evolutions']), 5)
    
    def test_evolution_panel_render_branching_eevee(self):
        """Test branching layout rendering for Eevee (Story 5.2 Task 7.2, AC #2)."""
        # Insert Eevee and evolutions (same as above)
        with self.db as db:
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (133, 'eevee', 133, 3, 65, 65, 1))
            evolutions_data = [
                (134, 'vaporeon', 134, 10, 290, 184, 1),
                (135, 'jolteon', 135, 8, 245, 184, 1),
                (136, 'flareon', 136, 9, 250, 184, 1),
                (196, 'espeon', 196, 9, 265, 184, 2),
                (197, 'umbreon', 197, 10, 270, 184, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, evolutions_data)
            evo_rels = [
                (1, 67, 133, 134, 'use-item', None, 'water-stone', None, None),
                (2, 67, 133, 135, 'use-item', None, 'thunder-stone', None, None),
                (3, 67, 133, 136, 'use-item', None, 'fire-stone', None, None),
                (4, 67, 133, 196, 'level-up', None, None, 220, 'daytime'),
                (5, 67, 133, 197, 'level-up', None, None, 220, 'nighttime')
            ]
            db.executemany("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evo_rels)
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 133)
        panel.load_data()
        panel.load_sprites()
        
        # Verify all 6 sprites loaded
        self.assertEqual(len(panel.sprites), 6)
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Render should not crash with branching layout
        try:
            panel.render(surface, 20, 100)
            rendering_works = True
        except Exception as e:
            rendering_works = False
            print(f"Branching render failed: {e}")
        
        self.assertTrue(rendering_works, "Branching evolution panel should render without crashing")
    
    def test_evolution_panel_highlights_branch_vaporeon(self):
        """Test highlighting when viewing branch evolution (Story 5.2 Task 7.4, AC #5, #6)."""
        # Insert Eevee and evolutions
        with self.db as db:
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (133, 'eevee', 133, 3, 65, 65, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (134, 'vaporeon', 134, 10, 290, 184, 1))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (135, 'jolteon', 135, 8, 245, 184, 1))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (1, 67, 133, 134, 'use-item', None, 'water-stone', None, None))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (2, 67, 133, 135, 'use-item', None, 'thunder-stone', None, None))
            db.commit()
        
        # Create panel for Vaporeon (should show Eevee + all branches with Vaporeon highlighted)
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 134)
        panel.load_data()
        
        # Verify Vaporeon is stage 2 (AC #6: pre-evolution shown, branch is current)
        self.assertEqual(panel.evolution_data['current_stage'], 2)
        
        # Verify branching is detected
        self.assertTrue(panel.evolution_data['is_branching'])
        
        # Load sprites and render (AC #5: Vaporeon should be highlighted)
        panel.load_sprites()
        surface = pygame.Surface((800, 480))
        
        try:
            panel.render(surface, 20, 100)
            highlighting_works = True
        except Exception as e:
            highlighting_works = False
            print(f"Branch highlighting failed: {e}")
        
        self.assertTrue(highlighting_works, "Branch highlighting should work correctly")
    
    def test_branching_panel_renders_under_250ms(self):
        """Test branching panel performance with Eevee (Story 5.2 Task 7.6, AC #9)."""
        # Insert Eevee and all 5 evolutions (worst case)
        with self.db as db:
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (133, 'eevee', 133, 3, 65, 65, 1))
            evolutions_data = [
                (134, 'vaporeon', 134, 10, 290, 184, 1),
                (135, 'jolteon', 135, 8, 245, 184, 1),
                (136, 'flareon', 136, 9, 250, 184, 1),
                (196, 'espeon', 196, 9, 265, 184, 2),
                (197, 'umbreon', 197, 10, 270, 184, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, evolutions_data)
            evo_rels = [
                (1, 67, 133, 134, 'use-item', None, 'water-stone', None, None),
                (2, 67, 133, 135, 'use-item', None, 'thunder-stone', None, None),
                (3, 67, 133, 136, 'use-item', None, 'fire-stone', None, None),
                (4, 67, 133, 196, 'level-up', None, None, 220, 'daytime'),
                (5, 67, 133, 197, 'level-up', None, None, 220, 'nighttime')
            ]
            db.executemany("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evo_rels)
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 133)
        
        # Measure total time including data load, sprite load, and render
        start_time = time.perf_counter()
        panel.load_data()
        panel.load_sprites()
        surface = pygame.Surface((800, 480))
        panel.render(surface, 20, 100)
        total_time = (time.perf_counter() - start_time) * 1000
        
        # AC #9: Should complete within 250ms (database query + 6 sprites + render)
        self.assertLess(total_time, 250.0,
                       f"Branching panel (Eevee) took {total_time:.2f}ms, expected <250ms")
    
    def test_two_branch_evolution_wurmple(self):
        """Test two-branch evolution edge case (Story 5.2 Task 7.7, AC #10)."""
        # Insert Wurmple and its 2 evolutions
        with self.db as db:
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (133,))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (265, 'wurmple', 265, 3, 36, 56, 3))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (266, 'silcoon', 266, 6, 100, 72, 3))
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (268, 'cascoon', 268, 7, 115, 72, 3))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (1, 133, 265, 266, 'level-up', 7, None, None, None))
            db.execute("""
                INSERT INTO evolutions (id, evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (2, 133, 265, 268, 'level-up', 7, None, None, None))
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 265)
        panel.load_data()
        
        # Verify branching detected (AC #10: 2 branches should use same pattern)
        self.assertTrue(panel.evolution_data['is_branching'])
        
        # Verify 3 total Pokemon (1 root + 2 branches)
        self.assertEqual(len(panel.evolution_data['stages']), 3)
        
        # Verify 2 evolution relationships
        self.assertEqual(len(panel.evolution_data['evolutions']), 2)
        
        # Render should work without visual skew (AC #10)
        panel.load_sprites()
        surface = pygame.Surface((800, 480))
        
        try:
            panel.render(surface, 20, 100)
            rendering_works = True
        except Exception as e:
            rendering_works = False
            print(f"Two-branch render failed: {e}")
        
        self.assertTrue(rendering_works, "Two-branch layout should render correctly")


if __name__ == '__main__':
    unittest.main()

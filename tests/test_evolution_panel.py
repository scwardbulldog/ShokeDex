"""
Tests for EvolutionPanel component.

Story 5.1: Three-Stage Evolution Chain Display
Tests evolution panel rendering, data loading, sprite loading, and integration.

Story 5.6: Performance and Data Accuracy Validation
Tests performance budgets and data accuracy across curated sample.
"""

import unittest
import pytest
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
        # Insert three-stage evolution chain so sprites are expected
        with self.db as db:
            pokemon_data = [
                (4, 'charmander', 4, 6, 85, 62, 1),
                (5, 'charmeleon', 5, 11, 190, 142, 1),
                (6, 'charizard', 6, 17, 905, 240, 1),
            ]
            db.executemany(
                """
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                pokemon_data,
            )
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (4,))
            evolutions = [
                (4, 4, 5, 'level-up', 16, None, None, None),
                (4, 5, 6, 'level-up', 36, None, None, None),
            ]
            db.executemany(
                """
                INSERT INTO evolutions (
                    evolution_chain_id,
                    from_pokemon_id,
                    to_pokemon_id,
                    trigger,
                    min_level,
                    item,
                    min_happiness,
                    time_of_day
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                evolutions,
            )
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
        # Story 5.3: Expose empty evolution list on panel for single-stage handling
        self.assertTrue(hasattr(panel, 'evolutions'))
        self.assertEqual(len(panel.evolutions), 0)
    
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
    
    def test_evolution_panel_format_requirement_trade_with_item(self):
        """Test requirement formatting for trade-with-item evolution (AC #3, #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 95)  # Onix
        
        # Test trade with item requirement
        evo_data = {
            'method': 'trade',
            'level': None,
            'item': 'metal-coat',
            'trigger': None
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Trade holding Metal Coat")
    
    def test_evolution_panel_format_requirement_happiness(self):
        """Test requirement formatting for happiness evolution (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 172)  # Pichu
        
        # Test happiness requirement
        evo_data = {
            'method': 'level-up',
            'level': None,
            'item': None,
            'trigger': 'high-friendship'
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "High Friendship")
    
    def test_evolution_panel_format_requirement_happiness_day(self):
        """Test requirement formatting for happiness-day evolution (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 196)  # Espeon
        
        # Test happiness-day requirement
        evo_data = {
            'method': 'level-up',
            'level': None,
            'item': None,
            'trigger': 'happiness-day'
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "High Friendship (Day)")
    
    def test_evolution_panel_format_requirement_happiness_night(self):
        """Test requirement formatting for happiness-night evolution (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 197)  # Umbreon
        
        # Test happiness-night requirement
        evo_data = {
            'method': 'level-up',
            'level': None,
            'item': None,
            'trigger': 'happiness-night'
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "High Friendship (Night)")
    
    def test_evolution_panel_format_requirement_level_atk_higher(self):
        """Test requirement formatting for level-attack-higher evolution (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 236)  # Tyrogue -> Hitmonlee
        
        # Test level-attack-higher requirement
        evo_data = {
            'method': 'level-up',
            'level': 20,
            'item': None,
            'trigger': 'attack-higher'
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Level (Atk > Def)")
    
    def test_evolution_panel_format_requirement_level_def_higher(self):
        """Test requirement formatting for level-defense-higher evolution (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 236)  # Tyrogue -> Hitmonchan
        
        # Test level-defense-higher requirement
        evo_data = {
            'method': 'level-up',
            'level': 20,
            'item': None,
            'trigger': 'defense-higher'
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Level (Def > Atk)")
    
    def test_evolution_panel_format_requirement_level_atk_def_equal(self):
        """Test requirement formatting for level-attack-defense-equal evolution (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 236)  # Tyrogue -> Hitmontop
        
        # Test level-attack-defense-equal requirement
        evo_data = {
            'method': 'level-up',
            'level': 20,
            'item': None,
            'trigger': 'attack-defense-equal'
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Level (Atk = Def)")
    
    def test_evolution_panel_format_requirement_null_or_empty(self):
        """Test requirement formatting for null/empty evolution method (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 1)
        
        # Test null method
        evo_data = {
            'method': None,
            'level': None,
            'item': None,
            'trigger': None
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "")
        
        # Test empty string method
        evo_data_empty = {
            'method': '',
            'level': None,
            'item': None,
            'trigger': None
        }
        
        requirement_empty = panel._format_requirement(evo_data_empty)
        self.assertEqual(requirement_empty, "")
    
    def test_evolution_panel_format_requirement_unrecognized(self):
        """Test requirement formatting for unrecognized evolution method (AC #7)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 1)
        
        # Test unrecognized method
        evo_data = {
            'method': 'some-future-method',
            'level': None,
            'item': None,
            'trigger': None
        }
        
        requirement = panel._format_requirement(evo_data)
        self.assertEqual(requirement, "Unknown")
    
    def test_evolution_panel_format_requirement_truncation(self):
        """Test requirement text truncation for strings > 24 characters (AC #1, #2, #3)."""
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 1)
        
        # Test long item name that should be truncated
        evo_data = {
            'method': 'use-item',
            'level': None,
            'item': 'incredibly-long-stone-name-that-exceeds-limit',
            'trigger': None
        }
        
        requirement = panel._format_requirement(evo_data)
        # Should be ≤24 characters or have ellipsis
        self.assertTrue(len(requirement) <= 24 or requirement.endswith('...'),
                       f"Requirement '{requirement}' is {len(requirement)} chars, expected ≤24 or ellipsis")
    
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
    # Story 5.3: Single-Stage Pokémon Handling
    # ========================================

    def test_single_stage_renders_centered_no_evolutions_message(self):
        """Story 5.3 AC #1-3: Centered 'No evolutions' message for Ditto."""
        # Insert Ditto (no evolutions)
        with self.db as db:
            db.execute(
                """
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (132, 'ditto', 132, 3, 40, 101, 1),
            )
            db.commit()

        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 132)
        panel.load_data()

        # Render on test surface
        surface = pygame.Surface((800, 480))
        panel.render(surface, 20, 100)

        # Story 5.3: No-evolutions message should allocate cached text surface/rect
        self.assertTrue(hasattr(panel, "_no_evo_text_surface"))
        self.assertTrue(hasattr(panel, "_no_evo_text_rect"))
        self.assertIsNotNone(panel._no_evo_text_surface)
        self.assertIsNotNone(panel._no_evo_text_rect)

        # Verify message is centered within evolution panel region
        panel_width = surface.get_width() - (20 * 2)
        panel_height = 120  # Matches linear evolution panel height
        expected_center = (20 + panel_width // 2, 100 + panel_height // 2)
        self.assertEqual(panel._no_evo_text_rect.center, expected_center)

    def test_single_stage_load_sprites_skips_loading(self):
        """Story 5.3 AC #5: load_sprites() should not load sprites for single-stage Pokémon."""
        # Insert Ditto (no evolutions)
        with self.db as db:
            db.execute(
                """
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (132, 'ditto', 132, 3, 40, 101, 1),
            )
            db.commit()

        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 132)
        panel.load_data()
        panel.load_sprites()

        # For single-stage Pokémon with no evolutions, sprites dict should remain empty
        self.assertEqual(len(panel.evolution_data['evolutions']), 0)
        self.assertEqual(len(panel.sprites), 0)

    def test_single_stage_no_evolutions_across_generations(self):
        """Story 5.3 AC #6: Single-stage Pokémon across Gen 1-3 return empty evolution chains."""
        single_stage_pokemon = [
            (132, 'ditto', 1),   # Gen 1
            (201, 'unown', 2),   # Gen 2
            (359, 'absol', 3),   # Gen 3
        ]

        with self.db as db:
            for pokemon_id, name, generation in single_stage_pokemon:
                db.execute(
                    """
                    INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (pokemon_id, name, pokemon_id, 5, 50, 100, generation),
                )
            db.commit()

        for pokemon_id, name, generation in single_stage_pokemon:
            screen_manager = MockScreenManager(self.db)
            panel = EvolutionPanel(screen_manager, pokemon_id)
            panel.load_data()

            # Each should be a single-stage chain with no evolutions
            self.assertEqual(
                len(panel.evolution_data['stages']),
                1,
                msg=f"{name} (Gen {generation}) should have a single stage",
            )
            self.assertEqual(
                len(panel.evolution_data['evolutions']),
                0,
                msg=f"{name} (Gen {generation}) should have no evolutions",
            )

    def test_single_stage_render_under_50ms(self):
        """Story 5.3 AC #7: Single-stage evolution panel renders under 50ms."""
        # Insert Ditto as a single-stage Pokémon (no evolutions)
        with self.db as db:
            db.execute(
                """
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (132, 'ditto', 132, 3, 40, 101, 1),
            )
            db.commit()

        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 132)
        panel.load_data()

        surface = pygame.Surface((800, 480))

        # Warm-up render to initialize cached text surface
        panel.render(surface, 20, 100)

        start = time.perf_counter()
        panel.render(surface, 20, 100)
        duration_ms = (time.perf_counter() - start) * 1000.0

        self.assertLess(
            duration_ms,
            50.0,
            msg=f"Single-stage render took {duration_ms:.2f}ms, expected <50ms",
        )
    
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
    
    def test_evolution_panel_integration_bulbasaur_level_requirements(self):
        """Integration test: Bulbasaur evolution chain with level requirements (Story 5.4 AC #1)"""
        with self.db as db:
            db.create_schema()
            # Insert Bulbasaur line
            pokemon_data = [
                (1, 'bulbasaur', 1, 7, 69, 64, 1),
                (2, 'ivysaur', 2, 10, 130, 142, 1),
                (3, 'venusaur', 3, 20, 1000, 236, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (1,))
            
            evolutions = [
                (1, 1, 2, 'level-up', 16, None, None, None, None),
                (1, 2, 3, 'level-up', 32, None, None, None, None)
            ]
            db.executemany("""
                INSERT INTO evolutions (evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day, relative_physical_stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evolutions)
            db.commit()
        
        # Create and render panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 1)
        panel.load_data()
        panel.load_sprites()
        
        # Verify requirements are formatted correctly
        evolutions = panel.evolution_data['evolutions']
        self.assertEqual(len(evolutions), 2)
        
        # Check first evolution (Bulbasaur -> Ivysaur at Level 16)
        evo1 = evolutions[0]
        requirement1 = panel._format_requirement(evo1)
        self.assertEqual(requirement1, "Level 16")
        
        # Check second evolution (Ivysaur -> Venusaur at Level 32)
        evo2 = evolutions[1]
        requirement2 = panel._format_requirement(evo2)
        self.assertEqual(requirement2, "Level 32")
        
        # Render and verify no crashes
        surface = pygame.Surface((800, 480))
        panel.render(surface, 20, 100)
    
    def test_evolution_panel_integration_pikachu_stone_requirement(self):
        """Integration test: Pikachu evolution with Thunder Stone (Story 5.4 AC #2)"""
        with self.db as db:
            db.create_schema()
            # Insert Pichu, Pikachu, Raichu
            pokemon_data = [
                (172, 'pichu', 172, 3, 20, 41, 2),
                (25, 'pikachu', 25, 4, 60, 112, 1),
                (26, 'raichu', 26, 8, 300, 243, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (10,))
            
            evolutions = [
                (10, 172, 25, 'level-up', None, None, 220, None, None),  # Happiness
                (10, 25, 26, 'use-item', None, 'thunder-stone', None, None, None)  # Stone
            ]
            db.executemany("""
                INSERT INTO evolutions (evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day, relative_physical_stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evolutions)
            db.commit()
        
        # Create panel for Pikachu
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 25)
        panel.load_data()
        
        # Find stone evolution
        evolutions = panel.evolution_data['evolutions']
        stone_evo = next(e for e in evolutions if e['to_id'] == 26)
        
        # Verify stone requirement formatting
        requirement = panel._format_requirement(stone_evo)
        self.assertEqual(requirement, "Thunder Stone")
    
    def test_evolution_panel_integration_onix_trade_with_item(self):
        """Integration test: Onix -> Steelix with Metal Coat (Story 5.4 AC #3)"""
        with self.db as db:
            db.create_schema()
            # Insert Onix and Steelix
            pokemon_data = [
                (95, 'onix', 95, 88, 2100, 77, 1),
                (208, 'steelix', 208, 92, 4000, 179, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (39,))
            
            db.execute("""
                INSERT INTO evolutions (evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day, relative_physical_stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (39, 95, 208, 'trade', None, 'metal-coat', None, None, None))
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 95)
        panel.load_data()
        
        # Verify trade-with-item requirement
        evo = panel.evolution_data['evolutions'][0]
        requirement = panel._format_requirement(evo)
        self.assertEqual(requirement, "Trade holding Metal Coat")
    
    def test_evolution_panel_integration_golbat_happiness(self):
        """Integration test: Golbat -> Crobat with happiness (Story 5.4 AC #7)"""
        with self.db as db:
            db.create_schema()
            # Insert Zubat, Golbat, Crobat
            pokemon_data = [
                (41, 'zubat', 41, 8, 75, 49, 1),
                (42, 'golbat', 42, 16, 550, 159, 1),
                (169, 'crobat', 169, 18, 750, 241, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (21,))
            
            evolutions = [
                (21, 41, 42, 'level-up', 22, None, None, None, None),
                (21, 42, 169, 'level-up', None, None, 220, None, None)  # Happiness
            ]
            db.executemany("""
                INSERT INTO evolutions (evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day, relative_physical_stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evolutions)
            db.commit()
        
        # Create panel for Golbat
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 42)
        panel.load_data()
        
        # Find happiness evolution
        evolutions = panel.evolution_data['evolutions']
        happiness_evo = next(e for e in evolutions if e['to_id'] == 169)
        
        # Verify happiness requirement
        requirement = panel._format_requirement(happiness_evo)
        self.assertEqual(requirement, "High Friendship")
    
    def test_evolution_panel_performance_with_requirements(self):
        """Performance test: Rendering with requirement text stays within budget (Story 5.4 AC #6)"""
        with self.db as db:
            db.create_schema()
            # Insert three-stage evolution
            pokemon_data = [
                (4, 'charmander', 4, 6, 85, 62, 1),
                (5, 'charmeleon', 5, 11, 190, 142, 1),
                (6, 'charizard', 6, 17, 905, 240, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (2,))
            
            evolutions = [
                (2, 4, 5, 'level-up', 16, None, None, None, None),
                (2, 5, 6, 'level-up', 36, None, None, None, None)
            ]
            db.executemany("""
                INSERT INTO evolutions (evolution_chain_id, from_pokemon_id, to_pokemon_id,
                                       trigger, min_level, item, min_happiness, time_of_day, relative_physical_stats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, evolutions)
            db.commit()
        
        # Create panel
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 5)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Measure first render (cold cache)
        start_time = time.perf_counter()
        panel.render(surface, 20, 100)
        first_render_time = (time.perf_counter() - start_time) * 1000
        
        # AC #6: First render ≤ 200ms
        self.assertLess(first_render_time, 200.0,
                       f"First render with requirements took {first_render_time:.2f}ms, expected <200ms")
        
        # Measure cached render
        start_time = time.perf_counter()
        panel.render(surface, 20, 100)
        cached_render_time = (time.perf_counter() - start_time) * 1000
        
        # AC #6: Cached render ≤ 50ms
        self.assertLess(cached_render_time, 50.0,
                       f"Cached render with requirements took {cached_render_time:.2f}ms, expected <50ms")
    
    # Story 5.6 Task 3.2: EvolutionPanel Data Accuracy Validation
    # Test panel's internal data structures match expected values for curated sample
    
    def test_panel_data_accuracy_charmander_linear_three_stage(self):
        """
        Task 3.2: Validate EvolutionPanel data structure for linear 3-stage chain.
        
        Test Case: Charmander line (#4 → #5 → #6)
        AC #4: Panel's evolution_data matches expected structure and values
        """
        with self.db as db:
            db.create_schema()
            
            # Insert Charmander line
            pokemon_data = [
                (4, 'charmander', 4, 6, 85, 62, 1),
                (5, 'charmeleon', 5, 11, 190, 142, 1),
                (6, 'charizard', 6, 17, 905, 240, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (2,))
            
            evolutions = [
                (2, 4, 5, 16, 'level-up', None),
                (2, 5, 6, 36, 'level-up', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        panel.load_data()
        
        # Validate internal evolution_data structure
        self.assertIsNotNone(panel.evolution_data)
        self.assertEqual(len(panel.evolution_data['stages']), 3)
        self.assertEqual(panel.evolution_data['current_stage'], 1)
        self.assertFalse(panel.evolution_data['is_branching'])
        
        # Validate cached evolutions list
        self.assertEqual(len(panel.evolutions), 2)
        
        # Validate stage pokemon IDs
        stage_ids = [stage['pokemon_id'] for stage in panel.evolution_data['stages']]
        self.assertEqual(stage_ids, [4, 5, 6])
    
    def test_panel_data_accuracy_eevee_branching(self):
        """
        Task 3.2: Validate EvolutionPanel data structure for branching chain.
        
        Test Case: Eevee line (#133 → 5 evolutions)
        AC #4: Panel correctly identifies branching and loads all evolution paths
        """
        with self.db as db:
            db.create_schema()
            
            # Insert Eevee and evolutions
            pokemon_data = [
                (133, 'eevee', 133, 3, 65, 65, 1),
                (134, 'vaporeon', 134, 10, 290, 184, 1),
                (135, 'jolteon', 135, 8, 245, 184, 1),
                (136, 'flareon', 136, 9, 250, 184, 1),
                (196, 'espeon', 196, 9, 265, 184, 2),
                (197, 'umbreon', 197, 10, 270, 184, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            
            evolutions = [
                (67, 133, 134, None, 'use-item', 'water-stone'),
                (67, 133, 135, None, 'use-item', 'thunder-stone'),
                (67, 133, 136, None, 'use-item', 'fire-stone'),
                (67, 133, 196, None, 'level-up', None),
                (67, 133, 197, None, 'level-up', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 133)
        panel.load_data()
        
        # Validate branching flag
        self.assertTrue(panel.evolution_data['is_branching'])
        
        # Validate all 5 evolutions present
        self.assertEqual(len(panel.evolutions), 5)
        
        # Validate evolution target IDs
        evolution_targets = {e['to_id'] for e in panel.evolutions}
        self.assertEqual(evolution_targets, {134, 135, 136, 196, 197})
    
    def test_panel_data_accuracy_ditto_single_stage(self):
        """
        Task 3.2: Validate EvolutionPanel data structure for single-stage Pokémon.
        
        Test Case: Ditto (#132) - no evolutions
        AC #4, #5: Panel handles single-stage gracefully with empty evolution list
        """
        with self.db as db:
            db.create_schema()
            
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (132, 'ditto', 132, 3, 40, 101, 1))
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (66,))
            db.commit()
        
        # Create panel and load data
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 132)
        panel.load_data()
        
        # Validate single-stage structure
        self.assertEqual(len(panel.evolution_data['stages']), 1)
        self.assertEqual(len(panel.evolutions), 0)
        self.assertEqual(panel.evolution_data['current_stage'], 1)
        self.assertFalse(panel.evolution_data['is_branching'])
    
    def test_panel_data_accuracy_machoke_trade(self):
        """
        Task 3.2: Validate EvolutionPanel data structure for trade evolution.
        
        Test Case: Machoke line (#66 → #67 → #68)
        AC #4: Panel correctly identifies trade evolution requirement
        """
        with self.db as db:
            db.create_schema()
            
            pokemon_data = [
                (66, 'machop', 66, 8, 195, 61, 1),
                (67, 'machoke', 67, 15, 705, 142, 1),
                (68, 'machamp', 68, 16, 1300, 227, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (34,))
            
            evolutions = [
                (34, 66, 67, 28, 'level-up', None),
                (34, 67, 68, None, 'trade', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 67)
        panel.load_data()
        
        # Validate trade evolution present
        trade_evo = next((e for e in panel.evolutions if e['to_id'] == 68), None)
        self.assertIsNotNone(trade_evo)
        self.assertEqual(trade_evo['method'], 'trade')
    
    def test_panel_data_accuracy_pikachu_stone(self):
        """
        Task 3.2: Validate EvolutionPanel data structure for stone evolution.
        
        Test Case: Pikachu line (#172 → #25 → #26)
        AC #4: Panel correctly identifies Thunder Stone requirement
        """
        with self.db as db:
            db.create_schema()
            
            pokemon_data = [
                (172, 'pichu', 172, 3, 20, 41, 2),
                (25, 'pikachu', 25, 4, 60, 112, 1),
                (26, 'raichu', 26, 8, 300, 243, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (10,))
            
            evolutions = [
                (10, 172, 25, None, 'level-up', None),
                (10, 25, 26, None, 'use-item', 'thunder-stone')
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 25)
        panel.load_data()
        
        # Validate Thunder Stone evolution present
        stone_evo = next((e for e in panel.evolutions if e['to_id'] == 26), None)
        self.assertIsNotNone(stone_evo)
        self.assertEqual(stone_evo['method'], 'use-item')
        self.assertEqual(stone_evo['item'], 'thunder-stone')
    
    def test_panel_data_accuracy_golbat_happiness(self):
        """
        Task 3.2: Validate EvolutionPanel data structure for happiness evolution.
        
        Test Case: Golbat line (#41 → #42 → #169)
        AC #4: Panel correctly identifies high-friendship requirement
        """
        with self.db as db:
            db.create_schema()
            
            pokemon_data = [
                (41, 'zubat', 41, 8, 75, 49, 1),
                (42, 'golbat', 42, 16, 550, 159, 1),
                (169, 'crobat', 169, 18, 750, 241, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (21,))
            
            evolutions = [
                (21, 41, 42, 22, 'level-up', None),
                (21, 42, 169, None, 'level-up', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            # Add happiness requirement
            db.execute("""
                UPDATE evolutions 
                SET min_happiness = 220 
                WHERE from_pokemon_id = 42 AND to_pokemon_id = 169
            """)
            
            db.commit()
        
        # Create panel and load data
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 42)
        panel.load_data()
        
        # Validate happiness evolution present
        happiness_evo = next((e for e in panel.evolutions if e['to_id'] == 169), None)
        self.assertIsNotNone(happiness_evo)
        self.assertEqual(happiness_evo['method'], 'level-up')
        self.assertEqual(happiness_evo['trigger'], 'high-friendship')
    
    # Story 5.6 Task 4: Performance-Focused Tests
    # Using pytest.mark.performance decorator for performance test identification
    # Run with: pytest tests/test_evolution_panel.py -v -m performance
    
    @pytest.mark.performance
    def test_performance_charmander_first_render(self):
        """
        Task 4.1: Test first-render performance for linear 3-stage chain.
        
        Test Case: Charmander line (#4 → #5 → #6)
        Target: < 200ms first render on Raspberry Pi 3B+
        AC #1: First render completes within budget
        Margin: ±20% for cross-machine stability
        """
        with self.db as db:
            db.create_schema()
            
            # Insert Charmander line
            pokemon_data = [
                (4, 'charmander', 4, 6, 85, 62, 1),
                (5, 'charmeleon', 5, 11, 190, 142, 1),
                (6, 'charizard', 6, 17, 905, 240, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (2,))
            
            evolutions = [
                (2, 4, 5, 16, 'level-up', None),
                (2, 5, 6, 36, 'level-up', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data/sprites
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Measure first render (cold cache)
        start_time = time.perf_counter()
        panel.render(surface, 20, 100)
        first_render_time = (time.perf_counter() - start_time) * 1000
        
        # AC #1: First render ≤ 200ms (with 20% margin = 240ms max)
        self.assertLess(first_render_time, 240.0,
                       f"First render took {first_render_time:.2f}ms, expected <200ms (240ms with margin)")
        
        # Log timing for monitoring
        print(f"\n[PERF] Charmander first render: {first_render_time:.2f}ms")
    
    @pytest.mark.performance
    def test_performance_charmander_cached_render(self):
        """
        Task 4.1: Test cached-render performance for linear 3-stage chain.
        
        Test Case: Charmander line (repeat render)
        Target: < 50ms cached render
        AC #2: Cached render uses cached data/sprites efficiently
        Margin: ±20% for cross-machine stability
        """
        with self.db as db:
            db.create_schema()
            
            # Insert Charmander line
            pokemon_data = [
                (4, 'charmander', 4, 6, 85, 62, 1),
                (5, 'charmeleon', 5, 11, 190, 142, 1),
                (6, 'charizard', 6, 17, 905, 240, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (2,))
            
            evolutions = [
                (2, 4, 5, 16, 'level-up', None),
                (2, 5, 6, 36, 'level-up', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data/sprites
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 4)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Warm up cache with first render
        panel.render(surface, 20, 100)
        
        # Measure cached render
        start_time = time.perf_counter()
        panel.render(surface, 20, 100)
        cached_render_time = (time.perf_counter() - start_time) * 1000
        
        # AC #2: Cached render ≤ 50ms (with 20% margin = 60ms max)
        self.assertLess(cached_render_time, 60.0,
                       f"Cached render took {cached_render_time:.2f}ms, expected <50ms (60ms with margin)")
        
        # Log timing for monitoring
        print(f"\n[PERF] Charmander cached render: {cached_render_time:.2f}ms")
    
    @pytest.mark.performance
    def test_performance_eevee_first_render_worst_case(self):
        """
        Task 4.1: Test first-render performance for worst-case branching.
        
        Test Case: Eevee (#133) with 5 evolutions (6 total sprites)
        Target: < 250ms first render on Raspberry Pi 3B+
        AC #3: Worst-case branching meets performance budget
        Margin: ±20% for cross-machine stability
        """
        with self.db as db:
            db.create_schema()
            
            # Insert Eevee and all Gen 1-2 evolutions
            pokemon_data = [
                (133, 'eevee', 133, 3, 65, 65, 1),
                (134, 'vaporeon', 134, 10, 290, 184, 1),
                (135, 'jolteon', 135, 8, 245, 184, 1),
                (136, 'flareon', 136, 9, 250, 184, 1),
                (196, 'espeon', 196, 9, 265, 184, 2),
                (197, 'umbreon', 197, 10, 270, 184, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            
            evolutions = [
                (67, 133, 134, None, 'use-item', 'water-stone'),
                (67, 133, 135, None, 'use-item', 'thunder-stone'),
                (67, 133, 136, None, 'use-item', 'fire-stone'),
                (67, 133, 196, None, 'level-up', None),
                (67, 133, 197, None, 'level-up', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data/sprites
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 133)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Measure first render (cold cache)
        start_time = time.perf_counter()
        panel.render(surface, 20, 100)
        first_render_time = (time.perf_counter() - start_time) * 1000
        
        # AC #3: First render ≤ 250ms (with 20% margin = 300ms max)
        self.assertLess(first_render_time, 300.0,
                       f"Eevee first render took {first_render_time:.2f}ms, expected <250ms (300ms with margin)")
        
        # Log timing for monitoring
        print(f"\n[PERF] Eevee first render (worst-case): {first_render_time:.2f}ms")
    
    @pytest.mark.performance
    def test_performance_eevee_cached_render_worst_case(self):
        """
        Task 4.1: Test cached-render performance for worst-case branching.
        
        Test Case: Eevee (repeat render)
        Target: < 50ms cached render
        AC #3: Cached worst-case branching remains fast
        Margin: ±20% for cross-machine stability
        """
        with self.db as db:
            db.create_schema()
            
            # Insert Eevee and all Gen 1-2 evolutions
            pokemon_data = [
                (133, 'eevee', 133, 3, 65, 65, 1),
                (134, 'vaporeon', 134, 10, 290, 184, 1),
                (135, 'jolteon', 135, 8, 245, 184, 1),
                (136, 'flareon', 136, 9, 250, 184, 1),
                (196, 'espeon', 196, 9, 265, 184, 2),
                (197, 'umbreon', 197, 10, 270, 184, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            
            evolutions = [
                (67, 133, 134, None, 'use-item', 'water-stone'),
                (67, 133, 135, None, 'use-item', 'thunder-stone'),
                (67, 133, 136, None, 'use-item', 'fire-stone'),
                (67, 133, 196, None, 'level-up', None),
                (67, 133, 197, None, 'level-up', None)
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item)
                VALUES (?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
        
        # Create panel and load data/sprites
        screen_manager = MockScreenManager(self.db)
        panel = EvolutionPanel(screen_manager, 133)
        panel.load_data()
        panel.load_sprites()
        
        # Create test surface
        surface = pygame.Surface((800, 480))
        
        # Warm up cache with first render
        panel.render(surface, 20, 100)
        
        # Measure cached render
        start_time = time.perf_counter()
        panel.render(surface, 20, 100)
        cached_render_time = (time.perf_counter() - start_time) * 1000
        
        # AC #3: Cached render ≤ 50ms (with 20% margin = 60ms max)
        self.assertLess(cached_render_time, 60.0,
                       f"Eevee cached render took {cached_render_time:.2f}ms, expected <50ms (60ms with margin)")
        
        # Log timing for monitoring
        print(f"\n[PERF] Eevee cached render (worst-case): {cached_render_time:.2f}ms")


if __name__ == '__main__':
    unittest.main()

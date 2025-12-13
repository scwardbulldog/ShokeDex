"""
Tests for database module
"""

import unittest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import Database


class TestDatabase(unittest.TestCase):
    """Test Database class"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = Database(self.db_path)
        
    def tearDown(self):
        """Clean up temporary database"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        os.rmdir(self.temp_dir)
        
    def test_database_creation(self):
        """Test database file is created"""
        with self.db as db:
            db.create_schema()
        self.assertTrue(os.path.exists(self.db_path))
        
    def test_schema_creation(self):
        """Test schema tables are created"""
        with self.db as db:
            db.create_schema()
            
            # Check that all tables exist
            cursor = db.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' 
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'abilities',
                'evolution_chains',
                'evolutions',
                'moves',
                'pokemon',
                'pokemon_abilities',
                'pokemon_moves',
                'pokemon_stats',
                'pokemon_types',
                'schema_version',
                'stats',
                'types'
            ]
            
            for table in expected_tables:
                self.assertIn(table, tables, f"Table {table} not found")
                
    def test_schema_version(self):
        """Test schema version tracking"""
        with self.db as db:
            db.create_schema()
            version = db.get_schema_version()
            self.assertEqual(version, 1)
            
    def test_insert_and_query_pokemon(self):
        """Test inserting and querying Pokémon"""
        with self.db as db:
            db.create_schema()
            
            # Insert a test Pokémon
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (25, 'pikachu', 25, 4, 60, 112, 1))
            db.commit()
            
            # Query by ID
            pokemon = db.get_pokemon_by_id(25)
            self.assertIsNotNone(pokemon)
            self.assertEqual(pokemon['name'], 'pikachu')
            self.assertEqual(pokemon['generation'], 1)
            
            # Query by name
            pokemon = db.get_pokemon_by_name('pikachu')
            self.assertIsNotNone(pokemon)
            self.assertEqual(pokemon['id'], 25)
            
    def test_insert_types(self):
        """Test inserting types"""
        with self.db as db:
            db.create_schema()
            
            # Insert types
            db.execute("INSERT INTO types (id, name) VALUES (?, ?)", (1, 'normal'))
            db.execute("INSERT INTO types (id, name) VALUES (?, ?)", (10, 'fire'))
            db.execute("INSERT INTO types (id, name) VALUES (?, ?)", (11, 'water'))
            db.commit()
            
            # Query types
            cursor = db.execute("SELECT COUNT(*) FROM types")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 3)
            
    def test_insert_stats(self):
        """Test inserting stats"""
        with self.db as db:
            db.create_schema()
            
            # Insert stats
            stats = [
                (1, 'hp'),
                (2, 'attack'),
                (3, 'defense'),
                (4, 'special-attack'),
                (5, 'special-defense'),
                (6, 'speed')
            ]
            db.executemany("INSERT INTO stats (id, name) VALUES (?, ?)", stats)
            db.commit()
            
            # Query stats
            cursor = db.execute("SELECT COUNT(*) FROM stats")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 6)
            
    def test_pokemon_with_types_and_stats(self):
        """Test Pokémon with types and stats"""
        with self.db as db:
            db.create_schema()
            
            # Insert Pokémon
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (25, 'pikachu', 25, 4, 60, 112, 1))
            
            # Insert type
            db.execute("INSERT INTO types (id, name) VALUES (?, ?)", (13, 'electric'))
            
            # Link Pokémon to type
            db.execute("""
                INSERT INTO pokemon_types (pokemon_id, type_id, slot)
                VALUES (?, ?, ?)
            """, (25, 13, 1))
            
            # Insert stats
            stats = [
                (1, 'hp'),
                (2, 'attack'),
                (3, 'defense')
            ]
            db.executemany("INSERT INTO stats (id, name) VALUES (?, ?)", stats)
            
            # Link Pokémon stats
            pokemon_stats = [
                (25, 1, 35, 0),  # HP
                (25, 2, 55, 0),  # Attack
                (25, 3, 40, 0)   # Defense
            ]
            db.executemany("""
                INSERT INTO pokemon_stats (pokemon_id, stat_id, base_stat, effort)
                VALUES (?, ?, ?, ?)
            """, pokemon_stats)
            
            db.commit()
            
            # Query Pokémon with types
            pokemon = db.get_pokemon_by_id(25)
            self.assertEqual(pokemon['types'], 'electric')
            
            # Query stats
            stats = db.get_pokemon_stats(25)
            self.assertEqual(len(stats), 3)
            self.assertEqual(stats[0]['name'], 'hp')
            self.assertEqual(stats[0]['base_stat'], 35)
            
    def test_evolution_chain(self):
        """Test evolution chain storage"""
        with self.db as db:
            db.create_schema()
            
            # Insert Pokémon
            pokemon_data = [
                (172, 'pichu', 172, 3, 20, 41, 2),
                (25, 'pikachu', 25, 4, 60, 112, 1),
                (26, 'raichu', 26, 8, 300, 243, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            # Create evolution chain
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (10,))
            
            # Add evolutions
            evolutions = [
                (10, 172, 25, None, 'level-up', None, 220, None),  # Pichu → Pikachu (friendship)
                (10, 25, 26, None, 'use-item', 'thunder-stone', None, None)  # Pikachu → Raichu
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
            
            # Query evolutions
            evolutions = db.get_evolutions(25)
            self.assertEqual(len(evolutions), 2)
    
    def test_get_evolution_chain_three_stages(self):
        """Test get_evolution_chain for Charmander line (3-stage chain)"""
        with self.db as db:
            db.create_schema()
            
            # Insert Charmander, Charmeleon, Charizard
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
                (2, 4, 5, 16, 'level-up', None, None, None),  # Charmander → Charmeleon at 16
                (2, 5, 6, 36, 'level-up', None, None, None)   # Charmeleon → Charizard at 36
            ]
            db.executemany("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, evolutions)
            
            db.commit()
            
            # Test from Charmander's perspective
            chain = db.get_evolution_chain(4)
            self.assertEqual(chain['chain_id'], 2)
            self.assertEqual(len(chain['stages']), 3)
            self.assertEqual(len(chain['evolutions']), 2)
            self.assertEqual(chain['current_stage'], 1)
            
            # Verify stages are ordered correctly
            self.assertEqual(chain['stages'][0]['pokemon_id'], 4)
            self.assertEqual(chain['stages'][0]['name'], 'charmander')
            self.assertEqual(chain['stages'][0]['stage'], 1)
            
            self.assertEqual(chain['stages'][1]['pokemon_id'], 5)
            self.assertEqual(chain['stages'][1]['name'], 'charmeleon')
            self.assertEqual(chain['stages'][1]['stage'], 2)
            
            self.assertEqual(chain['stages'][2]['pokemon_id'], 6)
            self.assertEqual(chain['stages'][2]['name'], 'charizard')
            self.assertEqual(chain['stages'][2]['stage'], 3)
            
            # Verify evolution relationships
            self.assertEqual(chain['evolutions'][0]['from_id'], 4)
            self.assertEqual(chain['evolutions'][0]['to_id'], 5)
            self.assertEqual(chain['evolutions'][0]['level'], 16)
            self.assertEqual(chain['evolutions'][0]['method'], 'level-up')
            
            self.assertEqual(chain['evolutions'][1]['from_id'], 5)
            self.assertEqual(chain['evolutions'][1]['to_id'], 6)
            self.assertEqual(chain['evolutions'][1]['level'], 36)
            
            # Test from Charmeleon's perspective (middle stage)
            chain_middle = db.get_evolution_chain(5)
            self.assertEqual(chain_middle['current_stage'], 2)
            self.assertEqual(len(chain_middle['stages']), 3)
            
            # Test from Charizard's perspective (final stage)
            chain_final = db.get_evolution_chain(6)
            self.assertEqual(chain_final['current_stage'], 3)
            self.assertEqual(len(chain_final['stages']), 3)
    
    def test_get_evolution_chain_single_stage(self):
        """Test get_evolution_chain for Pokemon with no evolutions (Ditto)"""
        with self.db as db:
            db.create_schema()
            
            # Insert Ditto (no evolutions)
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (132, 'ditto', 132, 3, 40, 101, 1))
            
            db.commit()
            
            # Test single-stage Pokemon
            chain = db.get_evolution_chain(132)
            self.assertIsNone(chain['chain_id'])
            self.assertEqual(len(chain['stages']), 1)
            self.assertEqual(len(chain['evolutions']), 0)
            self.assertEqual(chain['current_stage'], 1)
            
            self.assertEqual(chain['stages'][0]['pokemon_id'], 132)
            self.assertEqual(chain['stages'][0]['name'], 'ditto')
            self.assertEqual(chain['stages'][0]['stage'], 1)
    
    def test_get_evolution_chain_stone_evolution(self):
        """Test get_evolution_chain with stone evolution (Pikachu)"""
        with self.db as db:
            db.create_schema()
            
            # Insert Pikachu and Raichu
            pokemon_data = [
                (25, 'pikachu', 25, 4, 60, 112, 1),
                (26, 'raichu', 26, 8, 300, 243, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            # Create evolution chain
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (10,))
            
            # Add stone evolution
            db.execute("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (10, 25, 26, None, 'use-item', 'thunder-stone', None, None))
            
            db.commit()
            
            # Test stone evolution
            chain = db.get_evolution_chain(25)
            self.assertEqual(len(chain['evolutions']), 1)
            self.assertEqual(chain['evolutions'][0]['method'], 'use-item')
            self.assertEqual(chain['evolutions'][0]['item'], 'thunder-stone')
            self.assertIsNone(chain['evolutions'][0]['level'])
            
            
    def test_context_manager(self):
        """Test database context manager"""
        with Database(self.db_path) as db:
            db.create_schema()
            self.assertIsNotNone(db.conn)
            
        # Connection should be closed after exiting context
        self.assertIsNone(db.conn)
    
    def test_generation_ranges_constant(self):
        """Test GENERATION_RANGES constant has correct values"""
        # This tests the constant defined in the method
        with self.db as db:
            db.create_schema()
            
            # Insert test Pokemon across all generations
            pokemon_data = [
                (1, 'Bulbasaur', 1, 7, 69, 64, 1, 1),      # Kanto start
                (151, 'Mew', 151, 4, 40, 270, 1, 1),       # Kanto end
                (152, 'Chikorita', 152, 9, 64, 64, 2, 1),  # Johto start
                (251, 'Celebi', 251, 6, 50, 270, 2, 1),    # Johto end
                (252, 'Treecko', 252, 5, 50, 62, 3, 1),    # Hoenn start
                (386, 'Deoxys', 386, 17, 608, 270, 3, 1)   # Hoenn end
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            db.commit()
            
            # Test generation 1 boundaries
            gen1 = db.get_pokemon_by_generation(1)
            gen1_ids = [p['id'] for p in gen1]
            self.assertIn(1, gen1_ids, "Bulbasaur (#1) should be in Kanto")
            self.assertIn(151, gen1_ids, "Mew (#151) should be in Kanto")
            self.assertNotIn(152, gen1_ids, "Chikorita (#152) should NOT be in Kanto")
            
            # Test generation 2 boundaries
            gen2 = db.get_pokemon_by_generation(2)
            gen2_ids = [p['id'] for p in gen2]
            self.assertIn(152, gen2_ids, "Chikorita (#152) should be in Johto")
            self.assertIn(251, gen2_ids, "Celebi (#251) should be in Johto")
            self.assertNotIn(151, gen2_ids, "Mew (#151) should NOT be in Johto")
            self.assertNotIn(252, gen2_ids, "Treecko (#252) should NOT be in Johto")
            
            # Test generation 3 boundaries
            gen3 = db.get_pokemon_by_generation(3)
            gen3_ids = [p['id'] for p in gen3]
            self.assertIn(252, gen3_ids, "Treecko (#252) should be in Hoenn")
            self.assertIn(386, gen3_ids, "Deoxys (#386) should be in Hoenn")
            self.assertNotIn(251, gen3_ids, "Celebi (#251) should NOT be in Hoenn")
    
    def test_get_pokemon_by_generation_kanto(self):
        """Test Kanto generation returns Pokemon #1-151"""
        with self.db as db:
            db.create_schema()
            
            # Insert all Kanto Pokemon (simplified - just IDs matter)
            kanto_pokemon = [
                (i, f'Pokemon{i}', i, 10, 100, 100, 1, 1)
                for i in range(1, 152)  # 1 to 151 inclusive
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, kanto_pokemon)
            db.commit()
            
            # Query generation 1
            results = db.get_pokemon_by_generation(1)
            
            self.assertEqual(len(results), 151, "Kanto should have 151 Pokemon")
            self.assertEqual(results[0]['id'], 1, "First Pokemon should be #1 (Bulbasaur)")
            self.assertEqual(results[-1]['id'], 151, "Last Pokemon should be #151 (Mew)")
    
    def test_get_pokemon_by_generation_johto(self):
        """Test Johto generation returns Pokemon #152-251"""
        with self.db as db:
            db.create_schema()
            
            # Insert all Johto Pokemon
            johto_pokemon = [
                (i, f'Pokemon{i}', i, 10, 100, 100, 2, 1)
                for i in range(152, 252)  # 152 to 251 inclusive
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, johto_pokemon)
            db.commit()
            
            # Query generation 2
            results = db.get_pokemon_by_generation(2)
            
            self.assertEqual(len(results), 100, "Johto should have 100 Pokemon")
            self.assertEqual(results[0]['id'], 152, "First Pokemon should be #152 (Chikorita)")
            self.assertEqual(results[-1]['id'], 251, "Last Pokemon should be #251 (Celebi)")
    
    def test_get_pokemon_by_generation_hoenn(self):
        """Test Hoenn generation returns Pokemon #252-386"""
        with self.db as db:
            db.create_schema()
            
            # Insert all Hoenn Pokemon
            hoenn_pokemon = [
                (i, f'Pokemon{i}', i, 10, 100, 100, 3, 1)
                for i in range(252, 387)  # 252 to 386 inclusive
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, hoenn_pokemon)
            db.commit()
            
            # Query generation 3
            results = db.get_pokemon_by_generation(3)
            
            self.assertEqual(len(results), 135, "Hoenn should have 135 Pokemon")
            self.assertEqual(results[0]['id'], 252, "First Pokemon should be #252 (Treecko)")
            self.assertEqual(results[-1]['id'], 386, "Last Pokemon should be #386 (Deoxys)")
    
    def test_invalid_generation_raises_error(self):
        """Test invalid generation parameter raises ValueError"""
        with self.db as db:
            db.create_schema()
            
            # Test generation 0 (invalid)
            with self.assertRaises(ValueError) as context:
                db.get_pokemon_by_generation(0)
            self.assertIn("Invalid generation", str(context.exception))
            self.assertIn("Must be 1, 2, or 3", str(context.exception))
            
            # Test generation 4 (invalid)
            with self.assertRaises(ValueError) as context:
                db.get_pokemon_by_generation(4)
            self.assertIn("Invalid generation", str(context.exception))
            
            # Test negative generation (invalid)
            with self.assertRaises(ValueError):
                db.get_pokemon_by_generation(-1)
    
    def test_parameterized_query_safety(self):
        """Test SQL injection prevention with parameterized queries"""
        with self.db as db:
            db.create_schema()
            
            # Insert test data
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation, is_default)
                VALUES (25, 'Pikachu', 25, 4, 60, 112, 1, 1)
            """)
            db.commit()
            
            # Attempt SQL injection with malicious generation value
            # This should fail at type validation before reaching SQL
            malicious_input = "1; DROP TABLE pokemon; --"
            
            # Should raise ValueError due to type checking (not int)
            with self.assertRaises(ValueError):
                db.get_pokemon_by_generation(malicious_input)
            
            # Verify table still exists
            cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pokemon'")
            result = cursor.fetchone()
            self.assertIsNotNone(result, "Pokemon table should still exist after injection attempt")
            
            # Verify data still intact
            cursor = db.execute("SELECT COUNT(*) FROM pokemon")
            count = cursor.fetchone()[0]
            self.assertEqual(count, 1, "Pokemon data should be intact")
    
    def test_query_returns_ordered_by_id(self):
        """Test that generation queries return Pokemon ordered by National Dex number"""
        with self.db as db:
            db.create_schema()
            
            # Insert Pokemon out of order
            pokemon_data = [
                (151, 'Mew', 151, 4, 40, 270, 1, 1),
                (1, 'Bulbasaur', 1, 7, 69, 64, 1, 1),
                (75, 'Graveler', 75, 10, 1050, 137, 1, 1),
                (25, 'Pikachu', 25, 4, 60, 112, 1, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation, is_default)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            db.commit()
            
            # Query should return ordered by ID
            results = db.get_pokemon_by_generation(1)
            ids = [p['id'] for p in results]
            
            self.assertEqual(ids, [1, 25, 75, 151], "Pokemon should be ordered by ID")
    
    def test_get_evolution_chain_trade_with_item(self):
        """Test get_evolution_chain with trade-item evolution (Onix -> Steelix)"""
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
            
            # Create evolution chain
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (39,))
            
            # Add trade-with-item evolution
            db.execute("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (39, 95, 208, None, 'trade', 'metal-coat', None, None))
            
            db.commit()
            
            # Test trade-with-item evolution
            chain = db.get_evolution_chain(95)
            self.assertEqual(len(chain['evolutions']), 1)
            self.assertEqual(chain['evolutions'][0]['method'], 'trade')
            self.assertEqual(chain['evolutions'][0]['item'], 'metal-coat')
    
    def test_get_evolution_chain_happiness(self):
        """Test get_evolution_chain with happiness evolution (Pichu -> Pikachu)"""
        with self.db as db:
            db.create_schema()
            
            # Insert Pichu and Pikachu
            pokemon_data = [
                (172, 'pichu', 172, 3, 20, 41, 2),
                (25, 'pikachu', 25, 4, 60, 112, 1)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            # Create evolution chain
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (10,))
            
            # Add happiness evolution
            db.execute("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (10, 172, 25, None, 'level-up', None, 220, None))
            
            db.commit()
            
            # Test happiness evolution
            chain = db.get_evolution_chain(172)
            self.assertEqual(len(chain['evolutions']), 1)
            self.assertEqual(chain['evolutions'][0]['method'], 'level-up')
            # Trigger should be 'high-friendship' based on min_happiness presence
            self.assertEqual(chain['evolutions'][0]['trigger'], 'high-friendship')
    
    def test_get_evolution_chain_happiness_day(self):
        """Test get_evolution_chain with happiness-day evolution (Eevee -> Espeon)"""
        with self.db as db:
            db.create_schema()
            
            # Insert Eevee and Espeon
            pokemon_data = [
                (133, 'eevee', 133, 3, 65, 65, 1),
                (196, 'espeon', 196, 9, 265, 184, 2)
            ]
            db.executemany("""
                INSERT INTO pokemon (id, name, species_id, height, weight, base_experience, generation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, pokemon_data)
            
            # Create evolution chain
            db.execute("INSERT INTO evolution_chains (id) VALUES (?)", (67,))
            
            # Add happiness-day evolution
            db.execute("""
                INSERT INTO evolutions 
                (evolution_chain_id, from_pokemon_id, to_pokemon_id, min_level, trigger, item, min_happiness, time_of_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (67, 133, 196, None, 'level-up', None, 220, 'day'))
            
            db.commit()
            
            # Test happiness-day evolution
            chain = db.get_evolution_chain(133)
            self.assertGreaterEqual(len(chain['evolutions']), 1)
            # Find the Espeon evolution
            espeon_evo = next(e for e in chain['evolutions'] if e['to_id'] == 196)
            self.assertEqual(espeon_evo['method'], 'level-up')
            self.assertEqual(espeon_evo['trigger'], 'happiness-day')


if __name__ == '__main__':
    unittest.main()

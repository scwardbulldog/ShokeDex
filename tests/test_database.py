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
            
            
    def test_context_manager(self):
        """Test database context manager"""
        with Database(self.db_path) as db:
            db.create_schema()
            self.assertIsNotNone(db.conn)
            
        # Connection should be closed after exiting context
        self.assertIsNone(db.conn)


if __name__ == '__main__':
    unittest.main()

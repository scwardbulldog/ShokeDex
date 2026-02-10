"""
Unit tests for database caching functionality
"""

import unittest
import tempfile
import os
from src.data.database import Database
from src.data.database_cache import CachedDatabase


class TestDatabaseCache(unittest.TestCase):
    """Test cases for CachedDatabase class"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database with sample data (once for all tests)"""
        # Create a temporary database
        cls.db_fd, cls.db_path = tempfile.mkstemp(suffix='.db')
        
        # Initialize schema and add test data
        with Database(cls.db_path) as db:
            db.create_schema()
            
            # Add test types
            db.execute("INSERT INTO types (id, name) VALUES (1, 'normal')")
            db.execute("INSERT INTO types (id, name) VALUES (2, 'fire')")
            db.execute("INSERT INTO types (id, name) VALUES (3, 'water')")
            db.execute("INSERT INTO types (id, name) VALUES (13, 'electric')")
            db.commit()
            
            # Add test stats
            for i, name in enumerate(['hp', 'attack', 'defense', 'special-attack', 'special-defense', 'speed'], 1):
                db.execute("INSERT INTO stats (id, name) VALUES (?, ?)", (i, name))
            db.commit()
            
            # Add test Pokémon
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, generation, description)
                VALUES (1, 'bulbasaur', 1, 7, 69, 1, 'A strange seed was planted on its back at birth.')
            """)
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, generation, description)
                VALUES (25, 'pikachu', 25, 4, 60, 1, 'When several of these Pokémon gather.')
            """)
            db.execute("""
                INSERT INTO pokemon (id, name, species_id, height, weight, generation, description)
                VALUES (150, 'mewtwo', 150, 20, 1220, 1, 'It was created by a scientist.')
            """)
            db.commit()
            
            # Add types
            db.execute("INSERT INTO pokemon_types (pokemon_id, type_id, slot) VALUES (25, 13, 1)")
            db.commit()
            
            # Add stats
            db.execute("INSERT INTO pokemon_stats (pokemon_id, stat_id, base_stat) VALUES (25, 1, 35)")
            db.execute("INSERT INTO pokemon_stats (pokemon_id, stat_id, base_stat) VALUES (25, 2, 55)")
            db.commit()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        os.close(cls.db_fd)
        os.unlink(cls.db_path)
    
    def setUp(self):
        """Reset cache stats before each test"""
        CachedDatabase.reset_cache_stats()
    
    def test_get_pokemon_by_id_cached(self):
        """Test get_pokemon_by_id with caching"""
        with CachedDatabase(self.db_path) as db:
            # First access - cache miss
            result1 = db.get_pokemon_by_id(25)
            self.assertIsNotNone(result1)
            self.assertEqual(result1['name'], 'pikachu')
            
            # Second access - cache hit
            result2 = db.get_pokemon_by_id(25)
            self.assertIsNotNone(result2)
            self.assertEqual(result2['name'], 'pikachu')
            
            # Verify results are identical
            self.assertEqual(result1['id'], result2['id'])
            self.assertEqual(result1['name'], result2['name'])
    
    def test_get_pokemon_by_name_cached(self):
        """Test get_pokemon_by_name with caching"""
        with CachedDatabase(self.db_path) as db:
            result1 = db.get_pokemon_by_name('pikachu')
            result2 = db.get_pokemon_by_name('PIKACHU')  # Case insensitive
            result3 = db.get_pokemon_by_name('Pikachu')
            
            self.assertIsNotNone(result1)
            self.assertEqual(result1['name'], 'pikachu')
            
            # All variations should return same data
            self.assertEqual(result1['id'], result2['id'])
            self.assertEqual(result1['id'], result3['id'])
    
    def test_get_pokemon_stats_cached(self):
        """Test get_pokemon_stats with caching"""
        with CachedDatabase(self.db_path) as db:
            stats1 = db.get_pokemon_stats(25)
            stats2 = db.get_pokemon_stats(25)
            
            self.assertEqual(len(stats1), len(stats2))
            self.assertTrue(len(stats1) > 0)
            
            # Verify stat values match
            for s1, s2 in zip(stats1, stats2):
                self.assertEqual(s1['base_stat'], s2['base_stat'])
    
    def test_get_pokemon_types_cached(self):
        """Test get_pokemon_types with caching"""
        with CachedDatabase(self.db_path) as db:
            types1 = db.get_pokemon_types(25)
            types2 = db.get_pokemon_types(25)
            
            self.assertEqual(types1, types2)
            self.assertEqual(types1, ['electric'])
    
    def test_cache_hit_stats(self):
        """Test cache statistics tracking"""
        CachedDatabase.reset_cache_stats()
        
        with CachedDatabase(self.db_path) as db:
            # Multiple accesses to same Pokémon
            for _ in range(5):
                db.get_pokemon_by_id(25)
            
            stats = CachedDatabase.get_cache_stats()
            
            # Should have hits after first access
            self.assertEqual(stats['by_id']['hits'], 5)
            self.assertEqual(stats['total_requests'], 5)
    
    def test_cache_miss_for_nonexistent(self):
        """Test cache behavior for nonexistent Pokémon"""
        with CachedDatabase(self.db_path) as db:
            result = db.get_pokemon_by_id(999)
            self.assertIsNone(result)
            
            # Access again
            result2 = db.get_pokemon_by_id(999)
            self.assertIsNone(result2)
            
            stats = CachedDatabase.get_cache_stats()
            self.assertEqual(stats['by_id']['misses'], 2)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        with CachedDatabase(self.db_path) as db:
            # Populate cache
            db.get_pokemon_by_id(25)
            db.get_pokemon_by_name('pikachu')
            
            # Clear cache
            db.clear_cache()
            
            # Reset stats and access again
            CachedDatabase.reset_cache_stats()
            db.get_pokemon_by_id(25)
            
            # Should work correctly after clear
            stats = CachedDatabase.get_cache_stats()
            self.assertEqual(stats['by_id']['hits'], 1)
    
    def test_different_pokemon_different_cache_entries(self):
        """Test that different Pokémon are cached separately"""
        with CachedDatabase(self.db_path) as db:
            pikachu = db.get_pokemon_by_id(25)
            bulbasaur = db.get_pokemon_by_id(1)
            mewtwo = db.get_pokemon_by_id(150)
            
            self.assertNotEqual(pikachu['id'], bulbasaur['id'])
            self.assertNotEqual(pikachu['id'], mewtwo['id'])
            
            # Access again - should be cached
            pikachu2 = db.get_pokemon_by_id(25)
            self.assertEqual(pikachu['name'], pikachu2['name'])


if __name__ == '__main__':
    unittest.main()

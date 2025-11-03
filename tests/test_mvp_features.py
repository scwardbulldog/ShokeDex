"""
Tests for MVP features
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.database import Database
from src.sync_manager import SyncManager, SyncStatus


class TestSyncManager(unittest.TestCase):
    """Test SyncManager functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sync_manager = SyncManager()
    
    def test_initialization(self):
        """Test SyncManager initializes correctly"""
        self.assertEqual(self.sync_manager.status, SyncStatus.IDLE)
        self.assertFalse(self.sync_manager.sync_enabled)
        self.assertIsNone(self.sync_manager.last_sync_time)
    
    def test_is_online_stub(self):
        """Test is_online returns False (stub)"""
        self.assertFalse(self.sync_manager.is_online())
    
    def test_enable_disable_sync(self):
        """Test enabling and disabling sync"""
        self.sync_manager.enable_sync(True)
        self.assertTrue(self.sync_manager.sync_enabled)
        
        self.sync_manager.enable_sync(False)
        self.assertFalse(self.sync_manager.sync_enabled)
    
    def test_sync_when_disabled(self):
        """Test sync fails when disabled"""
        result = self.sync_manager.start_sync()
        self.assertFalse(result)
        self.assertEqual(self.sync_manager.status, SyncStatus.IDLE)
    
    def test_sync_when_offline(self):
        """Test sync fails when offline"""
        self.sync_manager.enable_sync(True)
        result = self.sync_manager.start_sync()
        self.assertFalse(result)
        self.assertEqual(self.sync_manager.status, SyncStatus.OFFLINE)
    
    def test_get_sync_info(self):
        """Test getting sync information"""
        info = self.sync_manager.get_sync_info()
        
        self.assertIn('enabled', info)
        self.assertIn('status', info)
        self.assertIn('online', info)
        self.assertIn('last_sync', info)
        
        self.assertFalse(info['enabled'])
        self.assertFalse(info['online'])
    
    def test_force_offline_mode(self):
        """Test forcing offline mode"""
        self.sync_manager.enable_sync(True)
        self.sync_manager.force_offline_mode()
        
        self.assertFalse(self.sync_manager.sync_enabled)
        self.assertEqual(self.sync_manager.status, SyncStatus.OFFLINE)


class TestHomeScreenLogic(unittest.TestCase):
    """Test Home Screen filtering and search logic"""
    
    def test_filter_by_search_query(self):
        """Test filtering Pokemon by search query"""
        pokemon_list = [
            {'id': 1, 'name': 'bulbasaur'},
            {'id': 25, 'name': 'pikachu'},
            {'id': 4, 'name': 'charmander'},
        ]
        
        # Filter by name
        query = 'pika'
        result = [p for p in pokemon_list if query in p['name'].lower()]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['id'], 25)
        
        # Filter by ID (as string)
        query = '25'
        result = [p for p in pokemon_list if query in str(p['id'])]
        self.assertEqual(len(result), 1)  # Matches only 25
    
    def test_recent_views_tracking(self):
        """Test recent views list management"""
        recent_views = []
        max_recent = 12
        
        # Add items
        for pokemon_id in [1, 25, 4, 7, 1]:  # Note: 1 appears twice
            if pokemon_id in recent_views:
                recent_views.remove(pokemon_id)
            recent_views.insert(0, pokemon_id)
            recent_views = recent_views[:max_recent]
        
        # Check that 1 is at front (most recent)
        self.assertEqual(recent_views[0], 1)
        
        # Check that we don't have duplicates
        self.assertEqual(len(recent_views), len(set(recent_views)))
        
        # Check order (most recent first)
        self.assertEqual(recent_views, [1, 7, 4, 25])
    
    def test_favorites_tracking(self):
        """Test favorites set management"""
        favorites = set()
        
        # Add favorites
        favorites.add(25)
        favorites.add(1)
        favorites.add(6)
        
        self.assertEqual(len(favorites), 3)
        self.assertIn(25, favorites)
        
        # Remove favorite
        favorites.discard(1)
        self.assertEqual(len(favorites), 2)
        self.assertNotIn(1, favorites)


class TestDetailScreenTabs(unittest.TestCase):
    """Test Detail Screen tab cycling"""
    
    def test_tab_cycling(self):
        """Test cycling through tabs"""
        tabs = ["stats", "evolutions", "abilities"]
        current_tab = "stats"
        
        # Cycle forward
        current_idx = tabs.index(current_tab)
        next_idx = (current_idx + 1) % len(tabs)
        current_tab = tabs[next_idx]
        self.assertEqual(current_tab, "evolutions")
        
        # Cycle forward again
        current_idx = tabs.index(current_tab)
        next_idx = (current_idx + 1) % len(tabs)
        current_tab = tabs[next_idx]
        self.assertEqual(current_tab, "abilities")
        
        # Cycle forward (wraps around)
        current_idx = tabs.index(current_tab)
        next_idx = (current_idx + 1) % len(tabs)
        current_tab = tabs[next_idx]
        self.assertEqual(current_tab, "stats")
        
        # Cycle backward
        current_idx = tabs.index(current_tab)
        prev_idx = (current_idx - 1) % len(tabs)
        current_tab = tabs[prev_idx]
        self.assertEqual(current_tab, "abilities")


class TestPaginationLogic(unittest.TestCase):
    """Test pagination calculations"""
    
    def test_page_calculation(self):
        """Test page number calculations"""
        items_per_page = 12
        total_items = 151
        
        # Calculate total pages
        total_pages = (total_items + items_per_page - 1) // items_per_page
        self.assertEqual(total_pages, 13)
        
        # Test page ranges
        page = 0
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        self.assertEqual(start_idx, 0)
        self.assertEqual(end_idx, 12)
        
        # Last page
        page = 12
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        self.assertEqual(start_idx, 144)
        self.assertEqual(end_idx, 151)
    
    def test_grid_position_calculation(self):
        """Test grid position calculations"""
        grid_cols = 4
        items_per_page = 12
        
        # Test various positions
        for relative_idx in range(items_per_page):
            row = relative_idx // grid_cols
            col = relative_idx % grid_cols
            
            self.assertLess(row, 3)  # Max 3 rows
            self.assertLess(col, 4)  # Max 4 columns
        
        # Test specific positions
        relative_idx = 0
        row = relative_idx // grid_cols
        col = relative_idx % grid_cols
        self.assertEqual(row, 0)
        self.assertEqual(col, 0)
        
        relative_idx = 5
        row = relative_idx // grid_cols
        col = relative_idx % grid_cols
        self.assertEqual(row, 1)
        self.assertEqual(col, 1)


if __name__ == '__main__':
    unittest.main()

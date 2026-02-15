"""
Unit tests for dirty rectangle manager and static caching.
"""

import pygame
import pytest

from src.ui.dirty_rect_manager import DirtyRectManager
from src.ui.static_cache import StaticCache, FontCache, TextCache


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Initialize pygame for tests."""
    pygame.init()
    yield
    pygame.quit()


class TestDirtyRectManager:
    """Tests for DirtyRectManager."""
    
    def test_initialization(self):
        """Test manager initializes correctly."""
        manager = DirtyRectManager()
        assert manager.get_dirty_count() == 0
        assert manager.full_update_needed is True  # First render needs full update
    
    def test_mark_dirty(self):
        """Test marking rectangles as dirty."""
        manager = DirtyRectManager()
        manager.clear()  # Clear initial full update flag
        
        rect = pygame.Rect(10, 10, 100, 50)
        manager.mark_dirty(rect)
        
        assert manager.get_dirty_count() == 1
        assert manager.needs_update() is True
    
    def test_mark_dirty_area(self):
        """Test marking area by coordinates."""
        manager = DirtyRectManager()
        manager.clear()
        
        manager.mark_dirty_area(5, 5, 50, 50)
        
        assert manager.get_dirty_count() == 1
    
    def test_mark_full_update(self):
        """Test marking for full update."""
        manager = DirtyRectManager()
        manager.clear()
        
        manager.mark_full_update()
        
        assert manager.full_update_needed is True
        assert manager.needs_update() is True
    
    def test_clear(self):
        """Test clearing dirty rects."""
        manager = DirtyRectManager()
        manager.mark_dirty(pygame.Rect(0, 0, 10, 10))
        manager.mark_full_update()
        
        manager.clear()
        
        assert manager.get_dirty_count() == 0
        assert manager.full_update_needed is False
        assert manager.needs_update() is False


class TestStaticCache:
    """Tests for StaticCache."""
    
    def test_initialization(self):
        """Test cache initializes correctly."""
        cache = StaticCache()
        assert cache.get_cache_size() == 0
    
    def test_register_and_get(self):
        """Test registering and retrieving cached surfaces."""
        cache = StaticCache()
        
        def render_func():
            surface = pygame.Surface((100, 50))
            surface.fill((255, 0, 0))
            return surface
        
        cache.register("test_surface", render_func)
        
        # First get should render
        surface1 = cache.get("test_surface")
        assert surface1 is not None
        assert surface1.get_width() == 100
        assert surface1.get_height() == 50
        assert cache.get_cache_size() == 1
        
        # Second get should return cached version
        surface2 = cache.get("test_surface")
        assert surface2 is surface1  # Same object
    
    def test_invalidate(self):
        """Test invalidating cached surfaces."""
        cache = StaticCache()
        
        cache.register("test", lambda: pygame.Surface((10, 10)))
        cache.get("test")  # Cache it
        
        assert cache.has("test")
        
        cache.invalidate("test")
        
        assert not cache.has("test")
    
    def test_invalidate_all(self):
        """Test invalidating all cached surfaces."""
        cache = StaticCache()
        
        cache.register("test1", lambda: pygame.Surface((10, 10)))
        cache.register("test2", lambda: pygame.Surface((20, 20)))
        cache.get("test1")
        cache.get("test2")
        
        assert cache.get_cache_size() == 2
        
        cache.invalidate_all()
        
        assert cache.get_cache_size() == 0
    
    def test_memory_usage(self):
        """Test memory usage estimation."""
        cache = StaticCache()
        
        cache.register("test", lambda: pygame.Surface((100, 50)))
        cache.get("test")
        
        # 100 * 50 * 4 bytes = 20000 bytes
        assert cache.get_memory_usage() == 20000


class TestFontCache:
    """Tests for FontCache."""
    
    def test_get_font(self):
        """Test getting cached fonts."""
        font1 = FontCache.get_font(None, 24)
        font2 = FontCache.get_font(None, 24)
        
        # Should return same instance
        assert font1 is font2
        assert FontCache.get_cache_size() >= 1
    
    def test_different_sizes(self):
        """Test caching different font sizes."""
        font24 = FontCache.get_font(None, 24)
        font36 = FontCache.get_font(None, 36)
        
        # Should be different instances
        assert font24 is not font36
    
    def test_clear(self):
        """Test clearing font cache."""
        FontCache.get_font(None, 24)
        initial_size = FontCache.get_cache_size()
        
        FontCache.clear()
        
        assert FontCache.get_cache_size() == 0


class TestTextCache:
    """Tests for TextCache."""
    
    def test_initialization(self):
        """Test text cache initializes correctly."""
        cache = TextCache(max_size=50)
        assert cache.get_cache_size() == 0
        assert cache.max_size == 50
    
    def test_get_text(self):
        """Test getting cached text surfaces."""
        cache = TextCache()
        font = pygame.font.Font(None, 24)
        
        surface1 = cache.get_text("Hello", font, (255, 255, 255))
        surface2 = cache.get_text("Hello", font, (255, 255, 255))
        
        # Should return same cached surface
        assert surface1 is surface2
        assert cache.get_cache_size() == 1
    
    def test_different_text(self):
        """Test caching different text strings."""
        cache = TextCache()
        font = pygame.font.Font(None, 24)
        
        surface1 = cache.get_text("Hello", font, (255, 255, 255))
        surface2 = cache.get_text("World", font, (255, 255, 255))
        
        # Should be different surfaces
        assert surface1 is not surface2
        assert cache.get_cache_size() == 2
    
    def test_cache_eviction(self):
        """Test that cache evicts old entries when max_size is reached."""
        cache = TextCache(max_size=2)
        font = pygame.font.Font(None, 24)
        
        cache.get_text("First", font, (255, 255, 255))
        cache.get_text("Second", font, (255, 255, 255))
        
        assert cache.get_cache_size() == 2
        
        # Adding third should evict first
        cache.get_text("Third", font, (255, 255, 255))
        
        assert cache.get_cache_size() == 2
    
    def test_clear(self):
        """Test clearing text cache."""
        cache = TextCache()
        font = pygame.font.Font(None, 24)
        
        cache.get_text("Test", font, (255, 255, 255))
        
        cache.clear()
        
        assert cache.get_cache_size() == 0

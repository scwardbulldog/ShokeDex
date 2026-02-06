"""
Static Surface Cache for optimized rendering

Caches pre-rendered static UI elements to avoid redundant rendering.
"""

import pygame
from typing import Dict, Optional, Tuple, Callable


class StaticCache:
    """
    Caches static pygame surfaces to avoid redundant rendering.
    
    Common use cases:
    - Background images/gradients
    - UI frames and borders  
    - Static text labels
    - Generation badges
    """
    
    def __init__(self):
        """Initialize static cache."""
        self._cache: Dict[str, pygame.Surface] = {}
        self._render_funcs: Dict[str, Callable] = {}
    
    def register(self, key: str, render_func: Callable[[], pygame.Surface]):
        """
        Register a rendering function for a static element.
        
        Args:
            key: Unique identifier for the cached surface
            render_func: Function that renders and returns the surface
        """
        self._render_funcs[key] = render_func
    
    def get(self, key: str) -> Optional[pygame.Surface]:
        """
        Get a cached surface, rendering it if necessary.
        
        Args:
            key: Identifier for the cached surface
            
        Returns:
            The cached surface, or None if key not registered
        """
        if key in self._cache:
            return self._cache[key]
        
        if key in self._render_funcs:
            surface = self._render_funcs[key]()
            self._cache[key] = surface
            return surface
        
        return None
    
    def invalidate(self, key: str):
        """
        Invalidate a cached surface, forcing re-render on next get().
        
        Args:
            key: Identifier for the surface to invalidate
        """
        if key in self._cache:
            del self._cache[key]
    
    def invalidate_all(self):
        """Invalidate all cached surfaces."""
        self._cache.clear()
    
    def clear(self):
        """Clear all cached surfaces and render functions."""
        self._cache.clear()
        self._render_funcs.clear()
    
    def has(self, key: str) -> bool:
        """
        Check if a surface is cached.
        
        Args:
            key: Identifier to check
            
        Returns:
            True if surface is cached, False otherwise
        """
        return key in self._cache
    
    def get_cache_size(self) -> int:
        """Get number of cached surfaces."""
        return len(self._cache)
    
    def get_memory_usage(self) -> int:
        """
        Estimate memory usage of cached surfaces in bytes.
        
        Returns:
            Approximate bytes used by cached surfaces
        """
        total_bytes = 0
        for surface in self._cache.values():
            # Each pixel is 4 bytes (RGBA)
            total_bytes += surface.get_width() * surface.get_height() * 4
        return total_bytes


class FontCache:
    """
    Caches pygame font instances to avoid repeated creation.
    
    Creating fonts is expensive, so cache them by (path, size).
    """
    
    _fonts: Dict[Tuple[Optional[str], int], pygame.font.Font] = {}
    
    @classmethod
    def get_font(cls, font_path: Optional[str], size: int) -> pygame.font.Font:
        """
        Get a cached font instance.
        
        Args:
            font_path: Path to font file, or None for default font
            size: Font size in pixels
            
        Returns:
            Cached or newly created Font instance
        """
        key = (font_path, size)
        if key not in cls._fonts:
            cls._fonts[key] = pygame.font.Font(font_path, size)
        return cls._fonts[key]
    
    @classmethod
    def clear(cls):
        """Clear all cached fonts."""
        cls._fonts.clear()
    
    @classmethod
    def get_cache_size(cls) -> int:
        """Get number of cached fonts."""
        return len(cls._fonts)


class TextCache:
    """
    Caches pre-rendered text surfaces.
    
    Rendering text is expensive, so cache common strings.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize text cache.
        
        Args:
            max_size: Maximum number of text surfaces to cache
        """
        self._cache: Dict[Tuple[str, pygame.font.Font, Tuple], pygame.Surface] = {}
        self.max_size = max_size
    
    def get_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        antialias: bool = True
    ) -> pygame.Surface:
        """
        Get a cached text surface, rendering if necessary.
        
        Args:
            text: Text string to render
            font: Font instance to use
            color: RGB color tuple
            antialias: Whether to use antialiasing
            
        Returns:
            Rendered text surface
        """
        key = (text, font, color)
        
        if key in self._cache:
            return self._cache[key]
        
        # Render new text
        surface = font.render(text, antialias, color)
        
        # Add to cache, evicting old entries if needed
        if len(self._cache) >= self.max_size:
            # Simple FIFO eviction - remove first item
            first_key = next(iter(self._cache))
            del self._cache[first_key]
        
        self._cache[key] = surface
        return surface
    
    def clear(self):
        """Clear all cached text."""
        self._cache.clear()
    
    def get_cache_size(self) -> int:
        """Get number of cached text surfaces."""
        return len(self._cache)

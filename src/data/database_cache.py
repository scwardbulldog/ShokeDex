"""
Database caching layer for ShokeDex
Implements LRU caching for frequently accessed queries to improve performance
"""

from functools import lru_cache
from typing import Optional, List, Dict, Any, Tuple
from .database import Database


class CachedDatabase(Database):
    """
    Database wrapper with LRU caching for frequently accessed queries.
    
    This class extends the base Database class to add transparent caching
    for read operations that are accessed repeatedly during navigation.
    
    Cache benefits:
    - Reduces disk I/O for repeated queries
    - Improves UI responsiveness during Pokémon navigation
    - Minimal memory overhead (~256 entries per cache)
    
    Target use case: UI navigation where users frequently view the same
    Pokémon multiple times (back/forward navigation, favorites, etc.)
    """
    
    # Class-level cache statistics
    _cache_stats = {
        'hits': 0,
        'misses': 0,
        'by_id_hits': 0,
        'by_id_misses': 0,
        'by_name_hits': 0,
        'by_name_misses': 0,
        'stats_hits': 0,
        'stats_misses': 0,
        'types_hits': 0,
        'types_misses': 0,
    }
    
    def __init__(self, db_path: Optional[str] = None, cache_size: int = 256):
        """
        Initialize cached database.
        
        Args:
            db_path: Path to SQLite database file
            cache_size: Maximum number of entries per cache (default: 256)
                       With Gen 1-3 (386 Pokémon), 256 covers ~66% of data
        """
        super().__init__(db_path)
        self._cache_size = cache_size
        
        # Initialize caches for different query types
        self._get_pokemon_by_id_cache = lru_cache(maxsize=cache_size)(self._get_pokemon_by_id_impl)
        self._get_pokemon_by_name_cache = lru_cache(maxsize=cache_size)(self._get_pokemon_by_name_impl)
        self._get_pokemon_stats_cache = lru_cache(maxsize=cache_size)(self._get_pokemon_stats_impl)
        self._get_pokemon_types_cache = lru_cache(maxsize=cache_size)(self._get_pokemon_types_impl)
    
    def _get_pokemon_by_id_impl(self, pokemon_id: int) -> Optional[Tuple[Any, ...]]:
        """
        Internal implementation for get_pokemon_by_id.
        Returns tuple for hashability (required by lru_cache).
        """
        result = super().get_pokemon_by_id(pokemon_id)
        if result is None:
            return None
        # Convert dict to tuple of items for caching
        return tuple(sorted(result.items()))
    
    def get_pokemon_by_id(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Pokémon by ID with caching.
        
        This method caches results to avoid repeated database queries for
        the same Pokémon (common during UI navigation).
        
        Args:
            pokemon_id: National Dex number (1-386)
            
        Returns:
            Dict with pokemon data including description field, or None if not found
        """
        # Check cache
        cached = self._get_pokemon_by_id_cache(pokemon_id)
        
        if cached is None:
            CachedDatabase._cache_stats['by_id_misses'] += 1
            CachedDatabase._cache_stats['misses'] += 1
            return None
        
        # Cache hit
        CachedDatabase._cache_stats['by_id_hits'] += 1
        CachedDatabase._cache_stats['hits'] += 1
        
        # Convert back from tuple to dict
        return dict(cached)
    
    def _get_pokemon_by_name_impl(self, name: str) -> Optional[Tuple[Any, ...]]:
        """Internal implementation for get_pokemon_by_name."""
        result = super().get_pokemon_by_name(name)
        if result is None:
            return None
        return tuple(sorted(result.items()))
    
    def get_pokemon_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get Pokémon by name with caching.
        
        Args:
            name: Pokémon name (case-insensitive)
            
        Returns:
            Dict with pokemon data or None if not found
        """
        # Normalize to lowercase for cache efficiency
        name_lower = name.lower()
        
        cached = self._get_pokemon_by_name_cache(name_lower)
        
        if cached is None:
            CachedDatabase._cache_stats['by_name_misses'] += 1
            CachedDatabase._cache_stats['misses'] += 1
            return None
        
        CachedDatabase._cache_stats['by_name_hits'] += 1
        CachedDatabase._cache_stats['hits'] += 1
        
        return dict(cached)
    
    def _get_pokemon_stats_impl(self, pokemon_id: int) -> Tuple[Tuple[Any, ...], ...]:
        """Internal implementation for get_pokemon_stats."""
        result = super().get_pokemon_stats(pokemon_id)
        # Convert list of dicts to tuple of tuples
        return tuple(tuple(sorted(stat.items())) for stat in result)
    
    def get_pokemon_stats(self, pokemon_id: int) -> List[Dict[str, Any]]:
        """
        Get Pokémon stats with caching.
        
        Args:
            pokemon_id: National Dex number
            
        Returns:
            List of stat dicts
        """
        cached = self._get_pokemon_stats_cache(pokemon_id)
        
        CachedDatabase._cache_stats['stats_hits'] += 1
        CachedDatabase._cache_stats['hits'] += 1
        
        # Convert back from tuple of tuples to list of dicts
        return [dict(stat) for stat in cached]
    
    def _get_pokemon_types_impl(self, pokemon_id: int) -> Tuple[str, ...]:
        """Internal implementation for get_pokemon_types."""
        result = super().get_pokemon_types(pokemon_id)
        return tuple(result)
    
    def get_pokemon_types(self, pokemon_id: int) -> List[str]:
        """
        Get Pokémon types with caching.
        
        Args:
            pokemon_id: National Dex number
            
        Returns:
            List of type names
        """
        cached = self._get_pokemon_types_cache(pokemon_id)
        
        CachedDatabase._cache_stats['types_hits'] += 1
        CachedDatabase._cache_stats['hits'] += 1
        
        return list(cached)
    
    def clear_cache(self):
        """Clear all query caches. Useful for testing or after data updates."""
        self._get_pokemon_by_id_cache.cache_clear()
        self._get_pokemon_by_name_cache.cache_clear()
        self._get_pokemon_stats_cache.cache_clear()
        self._get_pokemon_types_cache.cache_clear()
    
    @classmethod
    def get_cache_stats(cls) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dict with cache hit/miss counts and hit rate
        """
        total_requests = cls._cache_stats['hits'] + cls._cache_stats['misses']
        hit_rate = (cls._cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            'total_hits': cls._cache_stats['hits'],
            'total_misses': cls._cache_stats['misses'],
            'total_requests': total_requests,
            'hit_rate_percent': hit_rate,
            'by_id': {
                'hits': cls._cache_stats['by_id_hits'],
                'misses': cls._cache_stats['by_id_misses'],
            },
            'by_name': {
                'hits': cls._cache_stats['by_name_hits'],
                'misses': cls._cache_stats['by_name_misses'],
            },
            'stats': {
                'hits': cls._cache_stats['stats_hits'],
                'misses': cls._cache_stats['stats_misses'],
            },
            'types': {
                'hits': cls._cache_stats['types_hits'],
                'misses': cls._cache_stats['types_misses'],
            },
        }
    
    @classmethod
    def reset_cache_stats(cls):
        """Reset cache statistics. Useful for testing."""
        cls._cache_stats = {
            'hits': 0,
            'misses': 0,
            'by_id_hits': 0,
            'by_id_misses': 0,
            'by_name_hits': 0,
            'by_name_misses': 0,
            'stats_hits': 0,
            'stats_misses': 0,
            'types_hits': 0,
            'types_misses': 0,
        }

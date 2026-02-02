"""
Database query caching layer for ShokeDex

Provides LRU caching for frequently accessed read-only database queries.
"""

from functools import lru_cache
from typing import Optional, List, Dict, Any, Tuple
from data.database import Database as BaseDatabase


class CachedDatabase(BaseDatabase):
    """
    Database wrapper with LRU caching for read operations.
    
    Caches results of frequently accessed queries to reduce I/O and improve
    navigation performance, especially on resource-constrained Raspberry Pi.
    
    Cache Strategy:
    - Size: 256 entries per method (sufficient for Gen 1-3 navigation)
    - Eviction: LRU (Least Recently Used)
    - Scope: Read-only queries only (pokemon, stats, types)
    
    Performance Impact:
    - Reduces SQLite I/O operations
    - Lower CPU usage on repeated queries
    - Faster navigation (forward/back pattern benefits most)
    """
    
    def __init__(self, db_path: Optional[str] = None):
        super().__init__(db_path)
        # Track cache statistics
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_queries = 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache hit rate and query counts
        """
        hit_rate = (self._cache_hits / self._total_queries * 100) if self._total_queries > 0 else 0.0
        return {
            'total_queries': self._total_queries,
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_rate_percent': hit_rate,
            'cache_info': {
                'get_pokemon_by_id': self._cached_get_pokemon_by_id.cache_info()._asdict(),
                'get_pokemon_by_name': self._cached_get_pokemon_by_name.cache_info()._asdict(),
                'get_pokemon_stats': self._cached_get_pokemon_stats.cache_info()._asdict(),
                'get_pokemon_types': self._cached_get_pokemon_types.cache_info()._asdict(),
            }
        }
    
    def clear_cache(self):
        """Clear all cached query results"""
        self._cached_get_pokemon_by_id.cache_clear()
        self._cached_get_pokemon_by_name.cache_clear()
        self._cached_get_pokemon_stats.cache_clear()
        self._cached_get_pokemon_types.cache_clear()
        self._cache_hits = 0
        self._cache_misses = 0
        self._total_queries = 0
    
    @lru_cache(maxsize=256)
    def _cached_get_pokemon_by_id(self, pokemon_id: int) -> Optional[Tuple]:
        """
        Internal cached wrapper for get_pokemon_by_id.
        Returns tuple instead of dict for hashability (required by lru_cache).
        """
        result = super().get_pokemon_by_id(pokemon_id)
        if result is None:
            return None
        # Convert dict to tuple of (key, value) pairs for caching
        return tuple(sorted(result.items()))
    
    def get_pokemon_by_id(self, pokemon_id: int) -> Optional[Dict[str, Any]]:
        """
        Get Pokémon by ID with LRU caching.
        
        Args:
            pokemon_id: National Dex number (1-386)
            
        Returns:
            Dict with pokemon data, or None if not found
        """
        self._total_queries += 1
        cache_info_before = self._cached_get_pokemon_by_id.cache_info()
        
        result = self._cached_get_pokemon_by_id(pokemon_id)
        
        cache_info_after = self._cached_get_pokemon_by_id.cache_info()
        if cache_info_after.hits > cache_info_before.hits:
            self._cache_hits += 1
        else:
            self._cache_misses += 1
        
        if result is None:
            return None
        # Convert tuple back to dict
        return dict(result)
    
    @lru_cache(maxsize=256)
    def _cached_get_pokemon_by_name(self, name: str) -> Optional[Tuple]:
        """Internal cached wrapper for get_pokemon_by_name"""
        result = super().get_pokemon_by_name(name.lower())  # Normalize case
        if result is None:
            return None
        return tuple(sorted(result.items()))
    
    def get_pokemon_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get Pokémon by name with LRU caching.
        
        Args:
            name: Pokemon name (case-insensitive)
            
        Returns:
            Dict with pokemon data, or None if not found
        """
        self._total_queries += 1
        cache_info_before = self._cached_get_pokemon_by_name.cache_info()
        
        result = self._cached_get_pokemon_by_name(name.lower())
        
        cache_info_after = self._cached_get_pokemon_by_name.cache_info()
        if cache_info_after.hits > cache_info_before.hits:
            self._cache_hits += 1
        else:
            self._cache_misses += 1
        
        if result is None:
            return None
        return dict(result)
    
    @lru_cache(maxsize=256)
    def _cached_get_pokemon_stats(self, pokemon_id: int) -> Tuple:
        """Internal cached wrapper for get_pokemon_stats"""
        result = super().get_pokemon_stats(pokemon_id)
        # Convert list of dicts to tuple of tuples for caching
        return tuple(tuple(sorted(stat.items())) for stat in result)
    
    def get_pokemon_stats(self, pokemon_id: int) -> List[Dict[str, Any]]:
        """
        Get stats for a Pokémon with LRU caching.
        
        Args:
            pokemon_id: National Dex number (1-386)
            
        Returns:
            List of stat dictionaries
        """
        self._total_queries += 1
        cache_info_before = self._cached_get_pokemon_stats.cache_info()
        
        result = self._cached_get_pokemon_stats(pokemon_id)
        
        cache_info_after = self._cached_get_pokemon_stats.cache_info()
        if cache_info_after.hits > cache_info_before.hits:
            self._cache_hits += 1
        else:
            self._cache_misses += 1
        
        # Convert tuple of tuples back to list of dicts
        return [dict(stat) for stat in result]
    
    @lru_cache(maxsize=256)
    def _cached_get_pokemon_types(self, pokemon_id: int) -> Tuple[str, ...]:
        """Internal cached wrapper for get_pokemon_types"""
        result = super().get_pokemon_types(pokemon_id)
        # Convert list to tuple for caching
        return tuple(result)
    
    def get_pokemon_types(self, pokemon_id: int) -> List[str]:
        """
        Get Pokemon types with LRU caching.
        
        Args:
            pokemon_id: National Dex number (1-386)
            
        Returns:
            List of 1-2 type names in order
        """
        self._total_queries += 1
        cache_info_before = self._cached_get_pokemon_types.cache_info()
        
        result = self._cached_get_pokemon_types(pokemon_id)
        
        cache_info_after = self._cached_get_pokemon_types.cache_info()
        if cache_info_after.hits > cache_info_before.hits:
            self._cache_hits += 1
        else:
            self._cache_misses += 1
        
        # Convert tuple back to list
        return list(result)


# Re-export Database as CachedDatabase for transparent caching
Database = CachedDatabase

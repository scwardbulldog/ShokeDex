from pathlib import Path
from typing import Optional, Dict
from collections import OrderedDict


# LRU Cache with max 50 sprites (per Architecture)
# Using OrderedDict for efficient move_to_end() and popitem() operations
_CACHE: OrderedDict[str, object] = OrderedDict()
_CACHE_MAX_SIZE = 50

# Cache statistics for performance monitoring
_cache_hits = 0
_cache_misses = 0


def _get_assets_base() -> Path:
    """Return the absolute path to the `assets/sprites` directory.

    This computes the project root relative to this file so the loader works
    when run from different working directories.
    """
    # Path resolution notes:
    # src/ui/sprite_loader.py ->
    # parents[0] = src/ui
    # parents[1] = src
    # parents[2] = <repo root>
    # Use parents[2] as the repo root. If that doesn't contain assets, fall back
    # to a few sensible alternatives (current working dir, one level up).
    resolved = Path(__file__).resolve()
    repo_root_candidate = resolved.parents[2]
    candidate = repo_root_candidate / "assets" / "sprites"

    if candidate.exists():
        return candidate

    # Fallback: maybe running from repo root already (cwd)
    cwd_candidate = Path.cwd() / "assets" / "sprites"
    if cwd_candidate.exists():
        return cwd_candidate

    # Last resort: try one level up from repo root (older layout possibility)
    try:
        alt = resolved.parents[3] / "assets" / "sprites"
        if alt.exists():
            return alt
    except Exception:
        pass

    # Return the primary candidate even if it doesn't exist; callers will check .exists()
    return candidate


def _load_surface_with_pygame(path: Path):
    """Lazy import pygame and load an image surface. Returns None on failure."""
    try:
        import pygame
    except Exception:
        return None

    try:
        surf = pygame.image.load(str(path))
        # ensure alpha is preserved when available
        try:
            return surf.convert_alpha()
        except Exception:
            return surf.convert()
    except Exception:
        return None


def _evict_lru_if_needed():
    """Evict least recently used sprite if cache exceeds max size."""
    global _CACHE
    while len(_CACHE) > _CACHE_MAX_SIZE:
        # OrderedDict.popitem(last=False) removes the first (oldest) item
        evicted_key, _ = _CACHE.popitem(last=False)
        # Optional: print(f"LRU eviction: {evicted_key}")


def get_cache_stats() -> dict:
    """Get cache performance statistics.
    
    Returns:
        Dictionary with keys: size, max_size, hits, misses, hit_rate
    """
    global _cache_hits, _cache_misses
    total_requests = _cache_hits + _cache_misses
    hit_rate = (_cache_hits / total_requests * 100) if total_requests > 0 else 0.0
    
    return {
        "size": len(_CACHE),
        "max_size": _CACHE_MAX_SIZE,
        "hits": _cache_hits,
        "misses": _cache_misses,
        "hit_rate": hit_rate
    }


def reset_cache_stats():
    """Reset cache statistics (useful for testing)."""
    global _cache_hits, _cache_misses
    _cache_hits = 0
    _cache_misses = 0


def load_thumb(pokemon_id: int) -> Optional[object]:
    """Load and return the thumbnail Surface for a Pokémon (32x32).

    Returns None if the file doesn't exist or pygame isn't available.
    The return type is intentionally generic to avoid importing pygame at module import time.
    
    Uses LRU caching with max 50 sprites to prevent unbounded memory growth.
    """
    global _cache_hits, _cache_misses
    
    key = f"thumb:{pokemon_id:03d}"
    if key in _CACHE:
        _cache_hits += 1
        # Move to end (most recently used)
        _CACHE.move_to_end(key)
        return _CACHE[key]

    _cache_misses += 1
    path = _get_assets_base() / "thumb" / f"{pokemon_id:03d}.png"
    if not path.exists():
        _CACHE[key] = None
        _evict_lru_if_needed()
        return None

    surf = _load_surface_with_pygame(path)
    _CACHE[key] = surf
    _evict_lru_if_needed()
    return surf


def load_detail(pokemon_id: int) -> Optional[object]:
    """Load and return the detail Surface for a Pokémon (96x96).

    Returns None if the file doesn't exist or pygame isn't available.
    
    Uses LRU caching with max 50 sprites to prevent unbounded memory growth.
    """
    global _cache_hits, _cache_misses
    
    key = f"detail:{pokemon_id:03d}"
    if key in _CACHE:
        _cache_hits += 1
        # Move to end (most recently used)
        _CACHE.move_to_end(key)
        return _CACHE[key]

    _cache_misses += 1
    path = _get_assets_base() / "detail" / f"{pokemon_id:03d}.png"
    if not path.exists():
        _CACHE[key] = None
        _evict_lru_if_needed()
        return None

    surf = _load_surface_with_pygame(path)
    _CACHE[key] = surf
    _evict_lru_if_needed()
    return surf

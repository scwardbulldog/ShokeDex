from pathlib import Path
from typing import Optional, Dict


_CACHE: Dict[str, object] = {}


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


def load_thumb(pokemon_id: int) -> Optional[object]:
    """Load and return the thumbnail Surface for a Pokémon (32x32).

    Returns None if the file doesn't exist or pygame isn't available.
    The return type is intentionally generic to avoid importing pygame at module import time.
    """
    key = f"thumb:{pokemon_id:03d}"
    if key in _CACHE:
        return _CACHE[key]

    path = _get_assets_base() / "thumb" / f"{pokemon_id:03d}.png"
    if not path.exists():
        _CACHE[key] = None
        return None

    surf = _load_surface_with_pygame(path)
    _CACHE[key] = surf
    return surf


def load_detail(pokemon_id: int) -> Optional[object]:
    """Load and return the detail Surface for a Pokémon (96x96).

    Returns None if the file doesn't exist or pygame isn't available.
    """
    key = f"detail:{pokemon_id:03d}"
    if key in _CACHE:
        return _CACHE[key]

    path = _get_assets_base() / "detail" / f"{pokemon_id:03d}.png"
    if not path.exists():
        _CACHE[key] = None
        return None

    surf = _load_surface_with_pygame(path)
    _CACHE[key] = surf
    return surf

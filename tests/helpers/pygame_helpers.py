"""
Pygame test helper utilities

Provides utilities for testing pygame-based rendering and UI components.
These helpers extract data from surfaces but do NOT contain assertions.
"""

import pygame
from typing import Optional, Tuple


def surface_to_pixels(surface: pygame.Surface) -> list:
    """
    Convert pygame surface to 2D pixel array for testing.
    
    Args:
        surface: Pygame surface to convert
    
    Returns:
        2D list of RGB tuples representing pixel colors
    
    Usage:
        pixels = surface_to_pixels(surface)
        # Check specific pixel color
        assert pixels[10][20] == (255, 0, 0)  # Red pixel at (20, 10)
    """
    width, height = surface.get_size()
    pixels = []
    
    for y in range(height):
        row = []
        for x in range(width):
            color = surface.get_at((x, y))[:3]  # RGB only (no alpha)
            row.append(color)
        pixels.append(row)
    
    return pixels


def count_non_background_pixels(
    surface: pygame.Surface,
    background_color: Tuple[int, int, int] = (0, 0, 0)
) -> int:
    """
    Count pixels that are NOT the background color.
    
    Useful for validating that something was actually rendered.
    
    Args:
        surface: Surface to analyze
        background_color: RGB tuple for background (default: black)
    
    Returns:
        Number of non-background pixels
    
    Usage:
        # Render something
        screen.render(surface)
        
        # Verify rendering happened
        non_bg_pixels = count_non_background_pixels(surface)
        assert non_bg_pixels > 0, "Nothing was rendered"
    """
    width, height = surface.get_size()
    count = 0
    
    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))[:3]
            if color != background_color:
                count += 1
    
    return count


def get_dominant_color(surface: pygame.Surface) -> Tuple[int, int, int]:
    """
    Get the most common color in a surface.
    
    Useful for validating background colors or themes.
    
    Args:
        surface: Surface to analyze
    
    Returns:
        RGB tuple of the most common color
    
    Usage:
        dominant = get_dominant_color(surface)
        assert dominant == (255, 255, 255), "Background should be white"
    """
    color_counts = {}
    width, height = surface.get_size()
    
    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))[:3]
            color_counts[color] = color_counts.get(color, 0) + 1
    
    # Return color with highest count
    return max(color_counts.items(), key=lambda x: x[1])[0]


def find_color_region(
    surface: pygame.Surface,
    target_color: Tuple[int, int, int],
    tolerance: int = 0
) -> Optional[pygame.Rect]:
    """
    Find the bounding rectangle of pixels matching a target color.
    
    Useful for locating rendered sprites or UI elements.
    
    Args:
        surface: Surface to search
        target_color: RGB color to find
        tolerance: Color matching tolerance (0-255)
    
    Returns:
        pygame.Rect bounding the colored region, or None if not found
    
    Usage:
        # Find red region (with tolerance for anti-aliasing)
        red_region = find_color_region(surface, (255, 0, 0), tolerance=10)
        assert red_region is not None, "Red sprite not found"
        assert red_region.width > 50, "Red region too small"
    """
    width, height = surface.get_size()
    min_x, min_y = width, height
    max_x, max_y = 0, 0
    found = False
    
    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))[:3]
            
            # Check if color matches within tolerance
            if all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color, target_color)):
                found = True
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    if not found:
        return None
    
    return pygame.Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def save_surface_for_debug(surface: pygame.Surface, filename: str):
    """
    Save surface to file for debugging test failures.
    
    Useful when tests fail and you need to see what was actually rendered.
    
    Args:
        surface: Surface to save
        filename: Output filename (will be saved in test-results/)
    
    Usage:
        # In a test that's failing
        try:
            # ... test assertions
            pass
        except AssertionError:
            save_surface_for_debug(surface, "failed_render.png")
            raise
    """
    import os
    
    # Create test-results directory if it doesn't exist
    os.makedirs("test-results", exist_ok=True)
    
    output_path = os.path.join("test-results", filename)
    pygame.image.save(surface, output_path)
    print(f"Debug surface saved to: {output_path}")


def compare_surfaces(
    surface1: pygame.Surface,
    surface2: pygame.Surface,
    tolerance: int = 0
) -> Tuple[bool, int]:
    """
    Compare two surfaces for visual regression testing.
    
    Args:
        surface1: First surface
        surface2: Second surface
        tolerance: Per-channel color difference tolerance (0-255)
    
    Returns:
        Tuple of (are_equal, num_different_pixels)
    
    Usage:
        # Render screen twice, should be identical
        screen.render(surface1)
        screen.render(surface2)
        
        are_equal, diff_count = compare_surfaces(surface1, surface2)
        assert are_equal, f"{diff_count} pixels differ"
    """
    if surface1.get_size() != surface2.get_size():
        return False, -1
    
    width, height = surface1.get_size()
    diff_count = 0
    
    for y in range(height):
        for x in range(width):
            color1 = surface1.get_at((x, y))[:3]
            color2 = surface2.get_at((x, y))[:3]
            
            if not all(abs(c1 - c2) <= tolerance for c1, c2 in zip(color1, color2)):
                diff_count += 1
    
    are_equal = diff_count == 0
    return are_equal, diff_count

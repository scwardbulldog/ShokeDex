"""
Dirty Rectangle Manager for optimized rendering

Tracks changed screen regions to minimize display updates.
"""

import pygame
from typing import List, Optional


class DirtyRectManager:
    """
    Manages dirty rectangles for optimized pygame rendering.
    
    Instead of updating the entire display with pygame.display.flip(),
    this tracks only changed regions and updates them with pygame.display.update().
    """
    
    def __init__(self):
        """Initialize dirty rect manager."""
        self.dirty_rects: List[pygame.Rect] = []
        self.full_update_needed = True
    
    def mark_dirty(self, rect: pygame.Rect):
        """
        Mark a region as dirty (needs redraw).
        
        Args:
            rect: Rectangle region that changed
        """
        if rect and rect.width > 0 and rect.height > 0:
            self.dirty_rects.append(rect)
    
    def mark_dirty_area(self, x: int, y: int, width: int, height: int):
        """
        Mark a rectangular area as dirty.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Width of region
            height: Height of region
        """
        self.mark_dirty(pygame.Rect(x, y, width, height))
    
    def mark_full_update(self):
        """Mark that a full screen update is needed."""
        self.full_update_needed = True
    
    def update_display(self) -> int:
        """
        Update the display with accumulated dirty rects.
        
        Returns:
            Number of rectangles updated (0 if full flip was used)
        """
        if self.full_update_needed:
            pygame.display.flip()
            self.clear()
            return 0
        
        if not self.dirty_rects:
            return 0
        
        # Update only dirty regions
        pygame.display.update(self.dirty_rects)
        count = len(self.dirty_rects)
        self.clear()
        return count
    
    def clear(self):
        """Clear dirty rects and reset flags."""
        self.dirty_rects.clear()
        self.full_update_needed = False
    
    def get_dirty_count(self) -> int:
        """Get number of dirty rectangles."""
        return len(self.dirty_rects)
    
    def needs_update(self) -> bool:
        """Check if any update is needed."""
        return self.full_update_needed or len(self.dirty_rects) > 0

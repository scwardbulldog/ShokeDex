"""
Base Screen class for ShokeDex UI
"""

import pygame
from typing import Optional, List
from abc import ABC, abstractmethod


class Screen(ABC):
    """
    Abstract base class for all screens in the application.
    
    Each screen represents a different view (home, list, detail, settings).
    """
    
    def __init__(self, screen_manager):
        """
        Initialize screen.
        
        Args:
            screen_manager: The ScreenManager instance managing this screen
        """
        self.screen_manager = screen_manager
        self.surface: Optional[pygame.Surface] = None
        self._active = False
        self._needs_full_render = True  # Flag for initial render or major changes
    
    @abstractmethod
    def handle_input(self, action):
        """
        Handle input action.
        
        Args:
            action: InputAction enum value
        """
        pass
    
    @abstractmethod
    def update(self, delta_time: float):
        """
        Update screen state.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        pass
    
    @abstractmethod
    def render(self, surface: pygame.Surface) -> List[pygame.Rect]:
        """
        Render the screen.
        
        Args:
            surface: Pygame surface to render on
            
        Returns:
            List of dirty rectangles that were updated
        """
        pass
    
    def needs_full_render(self) -> bool:
        """Check if screen needs a full redraw."""
        return self._needs_full_render
    
    def mark_full_render(self):
        """Mark that screen needs a full redraw."""
        self._needs_full_render = True
    
    def clear_full_render(self):
        """Clear full render flag after rendering."""
        self._needs_full_render = False
    
    def on_enter(self):
        """Called when screen becomes active."""
        self._active = True
        self._needs_full_render = True  # Full render when entering screen
    
    def on_exit(self):
        """Called when screen becomes inactive."""
        self._active = False
    
    def is_active(self) -> bool:
        """Check if screen is currently active."""
        return self._active

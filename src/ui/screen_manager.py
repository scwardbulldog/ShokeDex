"""
Screen Manager for ShokeDex - Handles screen stack and transitions
"""

import pygame
from typing import List, Optional, Dict, Type
from .screen import Screen
from .dirty_rect_manager import DirtyRectManager


class ScreenManager:
    """
    Manages screen stack and transitions.
    
    Screens are managed as a stack:
    - Push a screen to navigate to it
    - Pop to go back to previous screen
    - Replace to switch screens without adding to history
    """
    
    def __init__(self, display_surface: pygame.Surface):
        """
        Initialize ScreenManager.
        
        Args:
            display_surface: Main display surface to render to
        """
        self.display_surface = display_surface
        self.screen_stack: List[Screen] = []
        self.screen_registry: Dict[str, Type[Screen]] = {}
        self.dirty_rect_manager = DirtyRectManager()
    
    def register_screen(self, name: str, screen_class: Type[Screen]):
        """
        Register a screen class with a name.
        
        Args:
            name: Identifier for the screen
            screen_class: Screen class (not instance)
        """
        self.screen_registry[name] = screen_class
    
    def push(self, screen: Screen):
        """
        Push a new screen onto the stack.
        
        Args:
            screen: Screen instance to push
        """
        # Deactivate current screen if any
        if self.screen_stack:
            self.screen_stack[-1].on_exit()
        
        # Add and activate new screen
        self.screen_stack.append(screen)
        screen.on_enter()
    
    def pop(self) -> Optional[Screen]:
        """
        Pop the current screen from the stack.
        
        Returns:
            The popped screen, or None if stack is empty
        """
        if not self.screen_stack:
            return None
        
        # Remove current screen
        screen = self.screen_stack.pop()
        screen.on_exit()
        
        # Activate previous screen if any
        if self.screen_stack:
            self.screen_stack[-1].on_enter()
        
        return screen
    
    def replace(self, screen: Screen):
        """
        Replace the current screen without affecting stack history.
        
        Args:
            screen: Screen instance to show
        """
        if self.screen_stack:
            old_screen = self.screen_stack.pop()
            old_screen.on_exit()
        
        self.screen_stack.append(screen)
        screen.on_enter()
    
    def clear(self):
        """Clear all screens from the stack."""
        while self.screen_stack:
            screen = self.screen_stack.pop()
            screen.on_exit()
    
    def get_current(self) -> Optional[Screen]:
        """
        Get the currently active screen.
        
        Returns:
            Current screen or None if stack is empty
        """
        return self.screen_stack[-1] if self.screen_stack else None
    
    def handle_input(self, action):
        """
        Pass input to the current screen.
        
        Args:
            action: InputAction to handle
        """
        current = self.get_current()
        if current:
            current.handle_input(action)
    
    def handle_input_release(self, action):
        """
        Pass input release event to the current screen.
        
        Args:
            action: InputAction that was released
        """
        current = self.get_current()
        if current and hasattr(current, 'handle_input_release'):
            current.handle_input_release(action)
    
    def update(self, delta_time: float):
        """
        Update the current screen.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        current = self.get_current()
        if current:
            current.update(delta_time)
    
    def render(self) -> List[pygame.Rect]:
        """
        Render the current screen to the display surface.
        
        Returns:
            List of dirty rectangles that were updated
        """
        current = self.get_current()
        if current:
            # Get dirty rects from screen rendering
            dirty_rects = current.render(self.display_surface)
            
            # Add to dirty rect manager
            if current.needs_full_render():
                self.dirty_rect_manager.mark_full_update()
                current.clear_full_render()
            else:
                for rect in dirty_rects:
                    self.dirty_rect_manager.mark_dirty(rect)
            
            return dirty_rects
        return []
    
    def update_display(self) -> int:
        """
        Update the display using dirty rect optimization.
        
        Returns:
            Number of dirty rectangles updated (0 if full flip was used)
        """
        return self.dirty_rect_manager.update_display()
    
    def has_screens(self) -> bool:
        """Check if there are any screens in the stack."""
        return len(self.screen_stack) > 0
    
    def get_stack_depth(self) -> int:
        """Get the number of screens in the stack."""
        return len(self.screen_stack)

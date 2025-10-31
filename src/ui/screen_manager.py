"""
Screen Manager for ShokeDex - Handles screen stack and transitions
"""

import pygame
from typing import List, Optional, Dict, Type
from .screen import Screen


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
    
    def update(self, delta_time: float):
        """
        Update the current screen.
        
        Args:
            delta_time: Time elapsed since last update in seconds
        """
        current = self.get_current()
        if current:
            current.update(delta_time)
    
    def render(self):
        """Render the current screen to the display surface."""
        current = self.get_current()
        if current:
            current.render(self.display_surface)
    
    def has_screens(self) -> bool:
        """Check if there are any screens in the stack."""
        return len(self.screen_stack) > 0
    
    def get_stack_depth(self) -> int:
        """Get the number of screens in the stack."""
        return len(self.screen_stack)

"""
Stub Screen for ShokeDex - Placeholder for future features
"""

import pygame
from typing import Optional
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction


class StubScreen(Screen):
    """
    Stub screen for features that are not yet implemented.
    
    Displays a placeholder message and allows navigation back.
    """
    
    def __init__(self, screen_manager, feature_name: str, description: str = ""):
        """
        Initialize StubScreen.
        
        Args:
            screen_manager: ScreenManager instance
            feature_name: Name of the feature
            description: Description of the feature (optional)
        """
        super().__init__(screen_manager)
        self.feature_name = feature_name
        self.description = description
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.heading_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
    
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 36)
        self.heading_font = pygame.font.Font(None, 28)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        if action == InputAction.BACK or action == InputAction.SELECT:
            self.screen_manager.pop()
    
    def update(self, delta_time: float):
        """Update screen state."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        # Clear background
        surface.fill(Colors.BACKGROUND)
        
        # Draw feature name
        title_text = self.title_font.render(self.feature_name, True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(240, 60))
        surface.blit(title_text, title_rect)
        
        # Draw "Coming Soon" message
        coming_soon = self.heading_font.render("Coming Soon", True, Colors.YELLOW)
        coming_soon_rect = coming_soon.get_rect(center=(240, 120))
        surface.blit(coming_soon, coming_soon_rect)
        
        # Draw description if provided
        if self.description:
            # Word wrap the description
            words = self.description.split()
            lines = []
            current_line = []
            max_width = 420
            
            for word in words:
                current_line.append(word)
                test_line = ' '.join(current_line)
                test_surface = self.text_font.render(test_line, True, Colors.TEXT_PRIMARY)
                if test_surface.get_width() > max_width:
                    current_line.pop()
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Draw lines
            y = 160
            for line in lines[:5]:  # Max 5 lines
                line_text = self.text_font.render(line, True, Colors.TEXT_SECONDARY)
                line_rect = line_text.get_rect(center=(240, y))
                surface.blit(line_text, line_rect)
                y += 25
        
        # Draw placeholder icon/graphic
        icon_size = 64
        icon_rect = pygame.Rect(240 - icon_size // 2, 220, icon_size, icon_size)
        pygame.draw.rect(surface, Colors.BORDER, icon_rect, 2)
        
        # Draw "?" in the icon
        question_text = self.title_font.render("?", True, Colors.BORDER)
        question_rect = question_text.get_rect(center=icon_rect.center)
        surface.blit(question_text, question_rect)
        
        # Draw help text
        help_text = self.small_font.render(
            "This feature is under development",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(center=(240, 295))
        surface.blit(help_text, help_rect)
        
        # Draw back instruction
        back_text = self.small_font.render(
            "Press BACK or SELECT to return",
            True,
            Colors.TEXT_SECONDARY
        )
        back_rect = back_text.get_rect(center=(240, 313))
        surface.blit(back_text, back_rect)
        
        # Return empty list = full screen update
        return []

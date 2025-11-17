"""
Detail Screen for ShokeDex - Detailed Pokémon view

Story 3.1: Basic layout with large sprite, header, and placeholder panels.
Full stat rendering, type badges, and other features come in later stories.
"""

import pygame
import logging
from typing import Optional, Dict
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction
from .sprite_loader import load_detail


class DetailScreen(Screen):
    """
    Detail screen showing comprehensive information about a single Pokémon.
    
    Story 3.1 Implementation:
    - Large sprite display (128x128, center-left positioning)
    - Header with Pokémon name and National Dex number
    - Holographic blue styling (panels, borders, text colors)
    - Placeholder panels for future features (stats, types, measurements, description)
    - B button navigation back to HomeScreen
    - StateManager integration for last viewed persistence
    """
    
    def __init__(self, screen_manager, pokemon_id: int):
        """
        Initialize DetailScreen for a specific Pokémon.
        
        Args:
            screen_manager: ScreenManager instance providing manager access
            pokemon_id: National Dex number to display (1-386)
        """
        super().__init__(screen_manager)
        self.pokemon_id = pokemon_id
        
        # Manager references (via screen_manager injection pattern)
        self.database = screen_manager.database if hasattr(screen_manager, 'database') else None
        self.state_manager = screen_manager.state_manager if hasattr(screen_manager, 'state_manager') else None
        self.sprite_loader = screen_manager.sprite_loader if hasattr(screen_manager, 'sprite_loader') else None
        
        # Pokémon data
        self.pokemon_data: Optional[Dict] = None
        self.sprite: Optional[pygame.Surface] = None
        
        # Fonts
        self.header_font: Optional[pygame.font.Font] = None
        self.body_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
    
    def on_enter(self):
        """
        Called when screen becomes active - load data, initialize resources.
        
        Lifecycle hook from Screen base class. Loads Pokémon data, sprite,
        and updates StateManager with last viewed Pokémon.
        """
        super().on_enter()
        
        # Initialize fonts (Orbitron Bold 24px for headers per UX spec, fallback to system)
        try:
            # Try to load custom fonts if available
            self.header_font = pygame.font.Font(None, 24)  # Orbitron Bold equivalent
        except Exception:
            self.header_font = pygame.font.Font(None, 24)
        
        self.body_font = pygame.font.Font(None, 16)  # Rajdhani equivalent for body
        self.small_font = pygame.font.Font(None, 14)
        
        # Load Pokémon data from database
        self._load_pokemon_data()
        
        # Load detail sprite (128x128 variant)
        if self.pokemon_data:
            try:
                self.sprite = load_detail(self.pokemon_id)
                if self.sprite is None:
                    logging.warning(f"Missing sprite for Pokemon #{self.pokemon_id}")
                    # Create text placeholder
                    self.sprite = self._create_text_placeholder(self.pokemon_data['name'])
            except Exception as e:
                logging.error(f"Error loading sprite for Pokemon #{self.pokemon_id}: {e}")
                self.sprite = self._create_text_placeholder(self.pokemon_data.get('name', f'Pokemon #{self.pokemon_id}'))
        
        # Update StateManager with last viewed Pokémon
        if self.state_manager:
            try:
                self.state_manager.set_last_viewed(self.pokemon_id)
            except Exception as e:
                logging.warning(f"Failed to update last viewed: {e}")
    
    def on_exit(self):
        """
        Called when screen becomes inactive - save state.
        
        Lifecycle hook from Screen base class. Persists last viewed Pokémon
        to state file via StateManager.
        """
        if self.state_manager:
            try:
                self.state_manager.save_state()
            except Exception as e:
                logging.warning(f"Failed to save state on exit: {e}")
        super().on_exit()
    
    def _load_pokemon_data(self):
        """
        Load Pokémon data from database.
        
        Queries database for basic Pokémon information needed for DetailScreen.
        Handles errors gracefully with fallback data.
        
        AC #7: Database query must complete in < 50ms
        AC #8: Handle database errors gracefully
        """
        if not self.database:
            logging.error("No database available for DetailScreen")
            self._show_error_screen("Database not available")
            return
        
        try:
            with self.database as db:
                # Get basic Pokémon info (AC #3: name and ID for header)
                self.pokemon_data = db.get_pokemon_by_id(self.pokemon_id)
                
                if not self.pokemon_data:
                    logging.error(f"Pokemon #{self.pokemon_id} not found in database")
                    self._show_error_screen("Could not load Pokémon data")
                    return
                
        except Exception as e:
            logging.error(f"Database error loading Pokemon #{self.pokemon_id}: {e}")
            self._show_error_screen("Could not load Pokémon data")
    
    def _create_text_placeholder(self, name: str) -> pygame.Surface:
        """
        Create text-based placeholder for missing sprites.
        
        Args:
            name: Pokémon name to display
            
        Returns:
            pygame.Surface with Pokémon name text on gray background
            
        AC #8: Missing sprites show text placeholder gracefully
        """
        surface = pygame.Surface((128, 128))
        surface.fill((64, 64, 64))  # Gray background
        
        try:
            font = pygame.font.Font(None, 36)
            text = font.render(name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(64, 64))
            surface.blit(text, text_rect)
        except Exception:
            pass  # Silent failure, return gray surface
        
        return surface
    
    def _show_error_screen(self, message: str):
        """
        Display error message when data loading fails.
        
        Args:
            message: User-friendly error message
            
        AC #8: Database errors show friendly message, allow B button exit
        """
        self.pokemon_data = None
        self.sprite = None
        logging.error(f"DetailScreen error: {message}")
    
    def handle_input(self, action: InputAction):
        """
        Handle button press actions.
        
        Args:
            action: InputAction enum value (BACK, LEFT, RIGHT, etc.)
            
        AC #1: B button returns to HomeScreen (pop navigation stack)
        """
        if action == InputAction.BACK:
            # Pop screen stack to return to HomeScreen
            self.screen_manager.pop()
    
    def update(self, delta_time: float):
        """
        Update screen state logic each frame.
        
        Args:
            delta_time: Time elapsed since last frame (seconds)
            
        Story 3.1: Minimal implementation - no animations or timers needed
        """
        pass  # No dynamic updates needed for basic layout
    
    def render(self, surface: pygame.Surface):
        """
        Draw screen content to pygame surface.
        
        Args:
            surface: pygame.Surface to render to
            
        AC #2: Large sprite display centered in left area
        AC #3: Header with name (title case) and dex number (#025 format)
        AC #4: Layout with header, sprite, placeholder panels
        AC #5: Holographic blue styling (dark blue panels, electric blue borders)
        AC #7: Render must complete in < 33ms for 30+ FPS
        """
        # Handle error state
        if not self.pokemon_data:
            surface.fill(Colors.DEEP_SPACE_BLACK)
            if self.body_font:
                error_text = self.body_font.render(
                    "Could not load Pokémon data",
                    True,
                    Colors.ICE_BLUE
                )
                error_rect = error_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
                surface.blit(error_text, error_rect)
                
                help_text = self.small_font.render(
                    "Press B to return",
                    True,
                    Colors.ICE_BLUE
                )
                help_rect = help_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 30))
                surface.blit(help_text, help_rect)
            return
        
        # Fill background with deep space black
        surface.fill(Colors.DEEP_SPACE_BLACK)
        
        # AC #3: Render header with name and dex number
        self._render_header(surface)
        
        # AC #2: Render large sprite (center-left positioning)
        self._render_sprite(surface)
        
        # AC #4: Render placeholder panels for future features
        self._render_placeholder_panels(surface)
    
    def _render_header(self, surface: pygame.Surface):
        """
        Render header section with Pokémon name and National Dex number.
        
        Args:
            surface: pygame.Surface to draw on
            
        AC #3: Name in title case (left), dex number #025 format (right)
        Uses Orbitron Bold 24px, white color per UX spec
        """
        if not self.pokemon_data or not self.header_font:
            return
        
        # Pokémon name (title case, left-aligned in header)
        name = self.pokemon_data['name'].capitalize()
        name_text = self.header_font.render(name, True, Colors.HOLOGRAM_WHITE)
        name_rect = name_text.get_rect(left=20, top=16)
        surface.blit(name_text, name_rect)
        
        # National Dex number (right-aligned in header, #025 format)
        dex_number = f"#{self.pokemon_data['id']:03d}"
        dex_text = self.header_font.render(dex_number, True, Colors.HOLOGRAM_WHITE)
        dex_rect = dex_text.get_rect(right=surface.get_width() - 20, top=16)
        surface.blit(dex_text, dex_rect)
    
    def _render_sprite(self, surface: pygame.Surface):
        """
        Render large Pokémon sprite in center-left area.
        
        Args:
            surface: pygame.Surface to draw on
            
        AC #2: 128x128 sprite, 50-60% screen real estate, center-left position
        Sprite has electric blue border for holographic effect
        """
        if not self.sprite:
            return
        
        # Calculate center-left position (50-60% width allocation)
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Position sprite in left-center area
        sprite_x = screen_width // 4 - self.sprite.get_width() // 2
        sprite_y = screen_height // 2 - self.sprite.get_height() // 2
        
        # Draw holographic border around sprite (AC #5: electric blue)
        border_rect = pygame.Rect(
            sprite_x - 4,
            sprite_y - 4,
            self.sprite.get_width() + 8,
            self.sprite.get_height() + 8
        )
        pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, border_rect, 2)
        
        # Blit sprite to surface
        surface.blit(self.sprite, (sprite_x, sprite_y))
    
    def _render_placeholder_panels(self, surface: pygame.Surface):
        """
        Render placeholder panels for future features.
        
        Args:
            surface: pygame.Surface to draw on
            
        AC #4: Layout structure with placeholders for:
        - Stats panel (right side) - Story 3.2
        - Type badges (below sprite) - Story 3.3
        - Physical measurements (bottom-left) - Story 3.4
        - Description area (bottom-center) - Story 3.5
        
        AC #5: Holographic blue styling (dark blue panels, electric blue borders)
        """
        screen_width = surface.get_width()
        screen_height = surface.get_height()
        
        # Stats panel placeholder (right side, 40% width)
        stats_panel = pygame.Rect(
            screen_width // 2 + 20,
            60,
            screen_width // 2 - 40,
            120
        )
        pygame.draw.rect(surface, Colors.DARK_BLUE, stats_panel)
        pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, stats_panel, 2)
        
        if self.small_font:
            stats_label = self.small_font.render("Stats (Story 3.2)", True, Colors.ICE_BLUE)
            surface.blit(stats_label, (stats_panel.x + 10, stats_panel.y + 10))
        
        # Type badges placeholder (below sprite, centered)
        type_panel = pygame.Rect(
            20,
            screen_height // 2 + 80,
            screen_width // 2 - 40,
            40
        )
        pygame.draw.rect(surface, Colors.DARK_BLUE, type_panel)
        pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, type_panel, 2)
        
        if self.small_font:
            type_label = self.small_font.render("Type Badges (Story 3.3)", True, Colors.ICE_BLUE)
            surface.blit(type_label, (type_panel.x + 10, type_panel.y + 10))
        
        # Physical measurements placeholder (bottom-left)
        phys_panel = pygame.Rect(
            20,
            screen_height - 80,
            screen_width // 3 - 20,
            60
        )
        pygame.draw.rect(surface, Colors.DARK_BLUE, phys_panel)
        pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, phys_panel, 2)
        
        if self.small_font:
            phys_label = self.small_font.render("Physical Data (3.4)", True, Colors.ICE_BLUE)
            surface.blit(phys_label, (phys_panel.x + 10, phys_panel.y + 10))
        
        # Description placeholder (bottom-center)
        desc_panel = pygame.Rect(
            screen_width // 3 + 20,
            screen_height - 80,
            screen_width - (screen_width // 3) - 40,
            60
        )
        pygame.draw.rect(surface, Colors.DARK_BLUE, desc_panel)
        pygame.draw.rect(surface, Colors.ELECTRIC_BLUE, desc_panel, 2)
        
        if self.small_font:
            desc_label = self.small_font.render("Description (Story 3.5)", True, Colors.ICE_BLUE)
            surface.blit(desc_label, (desc_panel.x + 10, desc_panel.y + 10))


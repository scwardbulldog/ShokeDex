"""
Detail Screen for ShokeDex - Detailed Pokémon view
"""

import pygame
from typing import Optional, Dict, List
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction


class DetailScreen(Screen):
    """
    Detail screen showing comprehensive information about a single Pokémon.
    
    Displays sprite, stats, types, abilities, and other information.
    """
    
    def __init__(self, screen_manager, pokemon_id: int, database=None):
        """
        Initialize DetailScreen.
        
        Args:
            screen_manager: ScreenManager instance
            pokemon_id: ID of the Pokemon to display
            database: Database instance (optional)
        """
        super().__init__(screen_manager)
        self.pokemon_id = pokemon_id
        self.database = database
        
        # Pokemon data
        self.pokemon_data: Optional[Dict] = None
        self.stats: List[Dict] = []
        self.types: List[str] = []
        
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
        self.heading_font = pygame.font.Font(None, 24)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Load Pokemon data
        self._load_pokemon_data()
    
    def _load_pokemon_data(self):
        """Load Pokemon data from database."""
        if self.database:
            try:
                with self.database as db:
                    # Get basic Pokemon info
                    self.pokemon_data = db.get_pokemon_by_id(self.pokemon_id)
                    
                    if self.pokemon_data:
                        # Get stats
                        self.stats = db.get_pokemon_stats(self.pokemon_id)
                        
                        # Get types
                        cursor = db.execute("""
                            SELECT t.name
                            FROM pokemon_types pt
                            JOIN types t ON pt.type_id = t.id
                            WHERE pt.pokemon_id = ?
                            ORDER BY pt.slot
                        """, (self.pokemon_id,))
                        self.types = [row[0] for row in cursor.fetchall()]
            except Exception as e:
                print(f"Error loading Pokemon data: {e}")
                self.pokemon_data = None
        
        # Create demo data if no database
        if not self.pokemon_data:
            self.pokemon_data = {
                'id': self.pokemon_id,
                'name': f'pokemon_{self.pokemon_id}',
                'height': 10,
                'weight': 100,
                'generation': 1,
            }
            self.stats = [
                {'name': 'HP', 'base_stat': 45},
                {'name': 'Attack', 'base_stat': 49},
                {'name': 'Defense', 'base_stat': 49},
                {'name': 'Special Attack', 'base_stat': 65},
                {'name': 'Special Defense', 'base_stat': 65},
                {'name': 'Speed', 'base_stat': 45},
            ]
            self.types = ['normal']
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        if action == InputAction.BACK:
            self.screen_manager.pop()
        elif action == InputAction.LEFT:
            self._navigate_pokemon(-1)
        elif action == InputAction.RIGHT:
            self._navigate_pokemon(1)
    
    def _navigate_pokemon(self, delta: int):
        """Navigate to adjacent Pokemon."""
        new_id = self.pokemon_id + delta
        
        # Check if Pokemon exists (simple bounds check for now)
        if new_id >= 1 and new_id <= 386:
            self.pokemon_id = new_id
            self._load_pokemon_data()
    
    def update(self, delta_time: float):
        """Update screen state."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        if not self.pokemon_data:
            surface.fill(Colors.BACKGROUND)
            error_text = self.text_font.render(
                "Pokemon not found",
                True,
                Colors.ERROR
            )
            error_rect = error_text.get_rect(center=(240, 160))
            surface.blit(error_text, error_rect)
            return
        
        # Clear background
        surface.fill(Colors.BACKGROUND)
        
        # Draw Pokemon name and ID
        name = self.pokemon_data['name'].capitalize()
        name_text = self.title_font.render(name, True, Colors.TEXT_PRIMARY)
        name_rect = name_text.get_rect(centerx=240, top=10)
        surface.blit(name_text, name_rect)
        
        id_text = self.text_font.render(
            f"#{self.pokemon_data['id']:03d}",
            True,
            Colors.TEXT_SECONDARY
        )
        id_rect = id_text.get_rect(centerx=240, top=45)
        surface.blit(id_text, id_rect)
        
        # Draw sprite placeholder
        sprite_rect = pygame.Rect(180, 75, 120, 120)
        pygame.draw.rect(surface, Colors.BORDER, sprite_rect, 2)
        
        # Draw "Sprite" text in center
        sprite_text = self.small_font.render("Sprite", True, Colors.TEXT_SECONDARY)
        sprite_text_rect = sprite_text.get_rect(center=sprite_rect.center)
        surface.blit(sprite_text, sprite_text_rect)
        
        # Draw types
        if self.types:
            types_y = 205
            types_label = self.heading_font.render("Type:", True, Colors.TEXT_PRIMARY)
            surface.blit(types_label, (20, types_y))
            
            types_x = 80
            for type_name in self.types:
                type_color = Colors.TYPE_COLORS.get(type_name.lower(), Colors.GRAY)
                type_rect = pygame.Rect(types_x, types_y, 70, 25)
                pygame.draw.rect(surface, type_color, type_rect)
                pygame.draw.rect(surface, Colors.BLACK, type_rect, 1)
                
                type_text = self.small_font.render(
                    type_name.capitalize(),
                    True,
                    Colors.BLACK
                )
                type_text_rect = type_text.get_rect(center=type_rect.center)
                surface.blit(type_text, type_text_rect)
                
                types_x += 75
        
        # Draw stats
        if self.stats:
            stats_y = 240
            stats_label = self.heading_font.render("Stats:", True, Colors.TEXT_PRIMARY)
            surface.blit(stats_label, (20, stats_y))
            
            stats_y += 25
            for stat in self.stats:
                # Stat name
                stat_name = self.small_font.render(
                    f"{stat['name']}:",
                    True,
                    Colors.TEXT_SECONDARY
                )
                surface.blit(stat_name, (30, stats_y))
                
                # Stat value
                stat_value = self.text_font.render(
                    str(stat['base_stat']),
                    True,
                    Colors.TEXT_PRIMARY
                )
                surface.blit(stat_value, (150, stats_y - 2))
                
                # Stat bar
                bar_width = int(stat['base_stat'] * 1.5)  # Scale to fit
                bar_rect = pygame.Rect(200, stats_y + 2, bar_width, 12)
                pygame.draw.rect(surface, Colors.LIGHT_GREEN, bar_rect)
                pygame.draw.rect(surface, Colors.BORDER, bar_rect, 1)
                
                stats_y += 20
        
        # Draw physical stats
        phys_y = 245
        phys_x = 320
        
        height_m = self.pokemon_data.get('height', 0) / 10.0
        weight_kg = self.pokemon_data.get('weight', 0) / 10.0
        
        height_text = self.small_font.render(
            f"Height: {height_m:.1f}m",
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(height_text, (phys_x, phys_y))
        
        weight_text = self.small_font.render(
            f"Weight: {weight_kg:.1f}kg",
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(weight_text, (phys_x, phys_y + 18))
        
        # Draw help text
        help_text = self.small_font.render(
            "←/→: Navigate | BACK: Return",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(right=470, bottom=315)
        surface.blit(help_text, help_rect)

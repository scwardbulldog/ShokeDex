"""
Home Screen for ShokeDex - Grid view of Pokémon
"""

import pygame
from typing import List, Optional, Tuple
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction


class HomeScreen(Screen):
    """
    Home screen showing a grid of Pokémon thumbnails.
    
    Displays Pokémon in a grid layout with sprite thumbnails and names.
    """
    
    def __init__(self, screen_manager, database=None):
        """
        Initialize HomeScreen.
        
        Args:
            screen_manager: ScreenManager instance
            database: Database instance (optional, for loading Pokemon data)
        """
        super().__init__(screen_manager)
        self.database = database
        
        # Grid configuration
        self.grid_cols = 4
        self.grid_rows = 3
        self.items_per_page = self.grid_cols * self.grid_rows
        
        # Selection state
        self.selected_index = 0
        self.page = 0
        
        # Pokemon data
        self.pokemon_list: List[dict] = []
        self.total_pokemon = 0
        
        # Fonts (will be initialized in on_enter)
        self.title_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        
        # Layout dimensions (for 480x320 display)
        self.cell_width = 120
        self.cell_height = 90
        self.grid_start_y = 40
        
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        
        # Load Pokemon data
        self._load_pokemon()
    
    def _load_pokemon(self):
        """Load Pokemon data from database."""
        if self.database:
            try:
                with self.database as db:
                    # Get all Pokemon, ordered by ID
                    cursor = db.execute(
                        "SELECT id, name FROM pokemon ORDER BY id"
                    )
                    self.pokemon_list = [
                        {'id': row[0], 'name': row[1]}
                        for row in cursor.fetchall()
                    ]
                    self.total_pokemon = len(self.pokemon_list)
            except Exception as e:
                print(f"Error loading Pokemon: {e}")
                self.pokemon_list = []
                self.total_pokemon = 0
        else:
            # Demo data if no database
            self.pokemon_list = [
                {'id': i, 'name': f"Pokemon {i}"}
                for i in range(1, 151)
            ]
            self.total_pokemon = len(self.pokemon_list)
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        if action == InputAction.UP:
            self._move_selection(-self.grid_cols)
        elif action == InputAction.DOWN:
            self._move_selection(self.grid_cols)
        elif action == InputAction.LEFT:
            self._move_selection(-1)
        elif action == InputAction.RIGHT:
            self._move_selection(1)
        elif action == InputAction.SELECT:
            self._select_pokemon()
        elif action == InputAction.START:
            self._open_settings()
    
    def _move_selection(self, delta: int):
        """Move selection by delta positions."""
        new_index = self.selected_index + delta
        
        # Clamp to valid range
        max_index = min(self.total_pokemon - 1, (self.page + 1) * self.items_per_page - 1)
        min_index = self.page * self.items_per_page
        
        if new_index < min_index:
            # Move to previous page
            if self.page > 0:
                self.page -= 1
                self.selected_index = new_index + self.items_per_page
        elif new_index > max_index:
            # Move to next page
            if (self.page + 1) * self.items_per_page < self.total_pokemon:
                self.page += 1
                self.selected_index = new_index - self.items_per_page
        else:
            self.selected_index = new_index
        
        # Final clamp
        self.selected_index = max(0, min(self.selected_index, self.total_pokemon - 1))
    
    def _select_pokemon(self):
        """Handle Pokemon selection."""
        if 0 <= self.selected_index < self.total_pokemon:
            pokemon = self.pokemon_list[self.selected_index]
            
            # Import here to avoid circular import
            from .detail_screen import DetailScreen
            
            detail_screen = DetailScreen(
                self.screen_manager,
                pokemon_id=pokemon['id'],
                database=self.database
            )
            self.screen_manager.push(detail_screen)
    
    def _open_settings(self):
        """Open settings screen."""
        from .settings_screen import SettingsScreen
        
        settings_screen = SettingsScreen(self.screen_manager)
        self.screen_manager.push(settings_screen)
    
    def update(self, delta_time: float):
        """Update screen state."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        # Clear background
        surface.fill(Colors.BACKGROUND)
        
        # Draw title
        title_text = self.title_font.render("ShokeDex", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(240, 20))
        surface.blit(title_text, title_rect)
        
        # Draw grid
        self._render_grid(surface)
        
        # Draw page indicator
        total_pages = (self.total_pokemon + self.items_per_page - 1) // self.items_per_page
        page_text = self.small_font.render(
            f"Page {self.page + 1}/{total_pages}",
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(page_text, (10, 300))
        
        # Draw help text
        help_text = self.small_font.render(
            "SELECT: View | START: Settings",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(right=470, bottom=315)
        surface.blit(help_text, help_rect)
    
    def _render_grid(self, surface: pygame.Surface):
        """Render the Pokemon grid."""
        start_idx = self.page * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, self.total_pokemon)
        
        for i in range(start_idx, end_idx):
            relative_idx = i - start_idx
            row = relative_idx // self.grid_cols
            col = relative_idx % self.grid_cols
            
            # Calculate cell position
            x = col * self.cell_width
            y = self.grid_start_y + row * self.cell_height
            
            # Get Pokemon data
            pokemon = self.pokemon_list[i]
            
            # Determine if this cell is selected
            is_selected = (i == self.selected_index)
            
            # Draw cell
            self._render_cell(surface, pokemon, x, y, is_selected)
    
    def _render_cell(
        self,
        surface: pygame.Surface,
        pokemon: dict,
        x: int,
        y: int,
        is_selected: bool
    ):
        """Render a single grid cell."""
        # Draw selection background
        if is_selected:
            rect = pygame.Rect(x + 2, y + 2, self.cell_width - 4, self.cell_height - 4)
            pygame.draw.rect(surface, Colors.SELECTION_BG, rect)
            pygame.draw.rect(surface, Colors.BORDER, rect, 2)
        
        # Draw sprite placeholder (centered in cell)
        sprite_size = 48
        sprite_x = x + (self.cell_width - sprite_size) // 2
        sprite_y = y + 10
        sprite_rect = pygame.Rect(sprite_x, sprite_y, sprite_size, sprite_size)
        
        # Draw sprite border
        color = Colors.SELECTION_TEXT if is_selected else Colors.BORDER
        pygame.draw.rect(surface, color, sprite_rect, 1)
        
        # Draw Pokemon ID (in sprite area for now)
        id_text = self.small_font.render(
            f"#{pokemon['id']:03d}",
            True,
            color
        )
        id_rect = id_text.get_rect(center=sprite_rect.center)
        surface.blit(id_text, id_rect)
        
        # Draw Pokemon name
        name_color = Colors.SELECTION_TEXT if is_selected else Colors.TEXT_PRIMARY
        name_text = self.small_font.render(
            pokemon['name'].capitalize(),
            True,
            name_color
        )
        name_rect = name_text.get_rect(centerx=x + self.cell_width // 2, top=y + 65)
        surface.blit(name_text, name_rect)

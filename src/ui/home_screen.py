"""
Home Screen for ShokeDex - Grid view of Pokémon
"""

import pygame
import os
from typing import List, Optional, Tuple
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction
from .sprite_loader import load_thumb


# Generation constants
GENERATION_NAMES = {
    1: "KANTO",
    2: "JOHTO",
    3: "HOENN"
}

GENERATION_RANGES = {
    1: (1, 151),    # Kanto: Bulbasaur to Mew
    2: (152, 251),  # Johto: Chikorita to Celebi
    3: (252, 386)   # Hoenn: Treecko to Deoxys
}

GENERATION_TOTALS = {
    1: 151,
    2: 100,
    3: 135
}


class GenerationBadge:
    """
    Visual component displaying current generation with logo and position counter.
    
    Shows region name (KANTO/JOHTO/HOENN) with optional logo icon and
    position counter in format #XXX/YYY.
    """
    
    def __init__(self, generation: int, pokemon_id: int):
        """
        Initialize generation badge.
        
        Args:
            generation: 1 (Kanto), 2 (Johto), or 3 (Hoenn)
            pokemon_id: Current Pokemon National Dex number
        """
        self.generation = generation
        self.pokemon_id = pokemon_id
        self.logo_surface: Optional[pygame.Surface] = None
        
        # Try to load generation logo
        self._load_logo()
        
        # Initialize fonts (will be set by parent screen)
        self.name_font: Optional[pygame.font.Font] = None
        self.counter_font: Optional[pygame.font.Font] = None
    
    def _load_logo(self):
        """Load generation logo asset with fallback to text-only."""
        logo_paths = {
            1: "assets/icons/badge_kanto.png",
            2: "assets/icons/badge_johto.png",
            3: "assets/icons/badge_hoenn.png"
        }
        
        if self.generation not in logo_paths:
            return
        
        logo_path = logo_paths[self.generation]
        
        try:
            if os.path.exists(logo_path):
                self.logo_surface = pygame.image.load(logo_path).convert_alpha()
                # Scale to 40x40px
                self.logo_surface = pygame.transform.smoothscale(self.logo_surface, (40, 40))
        except Exception as e:
            print(f"Warning: Generation badge asset not found: {logo_path} - {e}")
            self.logo_surface = None
    
    def update(self, pokemon_id: int):
        """Update position counter when Pokemon changes."""
        self.pokemon_id = pokemon_id
    
    def set_generation(self, generation: int, pokemon_id: int):
        """Update generation and reload logo if needed."""
        if generation != self.generation:
            self.generation = generation
            self.pokemon_id = pokemon_id
            self._load_logo()
    
    def render(self, surface: pygame.Surface, x: int, y: int):
        """
        Render badge to surface at specified position.
        
        Args:
            surface: pygame Surface to render on
            x: X coordinate (top-left corner)
            y: Y coordinate (top-left corner)
        """
        # Badge dimensions
        badge_width = 220
        badge_height = 50
        
        # Create badge background with transparency
        badge_surface = pygame.Surface((badge_width, badge_height), pygame.SRCALPHA)
        
        # Draw background (dark blue with transparency)
        bg_color = (*Colors.DARK_BLUE, 230)  # rgba(26, 47, 74, 0.9)
        pygame.draw.rect(badge_surface, bg_color, (0, 0, badge_width, badge_height))
        
        # Draw 2px electric blue border
        pygame.draw.rect(badge_surface, Colors.ELECTRIC_BLUE, (0, 0, badge_width, badge_height), 2)
        
        # Draw corner accent lines (45° cuts)
        accent_length = 10
        # Top-left corner
        pygame.draw.line(badge_surface, Colors.ELECTRIC_BLUE, (2, accent_length), (accent_length, 2), 2)
        # Top-right corner
        pygame.draw.line(badge_surface, Colors.ELECTRIC_BLUE, 
                        (badge_width - accent_length, 2), (badge_width - 2, accent_length), 2)
        # Bottom-left corner
        pygame.draw.line(badge_surface, Colors.ELECTRIC_BLUE,
                        (2, badge_height - accent_length), (accent_length, badge_height - 2), 2)
        # Bottom-right corner
        pygame.draw.line(badge_surface, Colors.ELECTRIC_BLUE,
                        (badge_width - accent_length, badge_height - 2), 
                        (badge_width - 2, badge_height - accent_length), 2)
        
        # Calculate content positioning
        content_x = 10
        
        # Draw logo if available
        if self.logo_surface:
            badge_surface.blit(self.logo_surface, (content_x, 5))
            content_x += 45  # Logo width + spacing
        
        # Draw generation name
        if self.name_font:
            name_text = self.name_font.render(
                GENERATION_NAMES[self.generation],
                True,
                Colors.HOLOGRAM_WHITE
            )
            badge_surface.blit(name_text, (content_x, 8))
        
        # Draw position counter
        if self.counter_font:
            total = GENERATION_TOTALS[self.generation]
            counter_text = self.counter_font.render(
                f"#{self.pokemon_id:03d}/{total:03d}",
                True,
                Colors.ICE_BLUE
            )
            badge_surface.blit(counter_text, (content_x, 28))
        
        # Blit badge to main surface
        surface.blit(badge_surface, (x, y))


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
        self.filtered_list: List[dict] = []
        self.total_pokemon = 0
        
        # Search state
        self.search_active = False
        self.search_query = ""
        
        # Favorites (stub - will be loaded from settings/database later)
        self.favorites: set = set()
        self.recent_views: List[int] = []  # Pokemon IDs
        
        # View mode (all, favorites, recent)
        self.view_mode = "all"  # Can be "all", "favorites", "recent"
        
        # Generation navigation
        self.current_generation = 1  # Default to Kanto
        self.generation_badge: Optional[GenerationBadge] = None
        
        # Fonts (will be initialized in on_enter)
        self.title_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        self.badge_name_font: Optional[pygame.font.Font] = None
        self.badge_counter_font: Optional[pygame.font.Font] = None
        
        # Layout dimensions (for 480x320 display)
        self.cell_width = 120
        self.cell_height = 90
        self.grid_start_y = 60  # Increased to accommodate search bar
        
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
        self.badge_name_font = pygame.font.Font(None, 24)  # For generation name
        self.badge_counter_font = pygame.font.Font(None, 18)  # For position counter
        
        # Initialize generation badge
        first_pokemon_id = 1  # Default to Bulbasaur
        if self.pokemon_list:
            first_pokemon_id = self.pokemon_list[0]['id']
        
        self.generation_badge = GenerationBadge(self.current_generation, first_pokemon_id)
        self.generation_badge.name_font = self.badge_name_font
        self.generation_badge.counter_font = self.badge_counter_font
        
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
        
        # Initialize filtered list
        self._apply_filters()
    
    def _apply_filters(self):
        """Apply current search and view filters to Pokemon list."""
        # Start with full list
        result = self.pokemon_list
        
        # Apply view mode filter
        if self.view_mode == "favorites" and self.favorites:
            result = [p for p in result if p['id'] in self.favorites]
        elif self.view_mode == "recent" and self.recent_views:
            # Show recent views in order
            result = [p for p in result if p['id'] in self.recent_views]
            result.sort(key=lambda p: self.recent_views.index(p['id']))
        
        # Apply search filter
        if self.search_query:
            query_lower = self.search_query.lower()
            result = [
                p for p in result
                if query_lower in p['name'].lower() or
                   query_lower in str(p['id'])
            ]
        
        self.filtered_list = result
        self.total_pokemon = len(result)
        
        # Reset selection if out of bounds
        if self.selected_index >= self.total_pokemon and self.total_pokemon > 0:
            self.selected_index = 0
            self.page = 0
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        # If search is active, handle search-specific input
        if self.search_active:
            if action == InputAction.BACK:
                # Clear search or deactivate
                if self.search_query:
                    self.search_query = ""
                    self._apply_filters()
                else:
                    self.search_active = False
                return
            # For actual typing, we'd need text input events
            # This is handled in the render loop for now
            return
        
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
        
        # Update generation badge with current Pokemon ID
        if 0 <= self.selected_index < self.total_pokemon:
            current_pokemon = self.filtered_list[self.selected_index]
            if self.generation_badge:
                self.generation_badge.update(current_pokemon['id'])
    
    def _select_pokemon(self):
        """Handle Pokemon selection."""
        if 0 <= self.selected_index < self.total_pokemon:
            pokemon = self.filtered_list[self.selected_index]
            
            # Add to recent views
            if pokemon['id'] not in self.recent_views:
                self.recent_views.insert(0, pokemon['id'])
                # Keep only last 12 recent views
                self.recent_views = self.recent_views[:12]
            elif pokemon['id'] in self.recent_views:
                # Move to front if already in list
                self.recent_views.remove(pokemon['id'])
                self.recent_views.insert(0, pokemon['id'])
            
            # Lazy import to avoid circular dependency
            # DetailScreen -> ScreenManager -> HomeScreen cycle
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
        title_rect = title_text.get_rect(center=(240, 15))
        surface.blit(title_text, title_rect)
        
        # Draw generation badge (top-left position)
        if self.generation_badge:
            self.generation_badge.render(surface, 10, 10)
        
        # Draw search/filter bar
        self._render_search_bar(surface)
        
        # Draw grid
        self._render_grid(surface)
        
        # Draw page indicator and view mode
        total_pages = max(1, (self.total_pokemon + self.items_per_page - 1) // self.items_per_page)
        page_text = self.small_font.render(
            f"Page {self.page + 1}/{total_pages}",
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(page_text, (10, 300))
        
        # Draw view mode indicator
        view_mode_text = f"View: {self.view_mode.capitalize()}"
        if self.search_query:
            view_mode_text += f" (Search: {self.search_query})"
        mode_render = self.small_font.render(
            view_mode_text,
            True,
            Colors.TEXT_SECONDARY
        )
        surface.blit(mode_render, (140, 300))
        
        # Draw help text
        help_text = self.small_font.render(
            "SELECT: View | START: Settings",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(right=470, bottom=315)
        surface.blit(help_text, help_rect)
    
    def _render_search_bar(self, surface: pygame.Surface):
        """Render search/filter bar."""
        bar_y = 35
        bar_height = 18
        
        # Draw search indicator
        search_icon = "🔍" if self.search_query or self.search_active else "⊡"
        search_text = self.small_font.render(
            f"{search_icon} {self.search_query}",
            True,
            Colors.TEXT_PRIMARY if self.search_active else Colors.TEXT_SECONDARY
        )
        surface.blit(search_text, (10, bar_y))
        
        # Draw view mode buttons (favorites, recent, all)
        button_x = 280
        button_width = 60
        for mode in ["all", "recent", "fav"]:
            is_active = (self.view_mode == mode or 
                        (mode == "fav" and self.view_mode == "favorites"))
            
            btn_rect = pygame.Rect(button_x, bar_y - 2, button_width, bar_height)
            
            # Draw button background
            if is_active:
                pygame.draw.rect(surface, Colors.SELECTION_BG, btn_rect)
            pygame.draw.rect(surface, Colors.BORDER, btn_rect, 1)
            
            # Draw button text
            btn_color = Colors.BLACK if is_active else Colors.TEXT_SECONDARY
            mode_name = "Fav" if mode == "fav" else mode.capitalize()
            btn_text = self.small_font.render(mode_name, True, btn_color)
            btn_text_rect = btn_text.get_rect(center=btn_rect.center)
            surface.blit(btn_text, btn_text_rect)
            
            button_x += button_width + 5
    
    def _render_grid(self, surface: pygame.Surface):
        """Render the Pokemon grid."""
        if self.total_pokemon == 0:
            # Show "no results" message
            no_results = self.text_font.render(
                "No Pokémon found",
                True,
                Colors.TEXT_SECONDARY
            )
            no_results_rect = no_results.get_rect(center=(240, 160))
            surface.blit(no_results, no_results_rect)
            return
        
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
            pokemon = self.filtered_list[i]
            
            # Check if favorited or recently viewed
            is_favorite = pokemon['id'] in self.favorites
            is_recent = pokemon['id'] in self.recent_views
            
            # Determine if this cell is selected
            is_selected = (i == self.selected_index)
            
            # Draw cell
            self._render_cell(surface, pokemon, x, y, is_selected, is_favorite, is_recent)
    
    def _render_cell(
        self,
        surface: pygame.Surface,
        pokemon: dict,
        x: int,
        y: int,
        is_selected: bool,
        is_favorite: bool = False,
        is_recent: bool = False
    ):
        """Render a single grid cell."""
        # Draw selection background
        if is_selected:
            rect = pygame.Rect(x + 2, y + 2, self.cell_width - 4, self.cell_height - 4)
            pygame.draw.rect(surface, Colors.SELECTION_BG, rect)
            pygame.draw.rect(surface, Colors.BORDER, rect, 2)
        
        # Draw favorite/recent indicator
        if is_favorite:
            fav_text = self.small_font.render("★", True, Colors.YELLOW)
            surface.blit(fav_text, (x + 5, y + 3))
        elif is_recent:
            recent_text = self.small_font.render("•", True, Colors.LIGHT_BLUE)
            surface.blit(recent_text, (x + 5, y + 3))
        
        # Draw sprite placeholder (centered in cell)
        sprite_size = 48
        sprite_x = x + (self.cell_width - sprite_size) // 2
        sprite_y = y + 10
        sprite_rect = pygame.Rect(sprite_x, sprite_y, sprite_size, sprite_size)
        
        # Draw sprite border
        color = Colors.SELECTION_TEXT if is_selected else Colors.BORDER
        pygame.draw.rect(surface, color, sprite_rect, 1)

        # Attempt to load and draw thumbnail
        try:
            thumb_surf = load_thumb(pokemon['id'])
            if thumb_surf:
                try:
                    if thumb_surf.get_size() != (sprite_size, sprite_size):
                        thumb_surf = pygame.transform.smoothscale(thumb_surf, (sprite_size, sprite_size))
                except Exception:
                    pass

                surface.blit(thumb_surf, (sprite_x, sprite_y))
            else:
                # Draw Pokemon ID (in sprite area as fallback)
                id_text = self.small_font.render(
                    f"#{pokemon['id']:03d}",
                    True,
                    color
                )
                id_rect = id_text.get_rect(center=sprite_rect.center)
                surface.blit(id_text, id_rect)
        except Exception:
            # On any error (pygame missing, load fail), draw ID placeholder
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

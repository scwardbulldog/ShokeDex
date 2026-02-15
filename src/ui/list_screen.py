"""
List Screen for ShokeDex - List view of Pokémon
"""

import pygame
from typing import List, Optional
from .screen import Screen
from .colors import Colors
from ..input_manager import InputAction
from .sprite_loader import load_thumb


class ListScreen(Screen):
    """
    List screen showing Pokémon in a scrollable list.
    
    Alternative view to the grid, shows more information per entry.
    """
    
    def __init__(self, screen_manager, database=None):
        """
        Initialize ListScreen.
        
        Args:
            screen_manager: ScreenManager instance
            database: Database instance (optional)
        """
        super().__init__(screen_manager)
        self.database = database
        
        # List configuration
        self.items_per_page = 8
        self.item_height = 35
        
        # Selection state
        self.selected_index = 0
        self.scroll_offset = 0
        
        # Pokemon data
        self.pokemon_list: List[dict] = []
        self.total_pokemon = 0
        
        # Fonts
        self.title_font: Optional[pygame.font.Font] = None
        self.text_font: Optional[pygame.font.Font] = None
        self.small_font: Optional[pygame.font.Font] = None
        
        # Layout
        self.list_start_y = 40
    
    def on_enter(self):
        """Called when screen becomes active."""
        super().on_enter()
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 32)
        self.text_font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
        
        # Load Pokemon data
        self._load_pokemon()
    
    def _load_pokemon(self):
        """Load Pokemon data from database."""
        if self.database:
            try:
                with self.database as db:
                    cursor = db.execute("""
                        SELECT p.id, p.name, GROUP_CONCAT(t.name) as types
                        FROM pokemon p
                        LEFT JOIN pokemon_types pt ON p.id = pt.pokemon_id
                        LEFT JOIN types t ON pt.type_id = t.id
                        GROUP BY p.id
                        ORDER BY p.id
                    """)
                    self.pokemon_list = [
                        {
                            'id': row[0],
                            'name': row[1],
                            'types': row[2].split(',') if row[2] else []
                        }
                        for row in cursor.fetchall()
                    ]
                    self.total_pokemon = len(self.pokemon_list)
            except Exception as e:
                print(f"Error loading Pokemon: {e}")
                self.pokemon_list = []
        else:
            # Demo data
            self.pokemon_list = [
                {'id': i, 'name': f"Pokemon {i}", 'types': ['normal']}
                for i in range(1, 151)
            ]
            self.total_pokemon = len(self.pokemon_list)
    
    def handle_input(self, action: InputAction):
        """Handle input actions."""
        if action == InputAction.UP:
            self._move_selection(-1)
        elif action == InputAction.DOWN:
            self._move_selection(1)
        elif action == InputAction.SELECT:
            self._select_pokemon()
        elif action == InputAction.BACK:
            self.screen_manager.pop()
    
    def _move_selection(self, delta: int):
        """Move selection by delta positions."""
        self.selected_index = max(0, min(
            self.selected_index + delta,
            self.total_pokemon - 1
        ))
        
        # Update scroll offset to keep selection visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.items_per_page:
            self.scroll_offset = self.selected_index - self.items_per_page + 1
    
    def _select_pokemon(self):
        """Handle Pokemon selection."""
        if 0 <= self.selected_index < self.total_pokemon:
            pokemon = self.pokemon_list[self.selected_index]
            
            from .detail_screen import DetailScreen
            
            detail_screen = DetailScreen(
                self.screen_manager,
                pokemon_id=pokemon['id'],
                database=self.database
            )
            self.screen_manager.push(detail_screen)
    
    def update(self, delta_time: float):
        """Update screen state."""
        pass
    
    def render(self, surface: pygame.Surface):
        """Render the screen."""
        # Clear background
        surface.fill(Colors.BACKGROUND)
        
        # Draw title
        title_text = self.title_font.render("Pokémon List", True, Colors.TEXT_PRIMARY)
        title_rect = title_text.get_rect(center=(240, 20))
        surface.blit(title_text, title_rect)
        
        # Draw list
        self._render_list(surface)
        
        # Draw scrollbar indicator
        if self.total_pokemon > self.items_per_page:
            self._render_scrollbar(surface)
        
        # Draw help text
        help_text = self.small_font.render(
            "SELECT: View | BACK: Return",
            True,
            Colors.TEXT_SECONDARY
        )
        help_rect = help_text.get_rect(right=470, bottom=315)
        surface.blit(help_text, help_rect)
    
    def _render_list(self, surface: pygame.Surface):
        """Render the Pokemon list."""
        end_idx = min(
            self.scroll_offset + self.items_per_page,
            self.total_pokemon
        )
        
        for i in range(self.scroll_offset, end_idx):
            relative_idx = i - self.scroll_offset
            y = self.list_start_y + relative_idx * self.item_height
            
            pokemon = self.pokemon_list[i]
            is_selected = (i == self.selected_index)
            
            self._render_list_item(surface, pokemon, y, is_selected)
    
    def _render_list_item(
        self,
        surface: pygame.Surface,
        pokemon: dict,
        y: int,
        is_selected: bool
    ):
        """Render a single list item."""
        # Draw selection background
        if is_selected:
            rect = pygame.Rect(10, y, 460, self.item_height - 2)
            pygame.draw.rect(surface, Colors.SELECTION_BG, rect)
            pygame.draw.rect(surface, Colors.BORDER, rect, 2)
        
        text_color = Colors.SELECTION_TEXT if is_selected else Colors.TEXT_PRIMARY
        
        # Draw Pokemon ID
        id_text = self.text_font.render(
            f"#{pokemon['id']:03d}",
            True,
            text_color
        )
        surface.blit(id_text, (20, y + 8))

        # Draw thumbnail if available
        try:
            thumb_surf = load_thumb(pokemon['id'])
            if thumb_surf:
                # Scale to thumbnail size (32x32) if necessary
                try:
                    if thumb_surf.get_size() != (32, 32):
                        thumb_surf = pygame.transform.smoothscale(thumb_surf, (32, 32))
                except Exception:
                    pass

                surface.blit(thumb_surf, (44, y + 2))
        except Exception:
            # Fail silently if pygame isn't available or loading fails
            pass
        
        # Draw Pokemon name
        name_text = self.text_font.render(
            pokemon['name'].capitalize(),
            True,
            text_color
        )
        surface.blit(name_text, (80, y + 8))
        
        # Draw types if available
        if 'types' in pokemon and pokemon['types']:
            types_text = ' / '.join([t.capitalize() for t in pokemon['types']])
            types_render = self.small_font.render(
                types_text,
                True,
                text_color
            )
            types_rect = types_render.get_rect(right=460, centery=y + self.item_height // 2)
            surface.blit(types_render, types_rect)
    
    def _render_scrollbar(self, surface: pygame.Surface):
        """Render scrollbar indicator."""
        scrollbar_x = 475
        scrollbar_y = self.list_start_y
        scrollbar_height = self.items_per_page * self.item_height
        
        # Draw scrollbar track
        pygame.draw.rect(
            surface,
            Colors.GRAY,
            (scrollbar_x, scrollbar_y, 3, scrollbar_height)
        )
        
        # Calculate thumb position and size
        thumb_height = max(20, int(
            scrollbar_height * self.items_per_page / self.total_pokemon
        ))
        thumb_y = scrollbar_y + int(
            scrollbar_height * self.scroll_offset / self.total_pokemon
        )
        
        # Draw scrollbar thumb
        pygame.draw.rect(
            surface,
            Colors.LIGHT_GREEN,
            (scrollbar_x, thumb_y, 3, thumb_height)
        )
        
        # Return empty list = full screen update
        return []